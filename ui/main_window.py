import queue
from typing import Optional

import customtkinter as ctk

from config.settings import CHART_SETTINGS, SENSOR_SETTINGS
from core.interfaces import DataQueueProvider
from core.algorithms import (
    Voter,
    VotingStrategy,
    AverageStrategy,
    MedianStrategy,
    MOutOfNStrategy,
    MajorityStrategy,
    AverageAdaptiveStrategy,
)
from ui.chart_widget import ChartWidget
from ui.components.settings_panel import SettingsPanel
from ui.components.controls import ControlPanel, HomeControls
from utils.data_parser import DataParser


class MainWindow(ctk.CTk):
    
    def __init__(
        self,
        data_provider: DataQueueProvider,
        title: str = CHART_SETTINGS.WINDOW_TITLE,
        width: int = CHART_SETTINGS.WINDOW_WIDTH,
        height: int = CHART_SETTINGS.WINDOW_HEIGHT,
    ):
        super().__init__()
        
        self._data_provider = data_provider
        self._data_queue = data_provider.get_data_queue()
        
        self.geometry(f"{width}x{height}")
        self.title(title)
        
        self._is_chart_paused = False
        self._settings_visible = False
        self._after_id: Optional[str] = None
        self._num_sensors = SENSOR_SETTINGS.DEFAULT_NUM_SENSORS
        self._reading_frequency = SENSOR_SETTINGS.DEFAULT_READING_FREQUENCY
        self._smoothing_factor = CHART_SETTINGS.DEFAULT_SMOOTHING_FACTOR
        
        self._all_strategies: dict[str, VotingStrategy] = {
            "Average": AverageStrategy(),
            "Median": MedianStrategy(),
            "Advanced m out of n": MOutOfNStrategy(),
            "Majority": MajorityStrategy(),
            "Average Adaptive": AverageAdaptiveStrategy(),
        }
        self._active_strategy_names: set[str] = set()
        
        self._voter = Voter()
        
        self._home_frame: Optional[ctk.CTkFrame] = None
        self._sensors_frame: Optional[ctk.CTkFrame] = None
        self._control_panel: Optional[ControlPanel] = None
        self._settings_panel: Optional[SettingsPanel] = None
        self._chart_widget: Optional[ChartWidget] = None
        self._home_controls: Optional[HomeControls] = None
        
        self._create_frames()
    
    def _create_frames(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._create_home_frame()
        self._create_sensors_frame()
        
        # Start on home frame
        self._show_home()
    
    def _create_home_frame(self) -> None:
        self._home_frame = ctk.CTkFrame(self)
        self._home_frame.grid(row=0, column=0, sticky="nsew")
        
        center_frame = ctk.CTkFrame(self._home_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self._home_controls = HomeControls(
            center_frame,
            on_show_chart=self._handle_show_chart,
            on_close=self._handle_close_application,
        )
        self._home_controls.pack()
    
    def _create_sensors_frame(self) -> None:
        self._sensors_frame = ctk.CTkFrame(self)
        self._sensors_frame.grid(row=0, column=0, sticky="nsew")
        
        self._sensors_frame.grid_rowconfigure(0, weight=0)
        self._sensors_frame.grid_rowconfigure(1, weight=0)
        self._sensors_frame.grid_rowconfigure(2, weight=1)
        self._sensors_frame.grid_columnconfigure(0, weight=1)
        
        self._control_panel = ControlPanel(
            self._sensors_frame,
            on_reset=self._handle_reset,
            on_restart=self._handle_restart,
            on_pause=self._handle_pause,
            on_resume=self._handle_resume,
            on_settings_toggle=self._handle_settings_toggle,
            on_back=self._handle_back_to_home,
        )
        self._control_panel.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 0))
        
        self._settings_panel = SettingsPanel(
            self._sensors_frame,
            on_smoothing_change=self._handle_smoothing_change,
            on_frequency_change=self._handle_frequency_change,
            on_num_sensors_change=self._handle_num_sensors_change,
            on_strategy_toggle=self._handle_strategy_toggle,
            available_strategies=list(self._all_strategies.values()),
        )
        
        self._chart_widget = ChartWidget(
            self._sensors_frame,
            num_sensors=self._num_sensors,
        )
    
    def _show_home(self) -> None:
        if self._home_frame:
            self._home_frame.tkraise()
    
    def _show_sensors(self) -> None:
        if self._sensors_frame:
            self._sensors_frame.tkraise()
    
    def _handle_show_chart(self) -> None:
        self._show_sensors()
        self._start_chart()
    
    def _handle_close_application(self) -> None:
        self._stop_chart()
        self._data_provider.stop()
        self.destroy()
    
    def _handle_reset(self) -> None:
        self._stop_chart()
        if self._chart_widget:
            self._chart_widget.clear_data()
            self._chart_widget.destroy_chart()
        self._voter.reset()
        self._data_provider.clear_queue() if hasattr(self._data_provider, 'clear_queue') else None
    
    def _handle_restart(self) -> None:
        self._handle_reset()
        self._start_chart()
    
    def _handle_pause(self) -> None:
        self._is_chart_paused = True
        self._data_provider.pause()
        if self._control_panel:
            self._control_panel.set_paused_state(True)
    
    def _handle_resume(self) -> None:
        self._is_chart_paused = False
        self._data_provider.resume()
        if self._control_panel:
            self._control_panel.set_paused_state(False)
    
    def _handle_settings_toggle(self) -> None:
        self._settings_visible = not self._settings_visible
        
        if self._settings_panel:
            if self._settings_visible:
                self._settings_panel.grid(row=1, column=0, sticky="ew", padx=10)
            else:
                self._settings_panel.grid_forget()
        
        if self._control_panel:
            self._control_panel.update_settings_button_text(self._settings_visible)
    
    def _handle_back_to_home(self) -> None:
        self._show_closing_dialog()
    
    def _handle_smoothing_change(self, factor: float) -> None:
        self._smoothing_factor = factor
        if self._chart_widget:
            self._chart_widget.set_smoothing_factor(factor)
    
    def _handle_frequency_change(self, frequency: float) -> None:
        self._reading_frequency = frequency
        self._data_provider.update_reading_frequency(frequency) if hasattr(self._data_provider, 'update_reading_frequency') else None
        if self._chart_widget:
            self._chart_widget.set_reading_frequency(frequency)
    
    def _handle_num_sensors_change(self, num_sensors: int) -> None:
        self._num_sensors = num_sensors
        self._data_provider.update_num_sensors(num_sensors) if hasattr(self._data_provider, 'update_num_sensors') else None
        
        self._handle_restart()
    
    def _handle_strategy_toggle(self, strategy_name: str, is_active: bool) -> None:
        if is_active:
            self._active_strategy_names.add(strategy_name)
        else:
            self._active_strategy_names.discard(strategy_name)
        
        active_strategies = [
            self._all_strategies[name]
            for name in self._active_strategy_names
            if name in self._all_strategies
        ]
        self._voter.set_strategies(active_strategies)
    
    def _start_chart(self) -> None:
        if self._chart_widget is None:
            return
        
        if not self._chart_widget.is_initialized:
            self._chart_widget.set_num_sensors(self._num_sensors)
            self._chart_widget.set_smoothing_factor(self._smoothing_factor)
            self._chart_widget.set_reading_frequency(self._reading_frequency)
            self._chart_widget.initialize()
            self._chart_widget.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        self._data_provider.resume()
        self._is_chart_paused = False
        
        active_strategies = [
            self._all_strategies[name]
            for name in self._active_strategy_names
            if name in self._all_strategies
        ]
        self._voter.set_strategies(active_strategies)
        
        self._schedule_chart_update()
        
        if self._control_panel:
            self._control_panel.set_chart_active(True)
    
    def _stop_chart(self) -> None:
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        
        if self._control_panel:
            self._control_panel.set_chart_active(False)
    
    def _schedule_chart_update(self) -> None:
        self._after_id = self.after(
            int(self._reading_frequency * 1000),
            self._update_chart_from_queue,
        )
    
    def _update_chart_from_queue(self) -> None:
        if self._chart_widget is None:
            return
        
        if not self._is_chart_paused:
            try:
                data_updated = False
                
                while not self._data_queue.empty():
                    data = self._data_queue.get_nowait()
                    
                    if not data or len(data) != self._num_sensors:
                        continue
                    
                    data_updated = True
                    
                    valid_readings = DataParser.filter_valid_readings(data)
                    
                    if valid_readings:
                        voting_results = self._voter.vote(valid_readings)
                    else:
                        voting_results = {}
                    
                    self._chart_widget.update_chart(
                        sensor_data=data,
                        voting_results=voting_results,
                        active_strategies=list(self._active_strategy_names),
                    )
                    
            except queue.Empty:
                pass
        
        self._schedule_chart_update()
    
    def _show_closing_dialog(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.geometry("600x200")
        dialog.title("Save chart before closing?")
        dialog.transient(self)
        dialog.grab_set()
        
        label = ctk.CTkLabel(
            dialog,
            text="Do you want to save the chart before returning to menu?",
        )
        label.pack(side="top", pady=(20, 10))
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        button_frame.grid_columnconfigure(0, weight=1, uniform="group1")
        button_frame.grid_columnconfigure(1, weight=1, uniform="group1")
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkButton(
            button_frame,
            text="Let work in background",
            command=lambda: (self._show_home(), dialog.destroy()),
        ).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="Pause",
            command=lambda: (self._handle_pause(), self._show_home(), dialog.destroy()),
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="Save to File",
            fg_color="green",
            hover_color="darkgreen",
            command=lambda: (self._show_save_dialog(), dialog.destroy()),
        ).grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="Abort",
            fg_color="red",
            hover_color="darkred",
            command=lambda: (self._handle_reset(), self._show_home(), dialog.destroy()),
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        self.wait_window(dialog)
    
    def _show_save_dialog(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.geometry("400x150")
        dialog.title("Choose file type")
        dialog.transient(self)
        dialog.grab_set()
        
        label = ctk.CTkLabel(dialog, text="Choose file type to save chart:")
        label.pack(side="top", pady=(20, 10))
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(
            button_frame,
            text="PNG",
            command=lambda: (self._save_chart_png(), dialog.destroy()),
        ).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="CSV",
            command=lambda: (self._save_chart_csv(), dialog.destroy()),
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        self.wait_window(dialog)
    
    def _save_chart_png(self) -> None:
        if self._chart_widget is None:
            return
        
        file_path = ctk.filedialog.asksaveasfilename(
            title="Save as PNG",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        )
        
        if file_path:
            self._chart_widget.save_as_png(file_path)
    
    def _save_chart_csv(self) -> None:
        if self._chart_widget is None:
            return
        
        file_path = ctk.filedialog.asksaveasfilename(
            title="Save as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        
        if file_path:
            self._chart_widget.export_to_csv(file_path)

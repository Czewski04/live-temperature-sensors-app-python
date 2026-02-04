from typing import Callable, Optional

import customtkinter as ctk

from config.settings import SENSOR_SETTINGS, CHART_SETTINGS
from core.algorithms import VotingStrategy


class SettingsPanel(ctk.CTkFrame):
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        on_smoothing_change: Optional[Callable[[float], None]] = None,
        on_frequency_change: Optional[Callable[[float], None]] = None,
        on_num_sensors_change: Optional[Callable[[int], None]] = None,
        on_strategy_toggle: Optional[Callable[[str, bool], None]] = None,
        available_strategies: Optional[list[VotingStrategy]] = None,
        **kwargs,
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self._on_smoothing_change = on_smoothing_change
        self._on_frequency_change = on_frequency_change
        self._on_num_sensors_change = on_num_sensors_change
        self._on_strategy_toggle = on_strategy_toggle
        self._available_strategies = available_strategies or []
        
        self._smoothing_factor = CHART_SETTINGS.DEFAULT_SMOOTHING_FACTOR
        self._reading_frequency = SENSOR_SETTINGS.DEFAULT_READING_FREQUENCY
        self._num_sensors = SENSOR_SETTINGS.DEFAULT_NUM_SENSORS
        
        self._strategy_states: dict[str, bool] = {
            strategy.name: False for strategy in self._available_strategies
        }
        
        self._smoothing_slider: Optional[ctk.CTkSlider] = None
        self._smoothing_label: Optional[ctk.CTkLabel] = None
        self._frequency_slider: Optional[ctk.CTkSlider] = None
        self._frequency_label: Optional[ctk.CTkLabel] = None
        self._num_sensors_slider: Optional[ctk.CTkSlider] = None
        self._num_sensors_label: Optional[ctk.CTkLabel] = None
        self._strategy_checkboxes: dict[str, ctk.CTkCheckBox] = {}
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        self._create_smoothing_slider()
        self._create_frequency_slider()
        self._create_num_sensors_slider()
        self._create_strategy_checkboxes()
    
    def _create_smoothing_slider(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(side="left", padx=10, pady=0, fill="y")
        
        self._smoothing_label = ctk.CTkLabel(frame, text="")
        self._smoothing_label.pack(side="top", pady=(5, 0))
        
        self._smoothing_slider = ctk.CTkSlider(
            frame,
            from_=int(CHART_SETTINGS.MIN_SMOOTHING_FACTOR * 100),
            to=int(CHART_SETTINGS.MAX_SMOOTHING_FACTOR * 100),
            number_of_steps=19,
            command=self._on_smoothing_slider_change,
        )
        self._smoothing_slider.bind("<ButtonRelease-1>", self._on_smoothing_slider_release)
        self._smoothing_slider.pack(side="top", padx=5, pady=(0, 5))
        
        self._smoothing_slider.set(self._smoothing_factor * 100)
        self._update_smoothing_label(self._smoothing_factor * 100)
    
    def _create_frequency_slider(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(side="left", padx=10, pady=0, fill="y")
        
        self._frequency_label = ctk.CTkLabel(frame, text="")
        self._frequency_label.pack(side="top", pady=(5, 0))
        
        self._frequency_slider = ctk.CTkSlider(
            frame,
            from_=int(SENSOR_SETTINGS.MIN_READING_FREQUENCY * 100),
            to=int(SENSOR_SETTINGS.MAX_READING_FREQUENCY * 100),
            number_of_steps=99,
            command=self._on_frequency_slider_change,
        )
        self._frequency_slider.bind("<ButtonRelease-1>", self._on_frequency_slider_release)
        self._frequency_slider.pack(side="top", padx=5, pady=(0, 5))
        
        self._frequency_slider.set(self._reading_frequency * 100)
        self._update_frequency_label(self._reading_frequency * 100)
    
    def _create_num_sensors_slider(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(side="left", padx=10, pady=0, fill="y")
        
        self._num_sensors_label = ctk.CTkLabel(frame, text="")
        self._num_sensors_label.pack(side="top", pady=(5, 0))
        
        self._num_sensors_slider = ctk.CTkSlider(
            frame,
            from_=SENSOR_SETTINGS.MIN_SENSORS,
            to=SENSOR_SETTINGS.MAX_SENSORS,
            number_of_steps=SENSOR_SETTINGS.MAX_SENSORS - SENSOR_SETTINGS.MIN_SENSORS,
            command=self._on_num_sensors_slider_change,
        )
        self._num_sensors_slider.bind("<ButtonRelease-1>", self._on_num_sensors_slider_release)
        self._num_sensors_slider.pack(side="top", padx=5, pady=(0, 5))
        
        self._num_sensors_slider.set(self._num_sensors)
        self._update_num_sensors_label(self._num_sensors)
    
    def _create_strategy_checkboxes(self) -> None:
        if not self._available_strategies:
            return
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(side="left", padx=10, pady=0, fill="y")
        
        label = ctk.CTkLabel(frame, text="Voters:")
        max_rows = 2 if len(self._available_strategies) >= 4 else 1
        total_cols = (len(self._available_strategies) + max_rows - 1) // max_rows
        label.grid(row=0, column=0, columnspan=total_cols, pady=(5, 0), sticky="w")
        
        for i, strategy in enumerate(self._available_strategies):
            row_index = (i % max_rows) + 1
            col_index = i // max_rows
            
            checkbox = ctk.CTkCheckBox(
                frame,
                text=strategy.name,
                command=lambda name=strategy.name: self._on_strategy_checkbox_toggle(name),
            )
            checkbox.grid(row=row_index, column=col_index, sticky="w", padx=10, pady=5)
            self._strategy_checkboxes[strategy.name] = checkbox
    
    def _on_smoothing_slider_change(self, value: float) -> None:
        self._update_smoothing_label(value)
    
    def _on_smoothing_slider_release(self, event) -> None:
        if self._smoothing_slider is None:
            return
        
        value = self._smoothing_slider.get()
        self._smoothing_factor = value / 100
        
        if self._on_smoothing_change:
            self._on_smoothing_change(self._smoothing_factor)
    
    def _update_smoothing_label(self, value: float) -> None:
        if self._smoothing_label:
            self._smoothing_label.configure(text=f"Smoothing Factor: {value / 100:.2f}")
    
    def _on_frequency_slider_change(self, value: float) -> None:
        self._update_frequency_label(value)
    
    def _on_frequency_slider_release(self, event) -> None:
        if self._frequency_slider is None:
            return
        
        value = self._frequency_slider.get()
        self._reading_frequency = value / 100
        
        if self._on_frequency_change:
            self._on_frequency_change(self._reading_frequency)
    
    def _update_frequency_label(self, value: float) -> None:
        if self._frequency_label:
            self._frequency_label.configure(text=f"Reading Frequency: {value / 100:.2f} s")
    
    def _on_num_sensors_slider_change(self, value: float) -> None:
        self._update_num_sensors_label(int(value))
    
    def _on_num_sensors_slider_release(self, event) -> None:
        if self._num_sensors_slider is None:
            return
        
        value = int(self._num_sensors_slider.get())
        self._num_sensors = value
        
        if self._on_num_sensors_change:
            self._on_num_sensors_change(value)
    
    def _update_num_sensors_label(self, value: int) -> None:
        if self._num_sensors_label:
            self._num_sensors_label.configure(text=f"Number of Sensors: {value}")
    
    def _on_strategy_checkbox_toggle(self, strategy_name: str) -> None:
        self._strategy_states[strategy_name] = not self._strategy_states[strategy_name]
        
        if self._on_strategy_toggle:
            self._on_strategy_toggle(strategy_name, self._strategy_states[strategy_name])
    
    @property
    def smoothing_factor(self) -> float:
        return self._smoothing_factor
    
    @property
    def reading_frequency(self) -> float:
        return self._reading_frequency
    
    @property
    def num_sensors(self) -> int:
        return self._num_sensors
    
    def get_active_strategies(self) -> list[str]:
        return [name for name, active in self._strategy_states.items() if active]
    
    def set_strategy_active(self, strategy_name: str, active: bool) -> None:
        if strategy_name in self._strategy_states:
            self._strategy_states[strategy_name] = active
            checkbox = self._strategy_checkboxes.get(strategy_name)
            if checkbox:
                if active:
                    checkbox.select()
                else:
                    checkbox.deselect()

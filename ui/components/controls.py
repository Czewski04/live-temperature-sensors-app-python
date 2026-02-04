from typing import Callable, Optional

import customtkinter as ctk


class ControlPanel(ctk.CTkFrame):
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        on_reset: Optional[Callable[[], None]] = None,
        on_restart: Optional[Callable[[], None]] = None,
        on_pause: Optional[Callable[[], None]] = None,
        on_resume: Optional[Callable[[], None]] = None,
        on_settings_toggle: Optional[Callable[[], None]] = None,
        on_back: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self._on_reset = on_reset
        self._on_restart = on_restart
        self._on_pause = on_pause
        self._on_resume = on_resume
        self._on_settings_toggle = on_settings_toggle
        self._on_back = on_back
        
        self._reset_button: Optional[ctk.CTkButton] = None
        self._restart_button: Optional[ctk.CTkButton] = None
        self._pause_button: Optional[ctk.CTkButton] = None
        self._resume_button: Optional[ctk.CTkButton] = None
        self._settings_button: Optional[ctk.CTkButton] = None
        self._back_button: Optional[ctk.CTkButton] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        self._reset_button = ctk.CTkButton(
            self,
            text="Reset",
            command=self._handle_reset,
        )
        self._reset_button.pack(side="left", padx=5, pady=5)
        
        self._restart_button = ctk.CTkButton(
            self,
            text="Restart",
            command=self._handle_restart,
        )
        self._restart_button.pack(side="left", padx=5, pady=5)
        
        self._resume_button = ctk.CTkButton(
            self,
            text="Resume",
            command=self._handle_resume,
            state="disabled",
        )
        self._resume_button.pack(side="left", padx=5, pady=5)
        
        self._pause_button = ctk.CTkButton(
            self,
            text="Pause",
            command=self._handle_pause,
        )
        self._pause_button.pack(side="left", padx=5, pady=5)
        

        self._back_button = ctk.CTkButton(
            self,
            text="Back to Home",
            command=self._handle_back,
        )
        self._back_button.pack(side="right", padx=5, pady=5)
        
        self._settings_button = ctk.CTkButton(
            self,
            text="Settings",
            command=self._handle_settings_toggle,
        )
        self._settings_button.pack(side="right", padx=5, pady=5)
    
    def _handle_reset(self) -> None:
        if self._on_reset:
            self._on_reset()
    
    def _handle_restart(self) -> None:
        if self._on_restart:
            self._on_restart()
    
    def _handle_pause(self) -> None:
        self.set_paused_state(True)
        if self._on_pause:
            self._on_pause()
    
    def _handle_resume(self) -> None:
        self.set_paused_state(False)
        if self._on_resume:
            self._on_resume()
    
    def _handle_settings_toggle(self) -> None:
        if self._on_settings_toggle:
            self._on_settings_toggle()
    
    def _handle_back(self) -> None:
        if self._on_back:
            self._on_back()
    
    def set_paused_state(self, is_paused: bool) -> None:
        if is_paused:
            if self._pause_button:
                self._pause_button.configure(state="disabled")
            if self._resume_button:
                self._resume_button.configure(state="normal")
        else:
            if self._pause_button:
                self._pause_button.configure(state="normal")
            if self._resume_button:
                self._resume_button.configure(state="disabled")
    
    def set_chart_active(self, is_active: bool) -> None:
        state = "normal" if is_active else "disabled"
        if self._pause_button:
            self._pause_button.configure(state=state)
        if self._resume_button:
            self._resume_button.configure(state="disabled")
    
    def update_settings_button_text(self, is_visible: bool) -> None:
        if self._settings_button:
            text = "Hide Settings" if is_visible else "Settings"
            self._settings_button.configure(text=text)


class HomeControls(ctk.CTkFrame):
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        on_show_chart: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self._on_show_chart = on_show_chart
        self._on_close = on_close
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        self._show_chart_button = ctk.CTkButton(
            self,
            text="Show all sensors",
            command=self._handle_show_chart,
        )
        self._show_chart_button.pack(pady=10)
        
        self._close_button = ctk.CTkButton(
            self,
            text="Close Application",
            command=self._handle_close,
            fg_color="red",
            hover_color="darkred",
        )
        self._close_button.pack(pady=10)
    
    def _handle_show_chart(self) -> None:
        if self._on_show_chart:
            self._on_show_chart()
    
    def _handle_close(self) -> None:
        if self._on_close:
            self._on_close()

from typing import Optional

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from config.settings import CHART_SETTINGS
from utils.data_parser import DataParser


class ChartWidget(ctk.CTkFrame):
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        num_sensors: int = 6,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        
        self._num_sensors = num_sensors
        
        self._fig: Optional[Figure] = None
        self._ax: Optional[Axes] = None
        self._canvas: Optional[FigureCanvasTkAgg] = None
        
        self._x_data: list[float] = []
        self._y_data_raw: list[list[float]] = [[] for _ in range(num_sensors)]
        self._y_data_smoothed: list[list[float]] = [[] for _ in range(num_sensors)]
        self._voting_data: dict[str, list[Optional[float]]] = {}
        
        self._smoothing_factor = CHART_SETTINGS.DEFAULT_SMOOTHING_FACTOR
        self._reading_frequency = 1.0
    
    def initialize(self) -> None:
        if self._fig is not None:
            return
        
        plt.style.use("dark_background")
        self._fig, self._ax = plt.subplots()
        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack(fill="both", expand=True)
        self._fig.tight_layout()
    
    def destroy_chart(self) -> None:
        if self._canvas:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None
        
        if self._fig:
            plt.close(self._fig)
            self._fig = None
        
        self._ax = None
    
    def clear_data(self) -> None:
        self._x_data.clear()
        self._y_data_raw = [[] for _ in range(self._num_sensors)]
        self._y_data_smoothed = [[] for _ in range(self._num_sensors)]
        self._voting_data.clear()
    
    def update_chart(
        self,
        sensor_data: list[Optional[float]],
        voting_results: dict[str, Optional[float]],
        active_strategies: list[str],
    ) -> None:
        if self._ax is None or self._fig is None:
            return
        
        if self._x_data:
            self._x_data.append(self._x_data[-1] + self._reading_frequency)
        else:
            self._x_data.append(0)
        
        for i in range(min(len(sensor_data), self._num_sensors)):
            raw_value = sensor_data[i]
            
            if raw_value is None:
                if self._y_data_raw[i]:
                    raw_value = self._y_data_raw[i][-1]
                else:
                    raw_value = 0.0
            
            self._y_data_raw[i].append(raw_value)
            
            if self._y_data_smoothed[i]:
                previous_smoothed = self._y_data_smoothed[i][-1]
            else:
                previous_smoothed = raw_value
            
            smoothed_value = DataParser.apply_exponential_smoothing(raw_value, previous_smoothed, self._smoothing_factor)
            self._y_data_smoothed[i].append(smoothed_value)
        
        for name, value in voting_results.items():
            if name not in self._voting_data:
                self._voting_data[name] = []
            self._voting_data[name].append(value)
        
        self._redraw(active_strategies)
    
    def _redraw(self, active_strategies: list[str]) -> None:
        if self._ax is None or self._fig is None or self._canvas is None:
            return
        
        self._ax.cla()
        
        has_active_voting = bool(active_strategies)
        
        for strategy_name in active_strategies:
            if strategy_name not in self._voting_data:
                continue
            
            data = self._voting_data[strategy_name]
            if not data:
                continue
            
            color = CHART_SETTINGS.VOTING_COLORS.get(strategy_name, "#ffffff")
            linestyle = CHART_SETTINGS.VOTING_LINESTYLES.get(strategy_name, "-")
            
            last_value = data[-1]
            if last_value is None:
                label_text = f"{strategy_name:<19}: no correct data"
            else:
                label_text = f"{strategy_name:<19}: {last_value:>11.2f}ºC"
            
            self._ax.plot(
                self._x_data[:len(data)],
                data,
                label=label_text,
                color=color,
                linestyle=linestyle,
                linewidth=4,
            )
        
        for i in range(self._num_sensors):
            if i >= len(self._y_data_smoothed) or not self._y_data_smoothed[i]:
                continue
            
            data = self._y_data_smoothed[i]
            last_raw = self._y_data_raw[i][-1] if self._y_data_raw[i] else 0
            
            if has_active_voting:
                color = CHART_SETTINGS.COLOUR_POOL_SECONDARY[i % len(CHART_SETTINGS.COLOUR_POOL_SECONDARY)]
                linestyle = "--"
                linewidth = 0.8
            else:
                color = CHART_SETTINGS.COLOUR_POOL_PRIMARY[i % len(CHART_SETTINGS.COLOUR_POOL_PRIMARY)]
                linestyle = "-"
                linewidth = 2
            
            self._ax.plot(
                self._x_data[:len(data)],
                data,
                label=f"Sensor {i + 1}: {last_raw:.1f}ºC",
                color=color,
                linestyle=linestyle,
                linewidth=linewidth,
            )
        
        self._ax.grid(True, linestyle="--", alpha=0.3)
        self._ax.legend(loc="upper left", prop={"family": "monospace", "size": 10})
        self._ax.set_xlabel("Time [s]")
        self._ax.set_ylabel("Temperature [ºC]")
        self._ax.set_title("Temperature Live Data")
        
        self._canvas.draw()
    
    @property
    def is_initialized(self) -> bool:
        return self._fig is not None and self._ax is not None
    
    @property
    def figure(self) -> Optional[Figure]:
        return self._fig
    
    def set_num_sensors(self, num_sensors: int) -> None:
        self._num_sensors = num_sensors
        self._y_data_raw = [[] for _ in range(num_sensors)]
        self._y_data_smoothed = [[] for _ in range(num_sensors)]
    
    def set_smoothing_factor(self, factor: float) -> None:
        self._smoothing_factor = max(0.0, min(1.0, factor))
    
    def set_reading_frequency(self, frequency: float) -> None:
        self._reading_frequency = frequency
    
    def get_chart_data(self) -> dict:
        return {
            "x_data": self._x_data.copy(),
            "sensor_data": [data.copy() for data in self._y_data_raw],
            "smoothed_data": [data.copy() for data in self._y_data_smoothed],
            "voting_data": {k: v.copy() for k, v in self._voting_data.items()},
        }
    
    def save_as_png(self, filepath: str) -> bool:
        if self._fig is None:
            return False
        
        try:
            self._fig.savefig(filepath)
            return True
        except Exception:
            return False
    
    def export_to_csv(self, filepath: str) -> bool:
        if not self._x_data:
            return False
        
        try:
            with open(filepath, "w", encoding="utf-8", newline="") as file:
                headers = ["Time [s]"]
                headers.extend([f"Sensor_{i + 1} [C]" for i in range(self._num_sensors)])
                file.write(";".join(headers) + "\n")
                
                for i in range(len(self._x_data)):
                    row = [f"{self._x_data[i]:.1f}".replace(".", ",")]
                    for j in range(self._num_sensors):
                        if j < len(self._y_data_raw) and i < len(self._y_data_raw[j]):
                            row.append(f"{self._y_data_raw[j][i]:.1f}".replace(".", ","))
                        else:
                            row.append("")
                    file.write(";".join(row) + "\n")
            
            return True
        except Exception:
            return False

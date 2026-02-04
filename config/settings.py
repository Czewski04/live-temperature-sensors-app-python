from dataclasses import dataclass, field
from typing import Final


@dataclass(frozen=True)
class ModbusSettings:
    
    PORT: str = "COM3"
    ADDRESS: int = 1
    BAUDRATE: int = 9600
    BYTESIZE: int = 8
    PARITY: str = "N"
    STOPBITS: int = 1
    TIMEOUT: float = 1.0
    START_ADDRESS: int = 0
    FUNCTION_CODE: int = 3
    ERROR_VALUE: int = -2731


@dataclass(frozen=True)
class SensorSettings:
    
    DEFAULT_NUM_SENSORS: int = 6
    MIN_SENSORS: int = 1
    MAX_SENSORS: int = 6
    DEFAULT_READING_FREQUENCY: float = 1.0
    MIN_READING_FREQUENCY: float = 0.1
    MAX_READING_FREQUENCY: float = 10.0
    TEMPERATURE_SCALE_FACTOR: float = 10.0


@dataclass
class ChartSettings:
    
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    WINDOW_TITLE: str = "Voting Algorithms Visualization"
    
    COLOUR_POOL_PRIMARY: list[str] = field(default_factory=lambda: [
        "#ff0000",
        "#00fa00",
        "#0000fa",
        "#fafa00",
        "#fa00fa",
        "#00fafa",
    ])
    
    COLOUR_POOL_SECONDARY: list[str] = field(default_factory=lambda: [
        "#ff9999",
        "#90ee90",
        "#9999ff",
        "#ffff99",
        "#ff99ff",
        "#99ffff",
    ])
    
    VOTING_COLORS: dict[str, str] = field(default_factory=lambda: {
        "Average": "#0000fa",
        "Median": "#fafa00",
        "Advanced m out of n": "#ff0000",
        "Majority": "#00fa00",
        "Average Adaptive": "#fa00fa",
    })
    
    VOTING_LINESTYLES: dict[str, str] = field(default_factory=lambda: {
        "Average": "-",
        "Median": "-",
        "Advanced m out of n": "-",
        "Majority": "--",
        "Average Adaptive": ":",
    })
    
    DEFAULT_SMOOTHING_FACTOR: float = 1.0
    MIN_SMOOTHING_FACTOR: float = 0.05
    MAX_SMOOTHING_FACTOR: float = 1.0


@dataclass(frozen=True)
class VotingSettings:
    
    THRESHOLD: float = 1.0
    HISTORY_THRESHOLD: float = 0.5
    
    MAJORITY_THRESHOLD_FACTOR: float = 0.5
    MAJORITY_DISTANCE_THRESHOLD: float = 1.0
    
    MAX_ERROR_COUNT: int = 2
    DEVIATION_THRESHOLD: float = 1.0


MODBUS_SETTINGS: Final[ModbusSettings] = ModbusSettings()
SENSOR_SETTINGS: Final[SensorSettings] = SensorSettings()
CHART_SETTINGS: Final[ChartSettings] = ChartSettings()
VOTING_SETTINGS: Final[VotingSettings] = VotingSettings()

from typing import Optional

from config.settings import MODBUS_SETTINGS, SENSOR_SETTINGS


class DataParser:
    
    @staticmethod
    def parse_temperature_registers(
        raw_values: list[int],
        error_value: int = MODBUS_SETTINGS.ERROR_VALUE,
        scale_factor: float = SENSOR_SETTINGS.TEMPERATURE_SCALE_FACTOR,
    ) -> list[Optional[float]]:
        parsed_values: list[Optional[float]] = []
        
        for value in raw_values:
            if value == error_value:
                parsed_values.append(None)
            else:
                parsed_values.append(value / scale_factor)
        
        return parsed_values
    
    @staticmethod
    def filter_valid_readings(readings: list[Optional[float]]) -> list[float]:
        return [reading for reading in readings if reading is not None]
    
    @staticmethod
    def fill_missing_readings(
        readings: list[Optional[float]],
        previous_readings: Optional[list[float]] = None,
        default_value: float = 0.0,
    ) -> list[float]:
        result: list[float] = []
        
        for i, reading in enumerate(readings):
            if reading is not None:
                result.append(reading)
            elif previous_readings and i < len(previous_readings):
                result.append(previous_readings[i])
            else:
                result.append(default_value)
        
        return result
    
    @staticmethod
    def apply_exponential_smoothing(
        current_value: float,
        previous_smoothed: float,
        smoothing_factor: float,
    ) -> float:
        return (smoothing_factor * current_value) + ((1 - smoothing_factor) * previous_smoothed)
    
    @staticmethod
    def validate_reading_range(
        reading: float,
        min_value: float = -50.0,
        max_value: float = 150.0,
    ) -> bool:
        return min_value <= reading <= max_value

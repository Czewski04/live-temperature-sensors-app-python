import logging
import queue
import threading
import time
from typing import Optional

import minimalmodbus
import serial

from config.settings import MODBUS_SETTINGS, SENSOR_SETTINGS
from core.interfaces import DataQueueProvider
from utils.data_parser import DataParser


logger = logging.getLogger(__name__)


class ModbusService(DataQueueProvider):
    
    def __init__(
        self,
        port: str = MODBUS_SETTINGS.PORT,
        address: int = MODBUS_SETTINGS.ADDRESS,
        baudrate: int = MODBUS_SETTINGS.BAUDRATE,
        num_sensors: int = SENSOR_SETTINGS.DEFAULT_NUM_SENSORS,
        reading_frequency: float = SENSOR_SETTINGS.DEFAULT_READING_FREQUENCY,
    ):
        self._port = port
        self._address = address
        self._baudrate = baudrate
        self._num_sensors = num_sensors
        self._reading_frequency = reading_frequency
        self._start_address = MODBUS_SETTINGS.START_ADDRESS
        
        self._instrument: Optional[minimalmodbus.Instrument] = None
        self._data_queue: queue.Queue[list[Optional[float]]] = queue.Queue()
        
        self._running_event = threading.Event()
        self._stop_event = threading.Event()
        self._read_thread: Optional[threading.Thread] = None
        
        self._config_lock = threading.Lock()
    
    def get_data_queue(self) -> queue.Queue[list[Optional[float]]]:
        return self._data_queue
    
    def connect(self) -> None:
        try:
            self._instrument = minimalmodbus.Instrument(self._port, self._address)
            self._instrument.serial.baudrate = self._baudrate
            self._instrument.serial.bytesize = MODBUS_SETTINGS.BYTESIZE
            self._instrument.serial.parity = serial.PARITY_NONE
            self._instrument.serial.stopbits = MODBUS_SETTINGS.STOPBITS
            self._instrument.serial.timeout = MODBUS_SETTINGS.TIMEOUT
            logger.info(f"Connected to Modbus device on {self._port}")
        except serial.SerialException as e:
            logger.error(f"Failed to connect to Modbus device: {e}")
            raise ConnectionError(f"Failed to connect to {self._port}: {e}") from e
    
    def disconnect(self) -> None:
        if self._instrument is not None:
            try:
                if self._instrument.serial.is_open:
                    self._instrument.serial.close()
                    logger.info("Modbus connection closed")
            except Exception as e:
                logger.warning(f"Error closing Modbus connection: {e}")
            finally:
                self._instrument = None
    
    def is_connected(self) -> bool:
        return (
            self._instrument is not None
            and self._instrument.serial.is_open
        )
    
    def start(self) -> None:
        if self._read_thread is not None and self._read_thread.is_alive():
            logger.warning("Reading thread already running")
            return
        
        self._stop_event.clear()
        self._running_event.set()
        
        self._read_thread = threading.Thread(
            target=self._reading_loop,
            name="ModbusReadThread",
            daemon=True,
        )
        self._read_thread.start()
        logger.info("Modbus reading thread started")
    
    def stop(self) -> None:
        self._stop_event.set()
        self._running_event.set()
        
        if self._read_thread is not None:
            self._read_thread.join(timeout=2.0)
            self._read_thread = None
        
        self.disconnect()
        logger.info("Modbus service stopped")
    
    def pause(self) -> None:
        self._running_event.clear()
        logger.debug("Modbus reading paused")
    
    def resume(self) -> None:
        self._running_event.set()
        logger.debug("Modbus reading resumed")
    
    def is_paused(self) -> bool:
        return not self._running_event.is_set()
    
    def update_reading_frequency(self, frequency: float) -> None:
        with self._config_lock:
            self._reading_frequency = max(
                SENSOR_SETTINGS.MIN_READING_FREQUENCY,
                min(frequency, SENSOR_SETTINGS.MAX_READING_FREQUENCY),
            )
        logger.debug(f"Reading frequency updated to {self._reading_frequency}s")
    
    def update_num_sensors(self, num_sensors: int) -> None:
        with self._config_lock:
            self._num_sensors = max(
                SENSOR_SETTINGS.MIN_SENSORS,
                min(num_sensors, SENSOR_SETTINGS.MAX_SENSORS),
            )
        logger.debug(f"Number of sensors updated to {self._num_sensors}")
    
    @property
    def num_sensors(self) -> int:
        with self._config_lock:
            return self._num_sensors
    
    @property
    def reading_frequency(self) -> float:
        with self._config_lock:
            return self._reading_frequency
    
    def _reading_loop(self) -> None:
        try:
            self.connect()
            
            while not self._stop_event.is_set():
                self._running_event.wait()
                
                if self._stop_event.is_set():
                    break
                
                try:
                    raw_values = self._read_registers()
                    parsed_data = DataParser.parse_temperature_registers(raw_values)
                    self._data_queue.put(parsed_data)
                except minimalmodbus.NoResponseError as e:
                    logger.warning(f"No response from Modbus device: {e}")
                except minimalmodbus.InvalidResponseError as e:
                    logger.warning(f"Invalid Modbus response: {e}")
                except Exception as e:
                    logger.error(f"Error reading Modbus data: {e}")
                
                with self._config_lock:
                    sleep_time = self._reading_frequency
                
                time.sleep(sleep_time)
                
        except ConnectionError as e:
            logger.error(f"Connection error in reading loop: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in reading loop: {e}")
        finally:
            self.disconnect()
    
    def _read_registers(self) -> list[int]:
        if self._instrument is None:
            raise RuntimeError("Not connected to Modbus device")
        
        with self._config_lock:
            num_sensors = self._num_sensors
        
        return self._instrument.read_registers(
            self._start_address,
            num_sensors,
            functioncode=MODBUS_SETTINGS.FUNCTION_CODE,
        )
    
    def clear_queue(self) -> None:
        with self._data_queue.mutex:
            self._data_queue.queue.clear()

import threading
import time
import minimalmodbus as mdbs
import serial

class ModbusBackend:
    def __init__(self, data_queue, num_sensors, reading_frequency):
        self.data_queue = data_queue
        self.port = 'COM3'
        self.address = 1
        self.baudrate = 9600
        self.num_sensors = num_sensors
        self.reading_frequency = reading_frequency
        self.start_address = 0
        self.error_value = -2731
        self.instrument = None
        self.running_event = threading.Event()
        self.stop_event = threading.Event()
        self.initialize_instrument()

    def initialize_instrument(self):
        self.instrument = mdbs.Instrument(self.port, self.address)
        self.instrument.serial.baudrate = self.baudrate
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = serial.PARITY_NONE
        self.instrument.serial.stopbits = 1
        self.instrument.serial.timeout = 1

    def read_data(self):
        raw_values = self.instrument.read_registers(self.start_address, self.num_sensors, functioncode=3)
        return raw_values

    def modbus_reading(self):
        try:
            while not self.stop_event.is_set():
                self.running_event.wait()
                raw_values = self.read_data()
                parsed_data = self.data_parser(raw_values)
                self.data_queue.put(parsed_data)
                time.sleep(self.reading_frequency)
        except mdbs.NoResponseError as e:
            print(e)
        except Exception as e:
            print(e)
        finally:
            self.close_connection()


    def data_parser(self, raw_values):
        parsed_values = []
        for value in raw_values:
            if value == self.error_value:
                parsed_values.append(None)
            else:
                parsed_values.append(value / 10.0)
        return parsed_values

    def close_connection(self):
        if self.instrument.serial.is_open:
            self.instrument.serial.close()

    def pause(self):
        self.running_event.clear()

    def resume(self):
        self.running_event.set()

    def stop(self):
        self.stop_event.set()
        self.running_event.set()

    def update_reading_frequency(self, new_frequency):
        self.reading_frequency = new_frequency


    def update_num_sensors(self, new_value):
        self.num_sensors = new_value

    def start_reading_thread(self):
        read_thread = threading.Thread(target=self.modbus_reading, daemon=True)
        read_thread.start()

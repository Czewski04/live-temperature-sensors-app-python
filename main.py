import logging
import sys

from config.settings import MODBUS_SETTINGS, SENSOR_SETTINGS
from infrastructure.modbus_service import ModbusService
from ui.main_window import MainWindow


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def create_modbus_service() -> ModbusService:
    return ModbusService(
        port=MODBUS_SETTINGS.PORT,
        address=MODBUS_SETTINGS.ADDRESS,
        baudrate=MODBUS_SETTINGS.BAUDRATE,
        num_sensors=SENSOR_SETTINGS.DEFAULT_NUM_SENSORS,
        reading_frequency=SENSOR_SETTINGS.DEFAULT_READING_FREQUENCY,
    )


def main() -> int:
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Sensor Fusion Application")
    
    try:
        modbus_service = create_modbus_service()
        modbus_service.start()
        app = MainWindow(data_provider=modbus_service)
        logger.info("Application initialized, starting main loop")
        app.mainloop()
        logger.info("Application closed normally")
        return 0
        
    except Exception as e:
        logger.exception(f"Application error: {e}")
        return 1
    finally:
        try:
            modbus_service.stop()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())

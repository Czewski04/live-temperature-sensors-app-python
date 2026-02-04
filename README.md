# Sensor Fusion Application

A real-time temperature monitoring and sensor fusion application with advanced voting algorithms for data validation and fault tolerance.

<img width="1180" height="641" alt="chart1" src="https://github.com/user-attachments/assets/ff9212b8-8dac-4b2b-a99e-b7b503b38616" />


## 📋 Overview

This application reads temperature data from multiple sensors via Modbus RTU protocol and applies various voting algorithms to determine the most reliable temperature reading. The system provides real-time visualization, configurable sensor fusion strategies, and comprehensive fault detection mechanisms.

## ✨ Features

- **Real-time Monitoring**: Live temperature data visualization from up to 6 sensors
- **Multiple Voting Algorithms**:
  - **Average**: Simple arithmetic mean of all sensor readings
  - **Median**: Robust median voting resistant to outliers
  - **Advanced M-out-of-N**: Weighted consensus algorithm with historical fallback
  - **Majority**: Group-based voting with proximity clustering
  - **Average Adaptive**: Self-adjusting algorithm that automatically excludes faulty sensors
- **Interactive UI**: Modern CustomTkinter-based interface with dark theme
- **Configurable Parameters**:
  - Number of active sensors (1-6)
  - Reading frequency (0.1-10 seconds)
  - Exponential smoothing factor
  - Individual voting algorithm toggles
- **Data Export**: Save charts as PNG images or export raw data to CSV
- **Thread-Safe Architecture**: Robust multi-threaded design with proper synchronization

<p align="center">
  <img width="1180" height="641" alt="chart3" src="https://github.com/user-attachments/assets/6eb6f5ba-dd3e-49b4-aaed-166617db568f" />
</p>

## 🏗️ Architecture

The application follows **Clean Architecture** and **Layered Architecture** principles with clear separation of concerns:

```
sensor_fusion_app/
├── config/                    # Configuration layer
│   ├── settings.py            # Application constants and settings
│   └── __init__.py
├── core/                      # Business logic layer
│   ├── interfaces.py          # Abstract base classes (Strategy Pattern)
│   ├── algorithms.py          # Voting algorithm implementations
│   └── __init__.py
├── infrastructure/            # External communication layer
│   ├── modbus_service.py      # Modbus RTU communication service
│   └── __init__.py
├── ui/                        # Presentation layer
│   ├── main_window.py         # Main application window
│   ├── chart_widget.py        # Matplotlib chart component
│   ├── components/
│   │   ├── controls.py        # Control buttons panel
│   │   ├── settings_panel.py  # Settings sliders and checkboxes
│   │   └── __init__.py
│   └── __init__.py
├── utils/                     # Utility layer
│   ├── data_parser.py         # Modbus data parsing utilities
│   └── __init__.py
├── main.py                    # Application entry point
└── requirements.txt           # Python dependencies
```

### Design Patterns

- **Strategy Pattern**: Interchangeable voting algorithms
- **Dependency Injection**: Loose coupling between layers
- **Repository Pattern**: Data queue abstraction
- **Observer Pattern**: Event-driven UI updates

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Serial port access for Modbus communication
- Windows/Linux/macOS

### Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd live-temperature-sensors-app-python
```

2. **Create a virtual environment**:
```bash
python -m venv venv
```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/macOS:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## 📦 Dependencies

- **customtkinter** (5.2.2): Modern UI framework
- **matplotlib** (3.10.8): Data visualization
- **numpy** (2.4.2): Numerical computations
- **minimalmodbus** (2.1.1): Modbus RTU communication
- **pyserial** (3.5): Serial port communication

## ⚙️ Configuration

Edit `config/settings.py` to customize application behavior:

### Modbus Settings
```python
PORT: str = "COM3"           # Chose correct serial port
ADDRESS: int = 1             # Modbus slave address
BAUDRATE: int = 9600         # Communication speed
ERROR_VALUE: int = -2731     # Sensor error indicator
```

### Sensor Settings
```python
DEFAULT_NUM_SENSORS: int = 6
MIN_SENSORS: int = 1
MAX_SENSORS: int = 6
DEFAULT_READING_FREQUENCY: float = 1.0  # seconds
TEMPERATURE_SCALE_FACTOR: float = 10.0  # Raw value divisor
```

### Voting Algorithm Parameters
```python
THRESHOLD: float = 1.0                    # M-out-of-N threshold
HISTORY_THRESHOLD: float = 0.5            # Historical fallback threshold
MAJORITY_DISTANCE_THRESHOLD: float = 1.0  # Majority grouping distance
MAX_ERROR_COUNT: int = 2                  # Adaptive algorithm error tolerance
DEVIATION_THRESHOLD: float = 1.0          # Adaptive algorithm deviation limit
```

## 🎮 Usage

### Starting the Application

```bash
python main.py
```

### Main Interface

1. **Home Screen**:
   - Click "Show all sensors" to start monitoring
   - Click "Close Application" to exit

2. **Monitoring Screen**:
   - **Control Buttons**:
     - **Reset**: Clear all chart data
     - **Restart**: Reset and restart data collection
     - **Pause/Resume**: Control data acquisition
     - **Settings**: Show/hide configuration panel
     - **Back to Home**: Return to main menu
   
   - **Settings Panel** (toggle with Settings button):
     - **Smoothing Factor**: Adjust exponential smoothing (0.05-1.0)
     - **Reading Frequency**: Set data acquisition rate (0.1-10s)
     - **Number of Sensors**: Select active sensors (1-6)
     - **Voters**: Enable/disable voting algorithms

3. **Saving Data**:
   - When returning to home, choose:
     - **Let work in background**: Continue data collection
     - **Pause**: Stop collection, keep data
     - **Save to File**: Export as PNG or CSV
     - **Abort**: Discard all data

### Voting Algorithms

Each voting algorithm can be independently enabled:

- **Average**: Fast, simple, but sensitive to outliers
- **Median**: Robust against single outlier sensors
- **Advanced m out of n**: Best for detecting sensor consensus
- **Majority**: Groups similar readings, rejects minorities
- **Average Adaptive**: Automatically excludes consistently faulty sensors

## 📊 Data Format

### Modbus Register Format

The application expects temperature data in the following format:
- **Register Address**: 0-5 (configurable)
- **Function Code**: 3 (Read Holding Registers)
- **Data Type**: 16-bit signed integer
- **Scale**: Value / 10.0 = Temperature in °C
- **Error Value**: -2731 indicates sensor fault

### CSV Export Format

```csv
Time [s];Sensor_1 [C];Sensor_2 [C];...;Sensor_6 [C]
0,0;25,5;26,0;...;24,8
1,0;25,6;26,1;...;24,9
```

## 🔧 Development

### Project Structure Principles

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Dependency Inversion**: High-level modules don't depend on low-level modules
3. **Open/Closed Principle**: Open for extension, closed for modification
4. **Interface Segregation**: Small, focused interfaces
5. **Single Responsibility**: Each class has one reason to change

### Adding New Voting Algorithms

1. Create a new class in `core/algorithms.py`:
```python
class MyStrategy(VotingStrategy):
    @property
    def name(self) -> str:
        return "My Strategy"
    
    def vote(self, data: list[float], historical_result: Optional[float] = None) -> Optional[float]:
        return 0.0
```

2. Register in `ui/main_window.py`:
```python
self._all_strategies: dict[str, VotingStrategy] = {
    "My Strategy": MyStrategy(),
}
```

### Thread Safety

The application uses multiple threads:
- **Main Thread**: UI event loop
- **Modbus Thread**: Data acquisition
- **Communication**: Thread-safe `queue.Queue`

## 🐛 Troubleshooting

### Common Issues

1. **Serial Port Error**:
   - Check if COM port is correct in `config/settings.py`
   - Verify no other application is using the port
   - Ensure proper permissions for serial port access

2. **No Response from Modbus Device**:
   - Verify device is powered and connected
   - Check baudrate, parity, and stopbits settings
   - Test with a Modbus diagnostic tool

3. **Import Errors**:
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

## 📝 License

This project is released under the MIT License.

## 👥 Author

- [Wiktor Wilczewski](https://github.com/Czewski04)

## 🙏 Acknowledgments

- **CustomTkinter**: Modern UI components
- **Matplotlib**: Professional data visualization
- **MinimalModbus**: Simple Modbus RTU implementation
- **NumPy**: Efficient numerical computations

---
**Last Updated**: February 2026

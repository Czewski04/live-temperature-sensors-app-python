from abc import ABC, abstractmethod
from typing import Optional
import queue


class VotingStrategy(ABC):
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def vote(self, data: list[float], historical_result: Optional[float] = None) -> Optional[float]:
        pass
    
    def reset(self) -> None:
        pass


class StatefulVotingStrategy(VotingStrategy):
    
    @abstractmethod
    def reset(self) -> None:
        pass


class ModbusReader(ABC):
    
    @abstractmethod
    def read_registers(self, start_address: int, count: int) -> list[int]:
        pass
    
    @abstractmethod
    def connect(self) -> None:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        pass


class DataQueueProvider(ABC):
    
    @abstractmethod
    def get_data_queue(self) -> queue.Queue:
        pass
    
    @abstractmethod
    def start(self) -> None:
        pass
    
    @abstractmethod
    def stop(self) -> None:
        pass
    
    @abstractmethod
    def pause(self) -> None:
        pass
    
    @abstractmethod
    def resume(self) -> None:
        pass

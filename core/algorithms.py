import math
from typing import Optional

import numpy as np

from core.interfaces import VotingStrategy, StatefulVotingStrategy
from config.settings import VOTING_SETTINGS


class AverageStrategy(VotingStrategy):
    
    @property
    def name(self) -> str:
        return "Average"
    
    def vote(self, data: list[float], historical_result: Optional[float] = None) -> Optional[float]:
        if not data:
            return None
        return float(np.average(data))


class MedianStrategy(VotingStrategy):
    
    @property
    def name(self) -> str:
        return "Median"
    
    def vote(self, data: list[float], historical_result: Optional[float] = None) -> Optional[float]:
        if not data:
            return None
        return float(np.median(data))


class MOutOfNStrategy(VotingStrategy):
    
    def __init__(
        self,
        threshold: float = VOTING_SETTINGS.THRESHOLD,
        history_threshold: float = VOTING_SETTINGS.HISTORY_THRESHOLD,
    ):
        self._threshold = threshold
        self._history_threshold = history_threshold
    
    @property
    def name(self) -> str:
        return "Advanced m out of n"
    
    def vote(self, data: list[float], historical_result: Optional[float] = None) -> Optional[float]:
        if not data:
            return None
        
        n = len(data)
        m = n // 2 + 1  # Majority threshold
        weights = [1] * n  # Equal weights for all sensors
        
        object_list: list[Optional[float]] = [None] * n
        tallies_list: list[float] = [0] * n
        
        # Initialize with first reading
        object_list[0] = data[0]
        tallies_list[0] = weights[0]
        
        # Process remaining readings
        for i in range(1, n):
            x_i = data[i]
            w_i = weights[i]
            matched_index = self._find_matching_object(x_i, object_list, tallies_list, n)
            
            if matched_index != -1:
                tallies_list[matched_index] += w_i
            else:
                self._add_or_replace_object(x_i, w_i, object_list, tallies_list, n)
        
        # Second pass: count votes and check for majority
        tallies_list = [0] * n
        for i in range(n):
            x_i = data[i]
            w_i = weights[i]
            for j in range(n):
                if object_list[j] is not None and abs(x_i - object_list[j]) <= self._threshold:
                    tallies_list[j] += w_i
                    if tallies_list[j] >= m:
                        return object_list[j]
        
        # Fallback to historical result
        return self._fallback_to_history(data, historical_result)
    
    def _find_matching_object(
        self,
        value: float,
        object_list: list[Optional[float]],
        tallies_list: list[float],
        n: int,
    ) -> int:
        for j in range(n):
            if object_list[j] is not None and tallies_list[j] != 0:
                if abs(value - object_list[j]) <= self._threshold:
                    return j
        return -1
    
    def _add_or_replace_object(
        self,
        value: float,
        weight: float,
        object_list: list[Optional[float]],
        tallies_list: list[float],
        n: int,
    ) -> None:
        for j in range(n):
            if tallies_list[j] == 0:
                object_list[j] = value
                tallies_list[j] = weight
                return
        
        min_val = min(tallies_list)
        min_index = tallies_list.index(min_val)
        
        if weight <= min_val:
            for j in range(n):
                tallies_list[j] = max(0, tallies_list[j] - weight)
        else:
            object_list[min_index] = value
            tallies_list[min_index] = weight
            for j in range(n):
                tallies_list[j] = max(0, tallies_list[j] - min_val)
    
    def _fallback_to_history(
        self,
        data: list[float],
        historical_result: Optional[float],
    ) -> Optional[float]:
        if historical_result is None:
            return None
        
        distances = [abs(historical_result - reading) for reading in data]
        min_distance = min(distances)
        min_index = distances.index(min_distance)
        
        if min_distance <= self._history_threshold:
            return data[min_index]
        return None


class MajorityStrategy(VotingStrategy):
    
    def __init__(self, threshold: float = VOTING_SETTINGS.MAJORITY_DISTANCE_THRESHOLD):
        self._threshold = threshold
    
    @property
    def name(self) -> str:
        return "Majority"
    
    def vote(self, data: list[float], historical_result: Optional[float] = None) -> Optional[float]:
        if not data:
            return None
        
        majority_threshold = math.ceil((len(data) + 1) / 2)
        sorted_data = sorted(data)
        
        n = len(sorted_data)
        distance = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                distance[i, j] = abs(sorted_data[i] - sorted_data[j])
        
        groups_list: list[list[float]] = []
        for i in range(n):
            group = [sorted_data[i]]
            for j in range(i + 1, n):
                if distance[i, j] <= self._threshold:
                    group.append(sorted_data[j])
                else:
                    break
            groups_list.append(group)
        
        for group in groups_list:
            if len(group) >= majority_threshold:
                return float(np.average(group))
        
        return None


class AverageAdaptiveStrategy(StatefulVotingStrategy):
    
    def __init__(
        self,
        max_error_count: int = VOTING_SETTINGS.MAX_ERROR_COUNT,
        deviation_threshold: float = VOTING_SETTINGS.DEVIATION_THRESHOLD,
    ):
        self._max_error_count = max_error_count
        self._deviation_threshold = deviation_threshold
        self._active_status_list: list[bool] = []
        self._error_count: list[int] = []
    
    @property
    def name(self) -> str:
        return "Average Adaptive"
    
    @property
    def active_status_list(self) -> list[bool]:
        return self._active_status_list.copy()
    
    @property
    def error_count(self) -> list[int]:
        return self._error_count.copy()
    
    def reset(self) -> None:
        self._active_status_list.clear()
        self._error_count.clear()
    
    def vote(self, data: list[float], historical_result: Optional[float] = None) -> Optional[float]:
        if not data:
            return None
        
        self._ensure_state_initialized(len(data))
        
        average = self._calculate_active_average(data)
        
        if average is None:
            return self._handle_all_disabled(data)
        
        self._update_sensor_status(data, average, historical_result)
        
        return average
    
    def _ensure_state_initialized(self, sensor_count: int) -> None:
        current_count = len(self._active_status_list)
        if current_count < sensor_count:
            for _ in range(sensor_count - current_count):
                self._active_status_list.append(True)
                self._error_count.append(0)
    
    def _calculate_active_average(self, data: list[float]) -> Optional[float]:
        total_value = 0.0
        counter = 0
        
        for i, reading in enumerate(data):
            if self._active_status_list[i]:
                total_value += reading
                counter += 1
        
        return total_value / counter if counter > 0 else None
    
    def _handle_all_disabled(self, data: list[float]) -> Optional[float]:
        average = sum(data) / len(data)
        
        for i, reading in enumerate(data):
            if abs(reading - average) <= self._deviation_threshold:
                self._error_count[i] -= 1
                if self._error_count[i] <= 0:
                    self._active_status_list[i] = True
            else:
                self._error_count[i] = self._max_error_count
        
        return None
    
    def _update_sensor_status(
        self,
        data: list[float],
        average: float,
        historical_result: Optional[float],
    ) -> None:
        for i, reading in enumerate(data):
            if self._active_status_list[i]:
                self._update_active_sensor(i, reading, average, historical_result)
            else:
                self._try_recover_sensor(i, reading, average)
    
    def _update_active_sensor(
        self,
        index: int,
        reading: float,
        average: float,
        historical_result: Optional[float],
    ) -> None:
        deviates_from_average = abs(reading - average) > self._deviation_threshold
        deviates_from_history = (
            historical_result is not None
            and abs(reading - historical_result) > self._deviation_threshold
        )
        
        if historical_result is not None:
            if deviates_from_history and deviates_from_average:
                self._error_count[index] += 1
                if self._error_count[index] >= self._max_error_count:
                    self._active_status_list[index] = False
            else:
                self._error_count[index] = 0
        else:
            if deviates_from_average:
                self._error_count[index] += 1
                if self._error_count[index] >= self._max_error_count:
                    self._active_status_list[index] = False
            else:
                self._error_count[index] = 0
    
    def _try_recover_sensor(self, index: int, reading: float, average: float) -> None:
        if abs(reading - average) <= self._deviation_threshold:
            self._error_count[index] -= 1
            if self._error_count[index] <= 0:
                self._active_status_list[index] = True
        else:
            self._error_count[index] = self._max_error_count


class Voter:
    
    def __init__(self, strategies: Optional[list[VotingStrategy]] = None):
        self._strategies: list[VotingStrategy] = strategies or []
        self._historical_results: dict[str, Optional[float]] = {}
    
    @property
    def strategies(self) -> list[VotingStrategy]:
        return self._strategies.copy()
    
    def set_strategies(self, strategies: list[VotingStrategy]) -> None:
        self._strategies = strategies
    
    def add_strategy(self, strategy: VotingStrategy) -> None:
        if strategy not in self._strategies:
            self._strategies.append(strategy)
    
    def remove_strategy(self, strategy: VotingStrategy) -> None:
        if strategy in self._strategies:
            self._strategies.remove(strategy)
    
    def clear_strategies(self) -> None:
        self._strategies.clear()
    
    def vote(self, data: list[float]) -> dict[str, Optional[float]]:
        results: dict[str, Optional[float]] = {}
        
        for strategy in self._strategies:
            historical = self._historical_results.get(strategy.name)
            result = strategy.vote(data, historical)
            results[strategy.name] = result
            
            if result is not None:
                self._historical_results[strategy.name] = result
        
        return results
    
    def reset(self) -> None:
        self._historical_results.clear()
        for strategy in self._strategies:
            strategy.reset()
    
    def get_historical_result(self, strategy_name: str) -> Optional[float]:
        return self._historical_results.get(strategy_name)

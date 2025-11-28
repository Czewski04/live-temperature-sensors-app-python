import math
import numpy as np


class Voter:
    def __init__(self):
        self.avg = False
        self.median = False
        self.adv_out_of_n = False
        self.majority = False
        self.average_adaptive = False

        self.active_status_list = []
        self.error_count = []


    def average_voting(self, data):
        return np.average(data)


    def median_voting(self, data):
        return np.median(data)


    def advanced_m_out_of_n_voting(self, data, history_result):
        n = len(data)
        m = n // 2 + 1
        weights = []
        for i in range(n):
            weights.append(1)
        threshold = 1.0
        history_threshold = 0.5

        object_list = [0] * n
        tallies_list = [0] * n

        object_list[0] = data[0]
        tallies_list[0] = weights[0]

        for i in range(1, n):
            x_i = data[i]
            w_i = weights[i]
            matched_index = -1
            for j in range(n):
                if object_list[j] is not None and tallies_list[j] != 0:
                    if abs(x_i - object_list[j]) <= threshold:
                        matched_index = j
                        break
            if matched_index != -1:
                tallies_list[matched_index] += w_i
            else:
                empty_index = -1

                for j in range(n):
                    if tallies_list[j] == 0:
                        empty_index = j
                        break
                if empty_index != -1:
                    object_list[empty_index] = x_i
                    tallies_list[empty_index] = w_i
                else:
                    min_val = min(tallies_list)
                    min_index = tallies_list.index(min_val)
                    if w_i <= min_val:
                        for j in range(n):
                            tallies_list[j] = max(0, tallies_list[j] - w_i)
                    else:
                        object_list[min_index] = x_i
                        tallies_list[min_index] = w_i
                        for j in range(n):
                                tallies_list[j] = max(0, tallies_list[j] - min_val)
        tallies_list = [0] * n
        for i in range(n):
            x_i = data[i]
            w_i = weights[i]
            for j in range(n):
                if object_list[j] is not None and abs(x_i - object_list[j]) <= threshold:
                    tallies_list[j] = tallies_list[j] + w_i
                    if tallies_list[j] >= m:
                        return object_list[j]
        if history_result is None:
            return None
        distances = []
        for i in range(n):
            distances.append(abs(history_result - data[i]))
        min_distance = min(distances)
        min_index = distances.index(min_distance)
        if min_distance <= history_threshold:
            return data[min_index]
        else:
            return None


    def majority_voting(self, data):
        threshold = 1
        majority_threshold = math.ceil((len(data) + 1) / 2)
        distance = np.zeros((len(data), len(data)))
        groups_list = []
        sorted_data = sorted(data)
        for i in range(len(sorted_data)):
            for j in range(i + 1, len(sorted_data)):
                    distance[i,j] = abs(sorted_data[i] - sorted_data[j])
        for i in range(len(data)):
            group = []
            groups_list.append(group)
            group.append(sorted_data[i])
            for j in range(i + 1, len(sorted_data)):
                if distance[i,j] <= threshold:
                    group.append(sorted_data[j])
                else:
                    break
        for i in range(len(groups_list)):
            if len(groups_list[i]) >= majority_threshold:
                return np.average(groups_list[i])
        return None

    def average_adaptive_voting(self, data):
        if len(self.active_status_list) < len(data) and len(self.error_count) < len(data):
            for i in range(len(data)-len(self.active_status_list)):
                self.active_status_list.append(True)
                self.error_count.append(0)
        max_error_count = 10
        deviation_threshold = 1.0
        total_value = 0.0
        counter = 0

        for i in range(len(data)):
            if self.active_status_list[i]:
                total_value += data[i]
                counter += 1
        if counter == 0:
            for i in range(len(data)):
                total_value += data[i]
                counter += 1
            average = total_value / counter
            for i in range(len(data)):
                if abs(data[i] - average) <= deviation_threshold:
                    self.error_count[i] -= 1
                    if self.error_count[i] <= 0:
                        self.active_status_list[i] = True
                else:
                    self.error_count[i] = max_error_count
            return None
        average = total_value / counter
        for i in range(len(data)):
            if self.active_status_list[i]:
                if abs(data[i] - average) > deviation_threshold:
                    self.error_count[i] += 1
                    if self.error_count[i] >= max_error_count:
                        self.active_status_list[i] = False
                else:
                    self.error_count[i] = 0
        for i in range(len(data)):
            if not self.active_status_list[i]:
                if abs(data[i] - average) <= deviation_threshold:
                    self.error_count[i] -= 1
                    if self.error_count[i] <= 0:
                        self.active_status_list[i] = True
                else:
                    self.error_count[i] = max_error_count
        return average

    def vote(self, data, history_result):
        results = {}
        if self.avg:
            results['Average'] = self.average_voting(data)
        if self.median:
            results['Median'] = self.median_voting(data)
        if self.adv_out_of_n:
            results['Advanced m out of n'] = self.advanced_m_out_of_n_voting(data, history_result)
        if self.majority:
            results['Majority'] = self.majority_voting(data)
        if self.average_adaptive:
            results['Average Adaptive'] = self.average_adaptive_voting(data)

        return results

    def update_votes(self, avg, median, adv_out_of_n, majority, average_adaptive):
        self.avg = avg
        self.median = median
        self.adv_out_of_n = adv_out_of_n
        self.majority = majority
        self.average_adaptive = average_adaptive
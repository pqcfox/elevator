import abc
import random
from copy import copy
from constants import *
from elevator import Building, PriorityElevator
from itertools import permutations


class Optimizer:
    __metaclass__ = abc.ABCMeta

    def __init__(self, crowd):
        self.crowd = crowd

    @abc.abstractmethod
    def optimize(self):
        """Returns the optimal parameter choices."""


class PartitionOptimizer(Optimizer):
    def optimize(self):
        """Optimizes by partitioning the parameter list."""
        best_partitions, best_time = None, None
        for order in permutations(range(1, FLOOR_COUNT + 1)):
            part_size = FLOOR_COUNT // ELEVATOR_COUNT
            partitions = [order[i * part_size:(i + 1) * part_size] for i in range(ELEVATOR_COUNT - 1)]
            partitions.append(order[(ELEVATOR_COUNT - 1) * part_size:])

            elevators = [PriorityElevator(i, partitions[i]) for i in range(len(partitions))]
            building = Building(elevators, self.crowd)
            time = building.run()
            if best_partitions is None or time < best_time:
                best_partitions, best_time = partitions, time

        return best_partitions


class GeneticOptimizer(Optimizer):
    def __init__(self, crowd):
        super().__init__(crowd)
        self.draw_pool = list(range(1, FLOOR_COUNT + 1))

    def optimize(self):
        population = []
        for _ in range(POPULATION_SIZE):
            parameters = [self.select(self.draw_pool) for _ in range(ELEVATOR_COUNT)]
            population.append(parameters)

        for _ in range(GENERATIONS):
            population = self.prune(population)
            population = self.reproduce(population)

        return min(population, key=self.test)

    def test(self, parameters):
        flattened = [value for parameter in parameters for value in parameter]
        if any([floor not in flattened for floor in self.draw_pool]):
            return float('inf')

        elevators = [PriorityElevator(i, parameters[i]) for i in range(len(parameters))]
        building = Building(elevators, self.crowd)
        return building.run()

    def prune(self, population):
        scores = [(self.test(parameters), parameters) for parameters in population]
        pruned = sorted(scores)[:SURVIVAL_RATE]
        return [pair[1] for pair in pruned]

    def reproduce(self, population):
        shuffled = copy(population)
        random.shuffle(shuffled)
        pairs = [(shuffled[i], shuffled[i+1]) for i in range(len(shuffled) // 2)]
        return population + [self.breed(*pair) for pair in pairs]

    def breed(self, a, b):
        child = []
        for a_param, b_param in zip(a, b):
            a_select = self.select(a_param)
            b_select = self.select(b_param)
            child.append(tuple(set(a_select) | set(b_select)))
        return child

    def select(self, parameter):
        select_parameter = []
        for value in parameter:
            if random.random() < GENE_PASS_RATE:
                select_parameter.append(value)
        return tuple(select_parameter)

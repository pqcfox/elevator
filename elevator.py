import abc
import random
from copy import copy
from constants import *


class FloorError(Exception):
    """An exception indicating an action was performed on the wrong floor."""


class Building:
    """A class which accepts an elevator class and maintains instances of it."""
    def __init__(self, elevators, crowd):
        """Initializes the building."""
        self.elevators = elevators
        self.crowd = crowd

    def run(self):
        """Generate elevators, run them, and time how long they took."""
        elevator_times = [0 for _ in range(len(self.elevators))]
        crowd_copy = copy(self.crowd)
        for elevator in self.elevators:
            elevator.reset(crowd_copy)

        while any([not elevator.is_done() for elevator in self.elevators]):
            least_index = elevator_times.index(min(elevator_times))
            current_elevator = self.elevators[least_index]
            elevator_times[least_index] += current_elevator.step()
        return max(elevator_times)


class Elevator(object):
    """A simple class to simulate an elevator."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, index):
        """Initializes the elevator."""
        self.index = index

    def reset(self, crowd):
        self.floor = 0
        self.contents = []
        self.crowd = crowd

    def is_done(self):
        """Determines whether the elevator is finished with all tasks."""
        return len(list(self.crowd.elements())) == 0 and len(self.contents) == 0

    @abc.abstractmethod
    def load(self):
        """Load the elevator and return the time it took."""

    def move(self, floor):
        """Move the elevator and return the time it took."""
        distance = abs(self.floor - floor)
        self.floor = floor
        return MOVE_TIME * distance

    def unload(self):
        """Unload all contents from the elevator and return the time it took."""
        self.contents = [content for content in self.contents if content != self.floor]
        return UNLOAD_TIME

    @abc.abstractmethod
    def step(self):
        """Take one action and return the time it took."""


class StandardElevator(Elevator):
    """An Elevator that drops people off in a standard order."""
    __metaclass__ = abc.ABCMeta

    def step(self):
        """Go to each floor one by one, then return."""
        if len(self.contents) == 0:
            if self.floor != 0:
                return self.move(0)
            return self.load()

        smallest = min(self.contents)
        if self.floor < smallest:
            return self.move(smallest)
        return self.unload()

    @abc.abstractmethod
    def load(self):
        """Load the elevator and return the time it took."""


class RandomElevator(StandardElevator):
    """An Elevator which allows people to load randomly."""
    def load(self):
        """Loads contents randomly."""
        if self.floor != 0:
            raise FloorError("Cannot load from non-ground floor!")
        count = ELEVATOR_CAPACITY - len(self.contents)
        all_crowd = list(self.crowd.elements())
        loaded = random.sample(all_crowd, count) if count < len(all_crowd) else all_crowd
        self.contents.extend(loaded)
        for level in loaded:
            self.crowd[level] -= 1
        return LOAD_TIME


class PriorityElevator(StandardElevator):
    """An Elevator which allows priority loading."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, index, priorities):
        super().__init__(index)
        self.priorities = priorities

    def load(self):
        """Load the elevator and return the time it took"""
        self.load_with_priority(self.priorities)
        return LOAD_TIME

    def load_with_priority(self, priorities):
        if len(priorities) == 0:
            return
        current = priorities[0]
        remaining = ELEVATOR_CAPACITY - len(self.contents)
        count = min(remaining, self.crowd[current])
        self.crowd[current] -= count
        self.contents.extend([current] * count)
        self.load_with_priority(priorities[1:])
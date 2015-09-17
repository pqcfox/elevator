from collections import Counter
from constants import *
from elevator import Building, RandomElevator, PriorityElevator
from optimizer import PartitionOptimizer, GeneticOptimizer

crowd = Counter({1: 100, 2: 100, 3: 20, 4: 100, 5: 50, 6: 20})
henry_alpha_priorities = [(1, 4, 3, 5), (2, 5), (4, 6, 5)]
henry_beta_priorities = [(1, 5), (2, 6), (3, 4)]
henry_gamma_priorities = [(1, 2, 3, 4, 5, 6) for _ in range(ELEVATOR_COUNT)]
partition_priorities = PartitionOptimizer(crowd).optimize()
genetic_priorities = GeneticOptimizer(crowd).optimize()

print("Partition priorities: {}".format(partition_priorities))
print("Genetic priorities: {}\n".format(genetic_priorities))

random_elevators = [RandomElevator(i) for i in range(ELEVATOR_COUNT)]
henry_alpha_elevators = [PriorityElevator(i, henry_alpha_priorities[i]) for i in range(ELEVATOR_COUNT)]
henry_beta_elevators = [PriorityElevator(i, henry_beta_priorities[i]) for i in range(ELEVATOR_COUNT)]
henry_gamma_elevators = [PriorityElevator(i, henry_gamma_priorities[i]) for i in range(ELEVATOR_COUNT)]
partition_elevators = [PriorityElevator(i, partition_priorities[i]) for i in range(ELEVATOR_COUNT)]
genetic_elevators = [PriorityElevator(i, genetic_priorities[i]) for i in range(ELEVATOR_COUNT)]

elevator_lists = {"Random": random_elevators,
                  "Henry Alpha": henry_alpha_elevators,
                  "Henry Beta": henry_beta_elevators,
                  "Henry Gamma": henry_gamma_elevators,
                  "Partition": partition_elevators,
                  "Genetic": genetic_elevators}

for system, elevators in elevator_lists.items():
    building = Building(elevators, crowd)
    times = []

    for i in range(250):
        times.append(building.run())

    print("System: {}".format(system))
    print("Minimum: {}".format(min(times)))
    print("Average: {}".format(sum(times)/len(times)))
    print("Maximum: {}\n".format(max(times)))
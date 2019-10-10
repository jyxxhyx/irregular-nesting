from domain.problem import Position, Problem
from local_search.evaluation import positition, evaluation

import sys


class Solution:
    positions: Position

    def __init__(self, sequence, positions=None, objective=None):
        self.sequences = sequence
        if positions is None:
            self.positions = dict()
        else:
            self.positions = positions
        if objective is None:
            self.objective = sys.maxsize
        else:
            self.objective = objective
        return

    def generate_positions(self, problem: Problem, nfps, config):
        self.positions = positition.bottom_left_heuristic(problem, self.sequences, nfps, config)
        return

    def generate_objective(self, problem: Problem):
        self.objective = evaluation.calculate_objective(problem, self.positions)
        return

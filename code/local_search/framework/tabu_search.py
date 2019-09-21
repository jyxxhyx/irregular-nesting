from local_search.framework.base_alg import BaseAlg
from local_search.construction.constructor import polygon_area_descending, offset_polygon_area_descending, \
    rectangular_area_descending, rectangular_diagonal_descending
from local_search.improvement.perturb import single_shuffle
from local_search.domain.solution import Solution
from domain.problem import Problem

from collections import deque
from copy import deepcopy, copy
from typing import Union


class TabuSearch(BaseAlg):
    def __init__(self, problem: Problem):
        self.problem = problem
        self.best_solution: Union[Solution, None] = None
        self.current_solution: Union[Solution, None] = None
        self.tabu_list = deque(maxlen=10)
        return

    def solve(self):
        # initial_sequence = polygon_area_descending(self.problem)
        initial_sequence = offset_polygon_area_descending(self.problem)
        # initial_sequence = rectangular_area_descending(self.problem)
        # initial_sequence = diagonal_descending(self.problem)
        self.current_solution = Solution(initial_sequence)
        self.current_solution.generate_positions(self.problem)
        self.current_solution.generate_objective(self.problem)
        self.best_solution = Solution(copy(initial_sequence), deepcopy(self.current_solution.positions),
                                      self.current_solution.objective)

        # TODO improvement阶段待实现（包括tabu search更新机制）
        return

    def get_best_solution(self):
        return self.best_solution

    def get_current_solution(self):
        return self.current_solution

    def get_best_objective(self):
        return self.best_solution.objective

    def get_current_objective(self):
        return self.current_solution.objective

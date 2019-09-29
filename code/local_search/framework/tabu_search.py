from local_search.framework.base_alg import BaseAlg
from local_search.construction.constructor import polygon_area_descending, offset_polygon_area_descending, \
    rectangular_area_descending, rectangular_diagonal_descending, sampling_based_on_offset_polygon_area_square
from local_search.improvement.perturb import single_shuffle
from local_search.domain.solution import Solution
from geometry.nfp_generator import generate_nfp, generate_nfp_pool
from domain.problem import Problem

from collections import deque
from itertools import combinations
from copy import deepcopy, copy
from typing import Union
import logging
import multiprocessing
from multiprocessing import Pool


class TabuSearch(BaseAlg):
    def __init__(self, problem: Problem):
        self.problem = problem
        self.best_solution: Union[Solution, None] = None
        self.current_solution: Union[Solution, None] = None
        self.tabu_list = deque(maxlen=10)
        self.nfps = dict()
        return

    def solve(self):
        # initial_sequence = polygon_area_descending(self.problem)
        initial_sequence = offset_polygon_area_descending(self.problem)
        # initial_sequence = rectangular_area_descending(self.problem)
        # initial_sequence = diagonal_descending(self.problem)
        # initial_sequence = sampling_based_on_offset_polygon_area_square(self.problem)
        self.current_solution = Solution(initial_sequence)
        self.current_solution.generate_positions(self.problem, self.nfps)
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

    def initialize_nfps(self):
        logger = logging.getLogger(__name__)
        for index, (shape1, shape2) in enumerate(combinations(self.problem.shapes, 2)):
            if index % 100 == 99:
                logger.info('{} nfps calculated.'.format(index + 1))
            single_nfp = generate_nfp(shape1.offset_polygon, shape2.offset_polygon)
            # p1相对于p2的nfp取负即为p2相对于p1的nfp
            self.nfps[shape1.shape_id, shape2.shape_id] = single_nfp
            self.nfps[shape2.shape_id, shape1.shape_id] = [[[-point[0], -point[1]] for point in single_polygon]
                                                           for single_polygon in single_nfp]
        return

    def initialize_nfps_pool(self, number_processes: int = 1):
        logger = logging.getLogger(__name__)
        p = Pool(processes=number_processes)
        logger.info('Prepare the input.')
        input_list = [(shape1.offset_polygon, shape2.offset_polygon, shape1.shape_id, shape2.shape_id)
                      for shape1, shape2 in combinations(self.problem.shapes, 2)]
        logger.info('Start to map.')
        result = p.map(generate_nfp_pool, input_list)
        for single_nfp, shape1_str, shape2_str in result:
            self.nfps[shape1_str, shape2_str] = single_nfp
            self.nfps[shape2_str, shape1_str] = [[[-point[0], -point[1]] for point in single_polygon]
                                                 for single_polygon in single_nfp]
        p.close()

        return


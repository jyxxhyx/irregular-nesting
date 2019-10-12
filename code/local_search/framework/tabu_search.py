from local_search.framework.base_alg import BaseAlg
from local_search.construction.constructor import polygon_area_descending, offset_polygon_area_descending, \
    rectangular_area_descending, rectangular_diagonal_descending, sampling_based_on_offset_polygon_area_square, \
    rectangular_residual_area_descending
from local_search.improvement.perturb import single_shuffle
from local_search.domain.solution import Solution
from geometry.nfp_generator import generate_nfp, generate_nfp_pool
from domain.problem import Problem

from collections import deque
from itertools import combinations, product
from copy import deepcopy, copy
from typing import Union
import logging
import os
import multiprocessing
from multiprocessing import Pool
import ujson


class TabuSearch(BaseAlg):
    def __init__(self, problem: Problem, config):
        self.problem = problem
        self.config = config
        self.best_solution: Union[Solution, None] = None
        self.current_solution: Union[Solution, None] = None
        self.tabu_list = deque(maxlen=10)
        self.nfps = dict()
        return

    def solve(self):
        # initial_sequence = polygon_area_descending(self.problem)
        # initial_sequence = offset_polygon_area_descending(self.problem)
        # initial_sequence = rectangular_residual_area_descending(self.problem)
        initial_sequence = rectangular_area_descending(self.problem)
        # initial_sequence = rectangular_diagonal_descending(self.problem)
        # initial_sequence = sampling_based_on_offset_polygon_area_square(self.problem)
        self.current_solution = Solution(initial_sequence)
        self.current_solution.generate_positions(self.problem, self.nfps,
                                                 self.config)
        self.current_solution.generate_objective(self.problem)
        self.best_solution = Solution(
            copy(initial_sequence), deepcopy(self.current_solution.positions),
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

    def initialize_nfps(self, input_folder, config, batch_id):
        logger = logging.getLogger(__name__)

        nfps_file_name = '{}_{}_{}_{}_{}_{}_{}_{}'.format(
            batch_id, config['scale'], config['extra_offset'],
            config['polygon_vertices'], config['clipper']['meter_limit'],
            config['clipper']['arc_tolerance'], config['clipper']['precision'],
            config['nfps_json'])

        nfps_full_name = os.path.join(os.pardir, config['output_folder'],
                                      input_folder, nfps_file_name)
        if os.path.isfile(nfps_full_name):
            logger.info('NFPs json file exists.')
            with open(nfps_full_name, 'r') as json_file:
                self.nfps = ujson.load(json_file)
        else:
            logger.info(
                'NFPs json file does not exist. Start to calculate NFPs.')
            for index, (hole, shape) in enumerate(product(self.problem.material.holes, self.problem.shapes)):
                self._calculate_one_nfp(index, hole, shape)
            start_index = len(self.problem.shapes) * len(self.problem.material.holes)
            for index, (shape1, shape2) in enumerate(
                    combinations(self.problem.shapes, 2)):
                self._calculate_one_nfp(start_index + index, shape1, shape2)
            with open(nfps_full_name, 'w') as json_file:
                ujson.dump(self.nfps, json_file)
                logger.info('NFPs saved to file: {}'.format(nfps_full_name))
        return

    def initialize_nfps_pool(self, input_folder, config, batch_id, number_processes: int = os.cpu_count() - 1):
        # 最好不要超过cpu数
        logger = logging.getLogger(__name__)

        nfps_file_name = '{}_{}_{}_{}_{}_{}_{}_{}'.format(
            batch_id, config['scale'], config['extra_offset'],
            config['polygon_vertices'], config['clipper']['meter_limit'],
            config['clipper']['arc_tolerance'], config['clipper']['precision'],
            config['nfps_json'])

        nfps_full_name = os.path.join(os.pardir, config['output_folder'],
                                      input_folder, nfps_file_name)
        if os.path.isfile(nfps_full_name):
            logger.info('NFPs json file exists.')
            with open(nfps_full_name, 'r') as json_file:
                self.nfps = ujson.load(json_file)
        else:
            logger.info(
                'NFPs json file does not exist. Start to calculate NFPs.')
            p = Pool(processes=number_processes)
            logger.info('Prepare the input.')

            iterator = list()
            iterator.extend(product(self.problem.material.holes, self.problem.shapes))
            iterator.extend(combinations(self.problem.shapes, 2))

            input_list = [{
                'polygon1': shape1.offset_polygon,
                'polygon2': shape2.offset_polygon,
                'shape1_str': shape1.shape_id,
                'shape2_str': shape2.shape_id,
                'precision': config['clipper']['precision']
            } for shape1, shape2 in iterator]
            logger.info('Start to map.')
            result = p.map(generate_nfp_pool, input_list)
            for single_nfp, shape1_str, shape2_str in result:
                self.nfps[shape1_str + shape2_str] = single_nfp
                self.nfps[shape2_str + shape1_str] = [[[
                    -point[0], -point[1]
                ] for point in single_polygon] for single_polygon in single_nfp]
            p.close()
            p.join()
            p.terminate()
            logger.info('Multiprocessing finished.')

            with open(nfps_full_name, 'w') as json_file:
                ujson.dump(self.nfps, json_file)
                logger.info('NFPs saved to file: {}'.format(nfps_full_name))
        return

    def _calculate_one_nfp(self, index, shape1, shape2):
        logger = logging.getLogger(__name__)
        if index % 100 == 0:
            logger.info('{} nfps calculated.'.format(index))
        single_nfp = generate_nfp(shape1.offset_polygon,
                                  shape2.offset_polygon,
                                  self.config['clipper'])
        # p1相对于p2的nfp取负即为p2相对于p1的nfp
        self.nfps[shape1.shape_id + shape2.shape_id] = single_nfp
        self.nfps[shape2.shape_id +
                  shape1.shape_id] = [[[-point[0], -point[1]]
                                       for point in single_polygon]
                                      for single_polygon in single_nfp]


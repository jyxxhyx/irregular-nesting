from src.local_search.framework.base_alg import BaseAlg
from src.local_search.construction.constructor import polygon_area_descending, offset_polygon_area_descending, \
    rectangular_area_descending, rectangular_diagonal_descending, rectangular_residual_area_descending
from src.local_search.improvement.perturb import single_shuffle
from src.local_search.domain.solution import Solution
from src.geometry.nfp_generator import generate_nfp, generate_nfp_pool
from src.geometry.rotate import rotate_180_3d, rotate_180_shift_3d, change_degree
from src.domain.problem import Problem
from src.output_handler.drawer import draw_two_polygons

from collections import deque
from itertools import combinations_with_replacement, product, permutations
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

    def initialize_nfps(self, input_folder, config, batch_id, similar_shapes):
        logger = logging.getLogger(__name__)

        nfps_file_name = _get_json_file_name(config, batch_id)
        nfps_full_name = os.path.join(os.getcwd(), config['output_folder'],
                                      input_folder, nfps_file_name)
        if os.path.isfile(nfps_full_name):
            logger.info('NFPs json file exists.')
            with open(nfps_full_name, 'r') as json_file:
                self.nfps = ujson.load(json_file)
        else:
            logger.info(
                'NFPs json file does not exist. Start to calculate NFPs.')
            for index, (hole, shape) in enumerate(
                    product(self.problem.material.holes, similar_shapes)):
                self._calculate_one_nfp(index, hole, shape)
            start_index = len(similar_shapes) * len(
                self.problem.material.holes)
            for index, (shape1, shape2) in enumerate(
                    combinations_with_replacement(similar_shapes, 2)):
                self._calculate_one_nfp(start_index + index, shape1, shape2)
            with open(nfps_full_name, 'w') as json_file:
                ujson.dump(self.nfps, json_file)
                logger.info('NFPs saved to file: {}'.format(nfps_full_name))
        return

    def initialize_nfps_pool(self,
                             input_folder,
                             config,
                             batch_id,
                             similar_shapes,
                             number_processes: int = os.cpu_count() - 1):
        # 最好不要超过cpu数
        logger = logging.getLogger(__name__)

        # self.test_rotation_nfp(similar_shapes, config['clipper'])

        nfps_file_name = _get_json_file_name(config, batch_id)
        nfps_full_name = os.path.join(os.getcwd(), config['output_folder'],
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

            rotate_shapes = [
                self.problem.shapes[shape.shape_id][180]
                for shape in similar_shapes
            ]

            # TODO 考虑旋转的情况
            iterator = list()
            iterator.extend(
                product(similar_shapes, self.problem.material.holes))
            # 考虑旋转
            iterator.extend(product(rotate_shapes,
                                    self.problem.material.holes))

            iterator.extend(combinations_with_replacement(similar_shapes, 2))
            iterator.extend(product(similar_shapes, rotate_shapes))

            input_list = [{
                'polygon1': shape1.offset_polygon,
                'polygon2': shape2.offset_polygon,
                'shape1_str': shape1.shape_id,
                'shape2_str': shape2.shape_id,
                'shape1_rotation': shape1.rotate_degree,
                'shape2_rotation': shape2.rotate_degree,
                'precision': config['clipper']['precision']
            } for shape1, shape2 in iterator]
            logger.info('Start to map.')
            result = p.map(generate_nfp_pool, input_list)
            logger.info('Multiprocessing finished.')
            for single_nfp, shape1_id, shape2_id, shape1_rotation, shape2_rotation in result:
                rotate_nfp = rotate_180_3d(single_nfp)
                self.nfps['{}_{}{}_{}'.format(shape1_id, shape1_rotation,
                                              shape2_id,
                                              shape2_rotation)] = single_nfp
                self.nfps['{}_{}{}_{}'.format(shape2_id, shape2_rotation,
                                              shape1_id,
                                              shape1_rotation)] = rotate_nfp

                shift_x = -self.problem.shapes[shape1_id][0].max_x
                shift_y = -self.problem.shapes[shape1_id][0].max_y
                if shape2_id in self.problem.shapes:
                    shift_x += self.problem.shapes[shape2_id][0].max_x
                    shift_y += self.problem.shapes[shape2_id][0].max_y
                    self.nfps['{}_{}{}_{}'.format(
                        shape1_id, change_degree(shape1_rotation), shape2_id,
                        change_degree(shape2_rotation))] = rotate_180_shift_3d(
                            single_nfp, shift_x, shift_y)
                    self.nfps['{}_{}{}_{}'.format(
                        shape2_id, change_degree(shape2_rotation), shape1_id,
                        change_degree(shape1_rotation))] = rotate_180_shift_3d(
                            rotate_nfp, -shift_x, -shift_y)
            p.close()
            p.join()
            p.terminate()
            logger.info('Results gathered.')

            if not config['is_production']:
                with open(nfps_full_name, 'w') as json_file:
                    ujson.dump(self.nfps, json_file)
                    logger.info('NFPs saved to file: {}'.format(nfps_full_name))
        return

    def _calculate_one_nfp(self, index, shape1, shape2):
        logger = logging.getLogger(__name__)
        if index % 100 == 0:
            logger.info('{} nfps calculated.'.format(index))
        single_nfp = generate_nfp(shape1.offset_polygon, shape2.offset_polygon,
                                  self.config['clipper'])
        # p1相对于p2的nfp取负即为p2相对于p1的nfp
        self.nfps[str(shape1) + str(shape2)] = single_nfp
        self.nfps[str(shape2) + str(shape1)] = rotate_180_3d(single_nfp)


def _get_json_file_name(config, batch_id):
    return '{}_{}_{}_{}_{}_{}_{}_{}_{}_{}'.format(
        batch_id, config['scale'], config['extra_offset'],
        config['extra_hole_offset'], config['polygon_vertices'],
        config['hausdorff_threshold'], config['clipper']['meter_limit'],
        config['clipper']['arc_tolerance'], config['clipper']['precision'],
        config['nfps_json'])

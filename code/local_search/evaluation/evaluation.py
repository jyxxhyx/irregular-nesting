from domain.problem import Problem, Position

import logging
from itertools import combinations, product
from shapely.geometry import Polygon, Point
import sys
from typing import Dict, Tuple


def calculate_objective(problem: Problem,
                        positions: Dict[str, Tuple[str, Position]]):
    assert len(positions) == len(problem.shapes)
    max_x = max(position.x + problem.shapes[key][inner_key].max_x
                for key, (inner_key, position) in positions.items())
    min_x = min(position.x + problem.shapes[key][inner_key].min_x
                for key, (inner_key, position) in positions.items())
    return max_x - min_x


def check_feasibility_distance(solution, problem: Problem, scale):
    logger = logging.getLogger(__name__)
    logger.info('Start to check the result.')

    feasibility_flag = _check_boundary(solution, problem)
    feasibility_flag = feasibility_flag and _check_holes(
        solution, problem, scale)
    feasibility_flag = feasibility_flag and _check_shapes(
        solution, problem, scale)

    if feasibility_flag:
        logger.info('Feasibility check passed.')
    else:
        logger.info('Feasibility check failed.')
    return


def _check_boundary(solution, problem: Problem):
    logger = logging.getLogger(__name__)
    feasibility_flag = True
    # 检查边框边界
    max_x = max(position.x + problem.shapes[key][inner_key].max_x
                for key, (inner_key, position) in solution.positions.items())
    min_x = min(position.x + problem.shapes[key][inner_key].min_x
                for key, (inner_key, position) in solution.positions.items())
    max_y = max(position.y + problem.shapes[key][inner_key].max_y
                for key, (inner_key, position) in solution.positions.items())
    min_y = min(position.y + problem.shapes[key][inner_key].min_y
                for key, (inner_key, position) in solution.positions.items())

    material = problem.material
    material_max_x = material.width - material.margin
    material_min_x = material.margin
    material_max_y = material.height - material.margin
    material_min_y = material.margin

    if max_x > material_max_x or max_y > material_max_y or min_x < material_min_x or min_y < material_min_y:
        logger.error('Positions of polygons: {}-{}, {}-{}'.format(
            min_x, max_x, min_y, max_y))
        logger.error('Margin of material: {}-{}, {}-{}'.format(
            material_min_x, material_max_x, material_min_y, material_max_y))
        feasibility_flag = False

    return feasibility_flag


def _check_holes(solution, problem: Problem, scale):
    logger = logging.getLogger(__name__)
    feasibility_flag = True

    min_distance = sys.maxsize

    positioned_shapes = [
        problem.shapes[key][inner_key]
        for key, (inner_key, position) in solution.positions.items()
    ]

    if problem.material.holes:
        for hole, shape in product(problem.material.holes, positioned_shapes):

            pos = solution.positions[shape.shape_id][1]
            shape_polygon = shape.generate_positioned_polygon_output(
                pos, scale)

            shapely_hole = Polygon(hole.scaled_polygon(scale))

            for point in shape_polygon:
                shapely_point = Point(point)
                temp_distance = shapely_hole.exterior.distance(shapely_point)
                if temp_distance * scale < problem.material.spacing:
                    feasibility_flag = False
                    logger.error(
                        'Shapes {} and {} are too close to each other'.format(
                            hole.shape_id, str(shape)))
                    logger.error(
                        'Point {} to shape {}\'s distance is {:.3f}'.format(
                            point, hole.shape_id, temp_distance))
                if min_distance > temp_distance:
                    min_distance = temp_distance
        logger.info(
            'Minimum distance between shapes and holes is {:.3f}.'.format(
                min_distance))
    else:
        logger.info('No holes. Skip the check.')
    return feasibility_flag


def _check_shapes(solution, problem: Problem, scale):
    logger = logging.getLogger(__name__)

    feasibility_flag = True
    min_distance = sys.maxsize

    positioned_shapes = [
        problem.shapes[key][inner_key]
        for key, (inner_key, position) in solution.positions.items()
    ]

    # 检查零件间的距离
    for shape1, shape2 in combinations(positioned_shapes, 2):
        pos1 = solution.positions[shape1.shape_id][1]
        pos2 = solution.positions[shape2.shape_id][1]

        polygon1 = shape1.generate_positioned_polygon_output(pos1, scale)
        polygon2 = shape2.generate_positioned_polygon_output(pos2, scale)

        shapely_polygon = Polygon(polygon2)

        for point in polygon1:
            shapely_point = Point(point)
            temp_distance = shapely_polygon.exterior.distance(shapely_point)
            if temp_distance * scale < problem.material.spacing:
                feasibility_flag = False
                logger.error(
                    'Shapes {} and {} are too close to each other'.format(
                        str(shape1), str(shape2)))
                logger.error(
                    'Point {} to shape {}\'s distance is {:.3f}'.format(
                        point, str(shape2), temp_distance))
            if min_distance > temp_distance:
                min_distance = temp_distance

    logger.info(
        'Minimum distance among shapes is {:.3f}.'.format(min_distance))
    return feasibility_flag

from domain.problem import Problem

import logging
from itertools import combinations, product
from shapely.geometry import Polygon, Point
import sys


def calculate_objective(problem: Problem, positions):
    assert len(positions) == len(problem.shapes)
    max_x = max(positions[i].x + problem.shapes[i].max_x
                for i in range(len(positions)))
    min_x = min(positions[i].x + problem.shapes[i].min_x
                for i in range(len(positions)))
    # max_y = max(positions[i].y + problem.shapes[i].max_y for i in range(len(positions)))
    # min_y = min(positions[i].y + problem.shapes[i].min_y for i in range(len(positions)))
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
    max_x = max(solution.positions[i].x + problem.shapes[i].max_x
                for i in range(len(solution.positions)))
    min_x = min(solution.positions[i].x + problem.shapes[i].min_x
                for i in range(len(solution.positions)))
    max_y = max(solution.positions[i].y + problem.shapes[i].max_y
                for i in range(len(solution.positions)))
    min_y = min(solution.positions[i].y + problem.shapes[i].min_y
                for i in range(len(solution.positions)))

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

    if problem.material.holes:
        for (index1,
             hole), (index2,
                     shape) in product(enumerate(problem.material.holes),
                                       enumerate(problem.shapes)):

            pos = solution.positions[index2]
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
                            hole.shape_id, shape.shape_id))
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

    # 检查零件间的距离
    for (index1, shape1), (index2,
                           shape2) in combinations(enumerate(problem.shapes),
                                                   2):
        pos1 = solution.positions[index1]
        pos2 = solution.positions[index2]

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
                        shape1.shape_id, shape2.shape_id))
                logger.error(
                    'Point {} to shape {}\'s distance is {:.3f}'.format(
                        point, shape2.shape_id, temp_distance))
            if min_distance > temp_distance:
                min_distance = temp_distance

    logger.info(
        'Minimum distance among shapes is {:.3f}.'.format(min_distance))
    return feasibility_flag

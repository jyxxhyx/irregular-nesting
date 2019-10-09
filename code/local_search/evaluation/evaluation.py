from domain.problem import Problem

import logging
from itertools import combinations
from shapely.geometry import Polygon, Point


def calculate_objective(problem: Problem, positions):
    assert len(positions) == len(problem.shapes)
    max_x = max(positions[i].x + problem.shapes[i].max_x
                for i in range(len(positions)))
    min_x = min(positions[i].x + problem.shapes[i].min_x
                for i in range(len(positions)))
    # max_y = max(positions[i].y + problem.shapes[i].max_y for i in range(len(positions)))
    # min_y = min(positions[i].y + problem.shapes[i].min_y for i in range(len(positions)))
    return max_x - min_x


def check_feasibility_offset():
    # TODO Apply multiple Point-in-polygon tests

    # Step 1. Update offset polygon with high precision

    # Step 2. Perform a huge number of pip tests

    return


def check_feasibility_distance(solution, problem: Problem, scale):
    logger = logging.getLogger(__name__)
    logger.info('Start to check the result.')
    feasibility_flag = True
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
    if feasibility_flag:
        logger.info('Feasibility check passed.')
    else:
        logger.info('Feasibility check failed.')
    return

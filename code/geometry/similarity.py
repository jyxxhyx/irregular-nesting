from domain.problem import Shape, Problem
from geometry.hausdorff import hausdorff_list, distance_function_list
from output_handler import drawer

import logging
import numpy as np


def get_similar_polygons(instance: Problem, threshold):
    logger = logging.getLogger(__name__)
    all_shapes = [
        shape for candidate_shapes in instance.shapes.values()
        for shape in candidate_shapes.values()
    ]
    for index, shape1 in enumerate(all_shapes):
        for i in range(index + 1, len(all_shapes)):
            shape2 = all_shapes[i]
            distance = calculate_similarity(shape1, shape2)
            if distance <= threshold:
                # TODO 如果改成并行计算，需要全部算完之后再重新刷一遍
                shape2.similar_shape = shape1.similar_shape
                logger.info(
                    'Hausdorff distance of shapes {} and {}: {}'.format(
                        str(shape1), str(shape2), distance))
                break
    logger.info(distance_function_list.cache_info())
    similar_offset_shapes = {shape.similar_shape for shape in all_shapes}
    logger.info('Size of origin shapes: {}. Size of unique shapes: {}.'.format(
        len(all_shapes), len(similar_offset_shapes)))
    return similar_offset_shapes


def calculate_similarity(shape1: Shape, shape2: Shape):
    polygon1 = shape1.offset_polygon
    polygon2 = shape2.offset_polygon
    distance = hausdorff_list(polygon1, polygon2)
    return distance

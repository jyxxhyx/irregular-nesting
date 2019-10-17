from src.domain.problem import Problem, Position, Shape
from src.geometry.nfp_generator import generate_nfp, generate_ifp, diff_ifp_nfps, intersect_polygons
from src.output_handler import drawer

import datetime
from typing import List, Dict, Tuple
import logging
import sys


def bottom_left_heuristic(problem: Problem, sequence: List[str], nfps,
                          config) -> Dict[str, Tuple[str, Position]]:
    logger = logging.getLogger(__name__)
    material = problem.material
    positions = dict()

    positioned_polygons = dict()
    # positioned_polygon_indices = list()

    # TODO ifp计算逻辑简化后，可以不纪录base_subject，目前debug需要，先保留
    base_subject = material.get_margin_polygon(material.width)

    weight = config['initial_weight']

    for outer_iter, key in enumerate(sequence):
        if outer_iter % 10 == 9:
            logger.info('{} shapes positioned.'.format(outer_iter + 1))

        candidate_shapes = problem.shapes[key]

        min_value = sys.maxsize
        min_rotation = -1
        min_position = Position(0, 0)

        # Find the minimum rotation
        for rotation, shape in candidate_shapes.items():
            # ifp_polygon = intersect_polygons(generate_ifp(material, shape, problem.offset_spacing), base_subject)
            ifp_polygon = generate_ifp(material, shape)

            for hole in material.holes:

                nfp_hole = _get_nfp(shape, hole, nfps, Position(0, 0),
                                    config['clipper'])
                if config['is_debug']:
                    drawer.draw_iteration(problem, ifp_polygon, nfp_hole,
                                          base_subject, positioned_polygons,
                                          shape.offset_polygon, outer_iter,
                                          (hole.shape_id, 0, rotation),
                                          'a', problem.batch_id)
                ifp_polygon = diff_ifp_nfps(ifp_polygon, nfp_hole)
                if config['is_debug']:
                    drawer.draw_iteration(problem, ifp_polygon, nfp_hole,
                                          base_subject, positioned_polygons,
                                          shape.offset_polygon, outer_iter,
                                          (hole.shape_id, 0, rotation),
                                          'b', problem.batch_id)

            for (previous_key,
                 previous_rotation), polygon in positioned_polygons.items():

                positioned_shape = problem.shapes[previous_key][previous_rotation]
                position = positions[previous_key][1]
                nfp_polygon = _get_nfp(shape, positioned_shape, nfps, position,
                                       config['clipper'])
                if config['is_debug']:
                    drawer.draw_iteration(problem, ifp_polygon, nfp_polygon,
                                          base_subject, positioned_polygons,
                                          shape.offset_polygon, outer_iter,
                                          (previous_key, previous_rotation, rotation),
                                          'a', problem.batch_id)
                ifp_polygon = diff_ifp_nfps(ifp_polygon, nfp_polygon)
                if config['is_debug']:
                    drawer.draw_iteration(problem, ifp_polygon, nfp_polygon,
                                          base_subject, positioned_polygons,
                                          shape.offset_polygon, outer_iter,
                                          (previous_key, previous_rotation, rotation),
                                          'b', problem.batch_id)

            # 每次选择一个x轴方向、y轴方向加权最小的点放置形状。
            # weight -> 0, y轴方向最小的位置，weight -> +infinity，x轴方向最小的位置

            value, min_idx, min_idx1 = min(
                (weight * v[0] + v[1], i, j)
                for j, ifp_single_polygon in enumerate(ifp_polygon)
                for i, v in enumerate(ifp_single_polygon))

            if min_value > value:
                min_value = value
                min_rotation = rotation
                min_position = Position(ifp_polygon[min_idx1][min_idx][0],
                                        ifp_polygon[min_idx1][min_idx][1])

        # logger.info('Shape {} with rotation {} chosen.'.format(key, min_rotation))
        positions[key] = (min_rotation, min_position)

        positioned_polygon = candidate_shapes[
            min_rotation].generate_positioned_offset_polygon(positions[key][1])
        base_subject = diff_ifp_nfps(base_subject, positioned_polygon)
        positioned_polygons[(key, min_rotation)] = positioned_polygon
        # positioned_polygon_indices.append((key, min_rotation))

        # x轴方向权重会不断增加
        weight += config['increment_weight']

    return positions


def _get_nfp(next_shape: Shape, positioned_shape: Shape, nfps: dict,
             position: Position, config_clipper):
    """
    在nfps中查找是否有两个形状的nfp，如果没有调用generate_nfp计算并存储，返回nfp并加上position对应的偏移量。
    Parameters
    ----------
    next_shape
    positioned_shape
    nfps: Dict[str, List[List[List[float]]]]
    position

    Returns
    -------

    """
    logger = logging.getLogger(__name__)
    shape_id1 = str(next_shape.similar_shape)
    shape_id2 = str(positioned_shape.similar_shape)
    if (shape_id1 + shape_id2) not in nfps:
        logger.warning('NFP {}-{} not found. Calculate online'.format(shape_id1, shape_id2))
        nfps[shape_id1 + shape_id2] = generate_nfp(
            next_shape.similar_shape.offset_polygon,
            positioned_shape.similar_shape.offset_polygon, config_clipper)
    return [[[position.x + node[0], position.y + node[1]] for node in each_nfp]
            for each_nfp in nfps[shape_id1 + shape_id2]]

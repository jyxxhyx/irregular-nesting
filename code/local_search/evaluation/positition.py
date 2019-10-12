from domain.problem import Problem, Position, Shape
from geometry.nfp_generator import generate_nfp, generate_ifp, diff_ifp_nfps, intersect_polygons
from output_handler import drawer

import datetime
from typing import List, Dict
import logging


def bottom_left_heuristic(problem: Problem, sequence, nfps,
                          config) -> Dict[int, Position]:
    logger = logging.getLogger(__name__)
    material = problem.material
    positions = dict()

    positioned_polygons = list()
    positioned_polygon_indices = list()

    # TODO ifp计算逻辑简化后，可以不纪录base_subject，目前debug需要，先保留
    base_subject = material.get_margin_polygon(material.width)

    weight = config['initial_weight']

    for outer_iter, idx in enumerate(sequence):
        if outer_iter % 10 == 9:
            logger.info('{} shapes positioned.'.format(outer_iter + 1))

        shape = problem.shapes[idx]
        # ifp_polygon = intersect_polygons(generate_ifp(material, shape, problem.offset_spacing), base_subject)
        ifp_polygon = generate_ifp(material, shape)

        for hole in material.holes:
            # nfp_hole = generate_nfp(shape.offset_polygon, hole.regular_polygon,
            #                         config['clipper'])
            nfp_hole = _get_nfp(shape, hole, nfps, Position(0, 0),
                                config['clipper'])
            ifp_polygon = diff_ifp_nfps(ifp_polygon, nfp_hole)

        for inner_iter, polygon in enumerate(positioned_polygons):
            # nfp_polygon = generate_nfp(shape.offset_polygon, polygon)
            positioned_shape = problem.shapes[
                positioned_polygon_indices[inner_iter]]
            position = positions[positioned_polygon_indices[inner_iter]]
            nfp_polygon = _get_nfp(shape, positioned_shape, nfps, position,
                                   config['clipper'])
            if config['is_debug']:
                drawer.draw_iteration(problem, ifp_polygon, nfp_polygon,
                                      base_subject, positioned_polygons,
                                      shape.offset_polygon, outer_iter,
                                      inner_iter, 'a',
                                      problem.shapes[0].batch_id)
            ifp_polygon = diff_ifp_nfps(ifp_polygon, nfp_polygon)
            if config['is_debug']:
                drawer.draw_iteration(problem, ifp_polygon, nfp_polygon,
                                      base_subject, positioned_polygons,
                                      shape.offset_polygon, outer_iter,
                                      inner_iter, 'b',
                                      problem.shapes[0].batch_id)

        # x轴方向权重会不断增加
        weight += config['increment_weight']
        # 每次选择一个x轴方向、y轴方向加权最小的点放置形状。
        # weight -> 0, y轴方向最小的位置，weight -> +infinity，x轴方向最小的位置

        _, min_idx, min_idx1 = min(
            (weight * v[0] + v[1], i, j)
            for j, ifp_single_polygon in enumerate(ifp_polygon)
            for i, v in enumerate(ifp_single_polygon))

        positions[idx] = Position(ifp_polygon[min_idx1][min_idx][0],
                                  ifp_polygon[min_idx1][min_idx][1])

        positioned_polygon = shape.generate_positioned_offset_polygon(
            positions[idx])
        base_subject = diff_ifp_nfps(base_subject, positioned_polygon)
        positioned_polygons.append(positioned_polygon)
        positioned_polygon_indices.append(idx)

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
    if (next_shape.shape_id + positioned_shape.shape_id) not in nfps:
        nfps[next_shape.shape_id + positioned_shape.shape_id] = generate_nfp(
            next_shape.offset_polygon, positioned_shape.offset_polygon,
            config_clipper)
    return [[[position.x + node[0], position.y + node[1]] for node in each_nfp]
            for each_nfp in nfps[next_shape.shape_id +
                                 positioned_shape.shape_id]]

from domain.problem import Problem, Position
from geometry.nfp_generator import generate_nfp, generate_ifp, diff_ifp_nfps, intersect_polygons
from output_handler import drawer

import datetime
from typing import List, Dict


def bottom_left_heuristic(problem: Problem, sequence) -> Dict[int, Position]:
    material = problem.material
    positions = dict()

    current_polygons = list()

    base_subject = material.get_margin_polygon(material.width)

    shape = problem.shapes[sequence[0]]
    ifp_polygon = generate_ifp(material, shape, problem.offset_spacing)
    positions[sequence[0]] = Position(material.margin, material.margin)

    positioned_polygon = shape.generate_positioned_offset_polygon(positions[sequence[0]])
    base_subject = diff_ifp_nfps(base_subject, positioned_polygon)
    current_polygons.append(positioned_polygon)

    weight = 1

    for outer_iter, idx in enumerate(sequence[1:]):
        if outer_iter % 10 == 9:
            print('{} shapes positioned. {}'.format(outer_iter + 1, datetime.datetime.now()))

        shape = problem.shapes[idx]
        # ifp_polygon = intersect_polygons(generate_ifp(material, shape, problem.offset_spacing), base_subject)
        ifp_polygon = generate_ifp(material, shape, problem.offset_spacing)

        for inner_iter, polygon in enumerate(current_polygons):
            # TODO 此处有效率上的优化空间，如果之前放的polygon离现在的ifp_polygon很远（用包络矩形检查一下），可以不算nfp。
            nfp_polygon = generate_nfp(shape.offset_polygon, polygon)
            # drawer.draw_iteration(problem, ifp_polygon, nfp_polygon, base_subject, current_polygons,
            #                       shape.offset_polygon, outer_iter,
            #                       inner_iter, 'a', problem.shapes[0].batch_id)
            ifp_polygon = diff_ifp_nfps(ifp_polygon, nfp_polygon)
            # drawer.draw_iteration(problem, ifp_polygon, nfp_polygon, base_subject, current_polygons,
            #                       shape.offset_polygon, outer_iter,
            #                       inner_iter, 'b', problem.shapes[0].batch_id)

        # x轴方向权重会不断增加
        weight += 1 / 10
        # 每次选择一个x轴方向、y轴方向加权最小的点放置形状。
        # weight -> 0, y轴方向最小的位置，weight -> +infinity，x轴方向最小的位置
        _, min_idx, min_idx1 = min((weight * v[0] + v[1], i, j) for j, ifp_single_polygon in enumerate(ifp_polygon)
                                   for i, v in enumerate(ifp_single_polygon))
        positions[idx] = Position(ifp_polygon[min_idx1][min_idx][0], ifp_polygon[min_idx1][min_idx][1])

        positioned_polygon = shape.generate_positioned_offset_polygon(positions[idx])
        base_subject = diff_ifp_nfps(base_subject, positioned_polygon)
        current_polygons.append(positioned_polygon)

    return positions


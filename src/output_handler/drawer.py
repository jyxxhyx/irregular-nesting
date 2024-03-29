from src.domain.problem import Shape, Problem

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numbers
import os
from pprint import pprint
from typing import List, Tuple


def draw_simple_polygon(input_polygon):
    """
    画一个简单的多边形
    Parameters
    ----------
    input_polygon
    """
    fig, ax = plt.subplots()
    patches = []
    polygon = Polygon(input_polygon, True)
    patches.append(polygon)

    face_colors = ('None', 'skyblue')
    edge_colors = ('aqua', 'b')

    p = PatchCollection(patches,
                        facecolors=face_colors,
                        edgecolors=edge_colors,
                        alpha=0.4)
    ax.add_collection(p)

    x_min = min(p[0] for p in input_polygon)
    x_max = max(p[0] for p in input_polygon)
    y_min = min(p[1] for p in input_polygon)
    y_max = max(p[1] for p in input_polygon)
    plt.xlim([x_min, x_max])
    plt.ylim([y_min, y_max])

    plt.show()


def draw_offset_shape(shape: Shape, text=None):
    """
    画一个形状和他对应的外延多边形
    Parameters
    ----------
    shape
    text
    """
    fig, ax = plt.subplots()
    patches = []
    polygon = Polygon(shape.polygon, True)
    patches.append(polygon)
    polygon = Polygon(shape.offset_polygon, True)
    patches.append(polygon)

    face_colors = ('None', 'skyblue')
    edge_colors = ('aqua', 'b')

    p = PatchCollection(patches,
                        facecolors=face_colors,
                        edgecolors=edge_colors,
                        alpha=0.4)
    ax.add_collection(p)

    x_min = min(p[0] for p in shape.offset_polygon)
    x_max = max(p[0] for p in shape.offset_polygon)
    y_min = min(p[1] for p in shape.offset_polygon)
    y_max = max(p[1] for p in shape.offset_polygon)
    plt.xlim([x_min, x_max])
    plt.ylim([y_min, y_max])

    plt.text((x_min + x_max) / 2, y_min + 10, text)

    plt.show()


def draw_two_shapes_nfp(shape1: Shape, shape2: Shape,
                        nfp: List[Tuple[float, float]]):
    """
    画两个多边形和对应的nfp
    Parameters
    ----------
    shape1
    shape2
    nfp

    Returns
    -------

    """
    fig, ax = plt.subplots()
    patches = []
    polygon = Polygon(shape1.polygon, True)
    patches.append(polygon)
    polygon = Polygon(shape1.offset_polygon, True)
    patches.append(polygon)
    polygon = Polygon(shape2.polygon, True)
    patches.append(polygon)
    polygon = Polygon(shape2.offset_polygon, True)
    patches.append(polygon)
    polygon = Polygon(nfp, True)
    patches.append(polygon)

    face_colors = ('None', 'skyblue', 'None', 'skyblue', 'none')
    edge_colors = ('aqua', 'b', 'aqua', 'b', 'lime')

    p = PatchCollection(patches,
                        facecolors=face_colors,
                        edgecolors=edge_colors,
                        linewidths=2,
                        alpha=0.4)
    ax.add_collection(p)

    x_min = min(min(p[0] for p in shape1.offset_polygon),
                min(p[0] for p in shape2.offset_polygon),
                min(p[0] for p in nfp))
    x_max = max(max(p[0] for p in shape1.offset_polygon),
                max(p[0] for p in shape2.offset_polygon),
                max(p[0] for p in nfp))
    y_min = min(min(p[1] for p in shape1.offset_polygon),
                min(p[1] for p in shape2.offset_polygon),
                min(p[1] for p in nfp))
    y_max = max(max(p[1] for p in shape1.offset_polygon),
                max(p[1] for p in shape2.offset_polygon),
                max(p[1] for p in nfp))
    plt.xlim([x_min, x_max])
    plt.ylim([y_min, y_max])

    plt.show()
    return


def draw_two_polygons(polygons1, polygons2):
    fig, ax = plt.subplots()
    patches = []
    face_colors = []
    edge_colors = []
    line_widths = []

    for base_polygon in polygons1:
        polygon = Polygon(base_polygon)
        face_colors.append('none')
        edge_colors.append('purple')
        line_widths.append(1)
        patches.append(polygon)

    for base_polygon in polygons2:
        polygon = Polygon(base_polygon)
        face_colors.append('none')
        edge_colors.append('red')
        line_widths.append(1)
        patches.append(polygon)

    p = PatchCollection(patches,
                        facecolors=face_colors,
                        edgecolors=edge_colors,
                        linewidths=line_widths,
                        alpha=0.4)

    x_min = min(min(p[0] for polygon in polygons1 for p in polygon),
                min(p[0] for polygon in polygons2 for p in polygon))
    y_min = min(min(p[1] for polygon in polygons1 for p in polygon),
                min(p[1] for polygon in polygons2 for p in polygon))
    x_max = max(max(p[0] for polygon in polygons1 for p in polygon),
                max(p[0] for polygon in polygons2 for p in polygon))
    y_max = max(max(p[1] for polygon in polygons1 for p in polygon),
                max(p[1] for polygon in polygons2 for p in polygon))

    ax.add_collection(p)
    fig.tight_layout()

    plt.xlim([x_min, x_max])
    plt.ylim([y_min, y_max])

    plt.show()
    return


def draw_iteration(problem, ifp, nfp, base_subject, current_polygons,
                   next_polygon, out_iter, inner_iter, add_str, batch_id):
    """
    画一次算法迭代中的状态，用于debug
    pyclipper很多操作返回的是三维数据，需要加判断。
    Parameters
    ----------
    problem
    ifp: 形状相对于面料的可行域
    nfp: 形状相当于某个已放置形状的nfp
    base_subject: 面料减去已放置形状的可行域
    current_polygons: 当前已放置的形状
    next_polygon: 下一个要放置的形状
    out_iter
    inner_iter
    add_str
    batch_id

    Returns
    -------

    """
    fig, ax = plt.subplots()
    patches = []
    face_colors = []
    edge_colors = []
    line_widths = []
    if isinstance(base_subject[0][0], numbers.Number):
        polygon = Polygon(base_subject)
        face_colors.append('none')
        edge_colors.append('purple')
        line_widths.append(1)
        patches.append(polygon)
    else:
        for base_polygon in base_subject:
            polygon = Polygon(base_polygon)
            face_colors.append('none')
            edge_colors.append('purple')
            line_widths.append(1)
            patches.append(polygon)
    if isinstance(ifp[0][0], numbers.Number):
        polygon = Polygon(ifp)
        face_colors.append('none')
        edge_colors.append('red')
        line_widths.append(5)
        patches.append(polygon)
    else:
        for each_ifp in ifp:
            polygon = Polygon(each_ifp)
            face_colors.append('none')
            edge_colors.append('red')
            line_widths.append(5)
            patches.append(polygon)
    if isinstance(nfp[0][0], numbers.Number):
        polygon = Polygon(nfp)
        face_colors.append('none')
        edge_colors.append('lime')
        line_widths.append(3)
        patches.append(polygon)
    else:
        for each_nfp in nfp:
            polygon = Polygon(each_nfp)
            face_colors.append('none')
            edge_colors.append('lime')
            line_widths.append(3)
            patches.append(polygon)

    for (key, rotation), positioned_polygon in current_polygons.items():
        polygon = Polygon(positioned_polygon)
        face_colors.append('lightcyan')
        edge_colors.append('skyblue')
        line_widths.append(3)
        patches.append(polygon)
        mean_x = sum(point[0] for point in positioned_polygon) / len(positioned_polygon)
        mean_y = sum(point[1] for point in positioned_polygon) / len(positioned_polygon)
        plt.text(mean_x, mean_y, '{}_{}'.format(key, rotation))

    polygon = Polygon(next_polygon)
    face_colors.append('lightpink')
    edge_colors.append('pink')
    line_widths.append(1)
    patches.append(polygon)

    p = PatchCollection(patches,
                        facecolors=face_colors,
                        edgecolors=edge_colors,
                        linewidths=line_widths,
                        alpha=0.4)
    ax.add_collection(p)

    ax.set_xlim([-2000, problem.material.height + 4000])
    ax.set_ylim([-2000, problem.material.height])
    # ax.axis('off')

    fig.tight_layout()

    plt.show()
    fig.savefig(
        os.path.join(
            os.getcwd(), 'figure', 'iter',
            '{}_construct_{}_{}_{}.pdf'.format(batch_id, out_iter, inner_iter,
                                               add_str)))
    fig.savefig(
        os.path.join(
            os.getcwd(), 'figure', 'iter',
            '{}_construct_{}_{}_{}.png'.format(batch_id, out_iter, inner_iter,
                                               add_str)))
    return


def draw_result(problem: Problem, objective, positions, file_name):
    """
    输出最终放置结果。
    Parameters
    ----------
    problem
    objective
    positions
    file_name

    Returns
    -------

    """
    width = objective
    fig, ax = plt.subplots()
    patches = []
    face_colors = []
    edge_colors = []
    # 画边框
    material_polygon = problem.material.get_polygon(width)
    if isinstance(material_polygon[0][0], numbers.Number):
        polygon = Polygon(material_polygon)
        face_colors.append('none')
        edge_colors.append('purple')
        patches.append(polygon)
    else:
        for each_material_polygon in material_polygon:
            polygon = Polygon(each_material_polygon)
            face_colors.append('none')
            edge_colors.append('purple')
            patches.append(polygon)
    # 画边际线
    margin_polygon = problem.material.get_margin_polygon(width)
    if isinstance(margin_polygon[0][0], numbers.Number):
        polygon = Polygon(margin_polygon)
        face_colors.append('none')
        edge_colors.append('red')
        patches.append(polygon)
    else:
        for each_margin_polygon in margin_polygon:
            polygon = Polygon(each_margin_polygon)
            face_colors.append('none')
            edge_colors.append('red')
            patches.append(polygon)
    # 画形状
    for key, (rotation, position) in positions.items():
        shape = problem.shapes[key][rotation]
        outline = shape.generate_positioned_polygon_output(position)
        polygon = Polygon(outline)
        face_colors.append('aqua')
        edge_colors.append('skyblue')
        patches.append(polygon)

    p = PatchCollection(patches,
                        facecolors=face_colors,
                        edgecolors=edge_colors,
                        linewidths=1,
                        alpha=0.4)
    ax.add_collection(p)

    # ax.axis('equal')

    ax.set_xlim([0, width])
    ax.set_ylim([0, problem.material.height])
    # ax.axis('off')

    fig.tight_layout()

    plt.show()
    fig.savefig(file_name)

    return

from domain.problem import Material, Shape

import numbers
from pprint import pprint
from typing import List

import pyclipper
from shapely.geometry import MultiPoint


def generate_nfp(polygon1, polygon2):
    # result = pyclipper.MinkowskiDiff(polygon1, polygon2)[0]
    # print('origin nfp len: {}'.format(len(result)))
    # result = pyclipper.SimplifyPolygon(result)[0]
    # print('simplify nfp len: {}'.format(len(result)))
    # result = pyclipper.CleanPolygon(result, 1.01)
    # print('clean nfp len: {}'.format(len(result)))
    nfp = pyclipper.CleanPolygons(pyclipper.SimplifyPolygons(pyclipper.MinkowskiDiff(polygon1, polygon2)), 1.20)
    return _clear_2d_list(nfp)


def generate_ifp(material: Material, shape: Shape, spacing):
    """
    生成布料内部的可行区域。

    Parameters
    ----------
    material
    shape
    spacing

    Returns
    -------

    """
    min_x = material.margin - shape.min_x - spacing
    min_y = material.margin - shape.min_y - spacing
    max_x = material.width - material.margin - (shape.max_x - shape.min_x)
    max_y = material.height - material.margin - (shape.max_y - shape.min_y)
    return [[min_x, min_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]]


def intersect_polygons(polygon1, polygon2):
    pc = pyclipper.Pyclipper()
    pc.AddPath(polygon1, pyclipper.PT_CLIP, True)
    if isinstance(polygon2[0][0], numbers.Number):
        pc.AddPath(polygon2, pyclipper.PT_SUBJECT, True)
    else:
        pc.AddPaths(polygon2, pyclipper.PT_SUBJECT, True)
    return pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)


def diff_ifp_nfps(ifp, nfp):
    """
    ifp和nfp的差集。
    Parameters
    ----------
    ifp
    nfp

    Returns
    -------

    """
    ifp = _clear_2d_list(ifp)
    nfp = _clear_2d_list(nfp)
    pc = pyclipper.Pyclipper()
    if isinstance(ifp[0][0], numbers.Number):
        pc.AddPath(ifp, pyclipper.PT_SUBJECT, True)
    else:
        pc.AddPaths(ifp, pyclipper.PT_SUBJECT, True)
    if isinstance(nfp[0][0], numbers.Number):
        pc.AddPath(nfp, pyclipper.PT_CLIP, True)
    else:
        pc_temp = pyclipper.Pyclipper()

        pc_temp.AddPaths(nfp, pyclipper.PT_SUBJECT, True)

        union_nfp = pc_temp.Execute(pyclipper.CT_UNION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
        # 此处保守起见，取了NFP并集的凸包
        # temp_union_nfp = union_nfp[0]
        # for i in range(1, len(union_nfp)):
        #     temp_union_nfp += union_nfp[i]
        # convex_polygon = MultiPoint(temp_union_nfp).convex_hull
        # convex_polygon = [[int(node[0]), int(node[1])] for node in list(convex_polygon.exterior.coords)]
        #
        # pc.AddPath(convex_polygon, pyclipper.PT_CLIP, True)

        # TODO 只去除NFP并集中的孔洞，允许形状为非凸
        union_polygon_without_holes = [each_union_nfp for each_union_nfp in union_nfp
                                       if pyclipper.Orientation(each_union_nfp)]
        pc.AddPaths(union_polygon_without_holes, pyclipper.PT_CLIP, True)
    result = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    return result


def _clear_2d_list(_2d_list: List[List[float]]):
    """
    去掉CleanPolygons后出现的一些空list
    Parameters
    ----------
    _2d_list

    Returns
    -------

    """
    _2d_list = [_1d_list for _1d_list in _2d_list if len(_1d_list) > 0]
    return _2d_list


def _is_ifp_nfp_rectangle_distant(ifp, nfp) -> bool:
    """
    判断ifp和nfp的外围矩形是否不相交。
    Parameters
    ----------
    ifp
    nfp

    Returns
    -------

    """
    if isinstance(ifp[0][0], numbers.Number):
        ifp_min_x = min(node[0] for node in ifp)
        ifp_min_y = min(node[1] for node in ifp)
        ifp_max_x = max(node[0] for node in ifp)
        ifp_max_y = max(node[1] for node in ifp)
    else:
        ifp_min_x = min(node[0] for each_ifp in ifp for node in each_ifp)
        ifp_min_y = min(node[1] for each_ifp in ifp for node in each_ifp)
        ifp_max_x = max(node[0] for each_ifp in ifp for node in each_ifp)
        ifp_max_y = max(node[1] for each_ifp in ifp for node in each_ifp)
    if isinstance(nfp[0][0], numbers.Number):
        nfp_min_x = min(node[0] for node in nfp)
        nfp_min_y = min(node[1] for node in nfp)
        nfp_max_x = max(node[0] for node in nfp)
        nfp_max_y = max(node[1] for node in nfp)
    else:
        nfp_min_x = min(node[0] for each_nfp in nfp for node in each_nfp)
        nfp_min_y = min(node[1] for each_nfp in nfp for node in each_nfp)
        nfp_max_x = max(node[0] for each_nfp in nfp for node in each_nfp)
        nfp_max_y = max(node[1] for each_nfp in nfp for node in each_nfp)
    return (nfp_max_x < ifp_min_x and nfp_max_y < ifp_min_y) or (nfp_min_x > ifp_max_x and nfp_min_y > ifp_max_y)


def intersection():
    ifp = [[0, 0], [20, 0], [20, 20], [0, 20]]
    nfp = [[10, 10], [30, 10], [30, 30], [10, 30]]
    result = diff_ifp_nfps(ifp, nfp)
    pprint(result)


if __name__ == '__main__':
    # poly2 = [[0, 0], [10, 0], [10, 10], [0, 10]]
    # poly1 = [[5, 5], [15, 5], [11, 15]]
    # # pprint(generate_nfp(poly1, poly2))
    #
    # rec_width = 100
    # rec_height = 100
    #
    # polygon_min_x = 10
    # polygon_min_y = 10
    # polygon_max_x = 20
    # polygon_max_y = 20
    #
    # # pprint(generate_ifp(rec_width, rec_height, polygon_min_x, polygon_min_y, polygon_max_x, polygon_max_y))
    #
    # nfp_list = list()
    # nfp_list.append(poly1)
    # nfp_list.append(poly2)
    #
    # temp_ifp = generate_ifp(rec_width, rec_height, polygon_min_x, polygon_min_y, polygon_max_x, polygon_max_y)
    # pprint(intersect_ifp_nfps(temp_ifp, nfp_list))

    intersection()

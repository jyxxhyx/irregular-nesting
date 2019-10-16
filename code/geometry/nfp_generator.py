from domain.problem import Material, Shape

import logging
import numbers
from pprint import pprint
from typing import List
import multiprocessing

import pyclipper
from shapely.geometry import MultiPoint


def generate_nfp(polygon1, polygon2, config_clipper):
    logger = logging.getLogger(__name__)
    result = pyclipper.MinkowskiDiff(polygon1, polygon2)
    logger.debug('Origin nfp size: {}'.format(
        sum(len(element) for element in result)))
    result = pyclipper.SimplifyPolygons(result)
    logger.debug('Simplify nfp size: {}'.format(
        sum(len(element) for element in result)))
    result = pyclipper.CleanPolygons(result, config_clipper['precision'])
    logger.debug('Clean nfp size: {}'.format(
        sum(len(element) for element in result)))
    # result = pyclipper.CleanPolygons(pyclipper.SimplifyPolygons(pyclipper.MinkowskiDiff(polygon1, polygon2)), 1.20)
    return _clean_empty_element_nested_list(result)


def generate_nfp_pool(info):
    polygon1 = info['polygon1']
    polygon2 = info['polygon2']
    shape1_str = info['shape1_str']
    shape2_str = info['shape2_str']
    precision = info['precision']

    logger = logging.getLogger(__name__)
    result = pyclipper.CleanPolygons(
        pyclipper.SimplifyPolygons(pyclipper.MinkowskiDiff(polygon1,
                                                           polygon2)), precision)
    result = _clean_empty_element_nested_list(result)
    # logger.info('{}-{}'.format(shape1_str, shape2_str))
    return result, shape1_str, shape2_str


def generate_ifp(material: Material, shape: Shape):
    """
    生成布料内部的可行区域。

    Parameters
    ----------
    material
    shape

    Returns
    -------

    """
    min_x = material.margin - shape.min_x
    min_y = material.margin - shape.min_y
    max_x = material.width - material.margin - (shape.max_x - shape.min_x)
    max_y = material.height - material.margin - (shape.max_y - shape.min_y)
    return [[[min_x, min_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]]]


def intersect_polygons(polygon1, polygon2):
    pc = pyclipper.Pyclipper()
    pc.AddPath(polygon1, pyclipper.PT_CLIP, True)
    if isinstance(polygon2[0][0], numbers.Number):
        pc.AddPath(polygon2, pyclipper.PT_SUBJECT, True)
    else:
        pc.AddPaths(polygon2, pyclipper.PT_SUBJECT, True)
    return pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD,
                      pyclipper.PFT_EVENODD)


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
    ifp = _clean_empty_element_nested_list(ifp)
    nfp = _clean_empty_element_nested_list(nfp)
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

        union_nfp = pc_temp.Execute(pyclipper.CT_UNION, pyclipper.PFT_EVENODD,
                                    pyclipper.PFT_EVENODD)

        # 只去除NFP并集中的孔洞，允许形状为非凸
        union_polygon_without_holes = [
            each_union_nfp for each_union_nfp in union_nfp
            if pyclipper.Orientation(each_union_nfp)
        ]
        pc.AddPaths(union_polygon_without_holes, pyclipper.PT_CLIP, True)
    result = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD,
                        pyclipper.PFT_EVENODD)
    return result


def _clean_empty_element_nested_list(nested_list: List[List[float]]):
    """
    去掉CleanPolygons后出现的一些空list
    Parameters
    ----------
    nested_list

    Returns
    -------

    """
    nested_list = [element for element in nested_list if len(element) > 0]
    return nested_list

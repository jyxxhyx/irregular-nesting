from domain.problem import Problem

from random import random
from bisect import bisect_right
import numpy as np
import logging


def polygon_area_descending(problem: Problem):
    """
    按照多边形面积降序排列
    Parameters
    ----------
    problem

    Returns
    -------

    """
    return [idx for idx, _ in sorted(enumerate(problem.shapes), key=lambda value: value[1].area, reverse=True)]


def offset_polygon_area_descending(problem: Problem):
    """
    按照外延多边形面积降序排列
    Parameters
    ----------
    problem

    Returns
    -------

    """
    return [idx for idx, _ in sorted(enumerate(problem.shapes), key=lambda value: value[1].calculate_offset_area(),
                                     reverse=True)]


def offset_polygon_width_descending(problem: Problem):
    """
    按照外延多边形长度降序排列
    Parameters
    ----------
    problem

    Returns
    -------

    """
    return [idx for idx, _ in sorted(enumerate(problem.shapes), key=lambda value: value[1].calculate_offset_width(),
                                     reverse=True)]


def rectangular_area_descending(problem: Problem):
    """
    按照最小覆盖长方形（不考虑旋转）面积降序排列
    Parameters
    ----------
    problem

    Returns
    -------

    """
    return [idx for idx, _ in sorted(enumerate(problem.shapes), key=lambda value: value[1].calculate_rectangular_area(),
                                     reverse=True)]


def rectangular_diagonal_descending(problem: Problem):
    """
    按照最小覆盖长方形（不考虑旋转）面积降序排列
    Parameters
    ----------
    problem

    Returns
    -------

    """
    return [idx for idx, _ in sorted(enumerate(problem.shapes), key=lambda value: value[1].calculate_diagonal_len(),
                                     reverse=True)]


def sampling_based_on_offset_polygon_area_square(problem: Problem):
    """
    按照外延多边形面积平方作为权重，抽样得到一个序列
    Parameters
    ----------
    problem

    Returns
    -------

    """
    return weighted_shuffle([shape.calculate_offset_area() ** 2 for shape in problem.shapes])


def weighted_shuffle(weight):
    """
    带权重的洗牌，
    参考http://nicky.vanforeest.com/probability/weightedRandomShuffling/weighted.html
    Parameters
    ----------
    weight

    Returns
    -------

    """
    logger = logging.getLogger(__name__)
    indices = np.arange(len(weight))
    result = np.empty_like(indices)
    cum_weights = np.cumsum(weight)
    for i in range(len(weight)):
        rnd = random() * cum_weights[-1]
        j = bisect_right(cum_weights, rnd)
        result[i] = indices[j]
        cum_weights[j:] -= weight[j]
    logger.debug(result)
    return result

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
    return [
        key for key, _ in sorted(problem.shapes.items(),
                                 key=lambda item: item[1][0].area,
                                 reverse=True)
    ]


def offset_polygon_area_descending(problem: Problem):
    """
    按照外延多边形面积降序排列
    Parameters
    ----------
    problem

    Returns
    -------

    """
    return [
        key for key, _ in sorted(
            problem.shapes.items(),
            key=lambda item: item[1][0].calculate_offset_area(),
            reverse=True)
    ]


def offset_polygon_width_descending(problem: Problem):
    """
    按照外延多边形长度降序排列
    Parameters
    ----------
    problem

    Returns
    -------

    """
    return [
        key for key, _ in sorted(
            problem.shapes.items(),
            key=lambda item: item[1][0].calculate_offset_width(),
            reverse=True)
    ]


def rectangular_residual_area_descending(problem: Problem, weight=0.5):
    """
    按照（weight * 最小覆盖长方形面积 + (1 - weight) * 外延多边形面积）降序排列
    Parameters
    ----------
    problem
    weight

    Returns
    -------

    """
    return [
        key for key, _ in sorted(
            problem.shapes.items(),
            key=lambda item: (weight * item[1][0].calculate_rectangular_area(
            ) + (1 - weight) * item[1][0].calculate_offset_area()),
            reverse=True)
    ]


def rectangular_area_descending(problem: Problem):
    """
    按照最小覆盖长方形（不考虑旋转）面积降序排列
    Parameters
    ----------
    problem

    Returns
    -------

    """
    return [
        key for key, _ in sorted(
            problem.shapes.items(),
            key=lambda item: item[1][0].calculate_rectangular_area(),
            reverse=True)
    ]


def rectangular_diagonal_descending(problem: Problem):
    """
    按照最小覆盖长方形（不考虑旋转）面积降序排列
    Parameters
    ----------
    problem

    Returns
    -------

    """
    return [
        key for key, _ in sorted(
            problem.shapes.items(),
            key=lambda item: item[1][0].calculate_diagonal_len(),
            reverse=True)
    ]

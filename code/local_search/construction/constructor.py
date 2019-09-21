from domain.problem import Problem


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

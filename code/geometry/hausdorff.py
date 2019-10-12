import functools
import sys


def hausdorff_list(x_a, x_b):
    n_a = len(x_a)
    n_b = len(x_b)
    c_max = 0
    c_max = _sub_hausdorff(x_a, x_b, c_max)
    c_max = _sub_hausdorff(x_b, x_a, c_max)
    return c_max


def _sub_hausdorff(x_a, x_b, c_max):
    for i in x_a:
        c_min = sys.maxsize
        for j in x_b:
            d = distance_function_list(i[0], i[1], j[0], j[1])
            if d < c_min:
                c_min = d
            if c_min < c_max:
                break
        if c_max < c_min < sys.maxsize:
            c_max = c_min
    return c_max


@functools.lru_cache(maxsize=1000000)
def distance_function_list(x1, y1, x2, y2):
    return abs(x2 - x1) + abs(y2 - y1)

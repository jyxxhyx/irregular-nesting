def rotate_180(polygon):
    rotate_polygon = [[-point[0], -point[1]] for point in polygon]
    return rotate_polygon


def rotate_180_3d(polygons):
    return [[[-point[0], -point[1]] for point in single_polygon]
            for single_polygon in polygons]


def rotate_180_shift_3d(polygons, shift_x, shift_y):
    return [[[-point[0] + shift_x, -point[1] + shift_y]
             for point in single_polygon] for single_polygon in polygons]


def change_degree(rotate):
    if rotate == 180:
        return 0
    elif rotate == 0:
        return 180

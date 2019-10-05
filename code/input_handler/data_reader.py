import numpy

from domain.problem import Shape, Material, Problem
from domain.material import Hole

import ast
import csv
import sys
from typing import List, Tuple

import pyclipper


def read_shapes_from_csv(file_name, spacing, scale: int = 1, max_shape_len: int = sys.maxsize):
    shape_list = list()
    with open(file_name, encoding='utf-8') as csv_file:
        contents = csv.reader(csv_file)
        header = next(contents, None)
        for row in contents:
            batch_id: str = row[0]
            shape_id: str = row[1]
            shape_num: int = int(row[2])
            # Nested list version
            shape_polygon: List[List[float]] = ast.literal_eval(row[3])
            shape_polygon = [[node[0] * scale, node[1] * scale] for node in shape_polygon]
            # Numpy version
            # shape_polygon = numpy.array(ast.literal_eval(row[3])) * scale
            # shape_polygon = [[node[0] * scale, node[1] * scale] for node in shape_polygon]

            shape_rotations: Tuple[int] = ast.literal_eval(row[4])
            material_id: str = row[5]
            # 保证所有多边形的坐标都是逆时针方向的
            if not pyclipper.Orientation(shape_polygon):
                shape = Shape(shape_id, shape_num, list(reversed(shape_polygon)), shape_rotations, batch_id,
                              material_id)
            else:
                shape = Shape(shape_id, shape_num, shape_polygon, shape_rotations, batch_id, material_id)

            # TODO 生成外延多边形的options：矩形，凸包，和实际的offset_polygon。矩形的浪费太多，结果不可行，
            #  实际offset_polygon算出来的结果局部还有问题，目前用凸包的方案
            shape.generate_offset_polygon(spacing)
            # shape.generate_convex_offset_polygon(spacing)
            # shape.generate_offset_rectangular(spacing)

            shape_list.append(shape)

            # 设置读取数量上限（debug时候会用到）
            if len(shape_list) > max_shape_len:
                break
    return shape_list


def read_material_from_csv(file_name, scale=1):
    with open(file_name, encoding='utf-8') as csv_file:
        contents = csv.reader(csv_file)
        header = next(contents, None)
        row_material = next(contents, None)
        material_id = row_material[0]
        area = row_material[1].split('*')
        width = int(area[0]) * scale
        height = int(area[1]) * scale
        holes = None
        if row_material[2]:
            holes = list()
            contents_holes = ast.literal_eval(row_material[2])
            for each_hole in contents_holes:
                coordinates = [each_hole[0][0] * scale, each_hole[0][1] * scale]
                hole = Hole(coordinates, each_hole[1] * scale)
                holes.append(hole)
        spacing = int(row_material[3]) * scale
        margin = int(row_material[4]) * scale
        material = Material(material_id, height, width, spacing, margin, holes)
    return material

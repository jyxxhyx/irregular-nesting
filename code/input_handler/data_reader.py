from domain.problem import Shape, Material, Problem

import ast
import csv
import sys
from typing import List, Tuple

import pyclipper


def read_shapes_from_csv(file_name, spacing, max_shape_len: int = sys.maxsize):
    shape_list = list()
    with open(file_name, encoding='utf-8') as csv_file:
        contents = csv.reader(csv_file)
        header = next(contents, None)
        for row in contents:
            batch_id: str = row[0]
            shape_id: str = row[1]
            shape_num: int = int(row[2])
            shape_polygon: List[List[float]] = ast.literal_eval(row[3])
            shape_rotations: Tuple[int] = ast.literal_eval(row[4])
            material_id: str = row[5]
            # 保证所有多边形的坐标都是逆时针方向的
            if not pyclipper.Orientation(shape_polygon):
                shape = Shape(shape_id, shape_num, list(reversed(shape_polygon)), shape_rotations, batch_id, material_id)
            else:
                shape = Shape(shape_id, shape_num, shape_polygon, shape_rotations, batch_id, material_id)

            # TODO 生成外延多边形的options：矩形，凸包，和实际的offset_polygon。矩形的浪费太多，结果不可行，
            #  实际offset_polygon算出来的结果局部还有问题，目前用凸包的方案
            # shape.generate_offset_polygon(spacing)
            shape.generate_convex_offset_polygon(spacing)
            # shape.generate_offset_rectangular(spacing)

            shape_list.append(shape)

            # 设置读取数量上限（debug时候会用到）
            if len(shape_list) > max_shape_len:
                break
    return shape_list


def read_material_from_csv(file_name):
    with open(file_name, encoding='utf-8') as csv_file:
        contents = csv.reader(csv_file)
        header = next(contents, None)
        row_material = next(contents, None)
        material_id = row_material[0]
        area = row_material[1].split('*')
        width = int(area[0])
        height = int(area[1])
        hole = None
        if row_material[2]:
            hole = None
        spacing = int(row_material[3])
        margin = int(row_material[4])
        material = Material(material_id, height, width, spacing, margin, hole)
    return material

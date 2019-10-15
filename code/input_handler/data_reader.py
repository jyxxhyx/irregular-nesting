from collections import OrderedDict

import numpy

from domain.problem import Shape, Material, Problem
from domain.material import Hole
from geometry.rotate import rotate_180

import ast
import csv
import sys
from typing import List, Tuple, Dict

import pyclipper


def read_shapes_from_csv(file_name,
                         spacing,
                         config,
                         scale: int = 1,
                         max_shape_len: int = sys.maxsize) -> Tuple[Dict[str, Dict[int, Shape]], str]:
    shape_dict: OrderedDict[str, Dict[int, Shape]] = OrderedDict()
    with open(file_name, encoding='utf-8') as csv_file:
        contents = csv.reader(csv_file)
        header = next(contents, None)
        for row in contents:
            batch_id: str = row[0]
            shape_id: str = row[1]
            shape_num: int = int(row[2])
            # Nested list version
            shape_polygon: List[List[float]] = ast.literal_eval(row[3])
            shape_polygon = [[node[0] * scale, node[1] * scale]
                             for node in shape_polygon]
            # Numpy version
            # shape_polygon = numpy.array(ast.literal_eval(row[3])) * scale
            # shape_polygon = [[node[0] * scale, node[1] * scale] for node in shape_polygon]

            shape_rotations: Tuple[int] = ast.literal_eval(row[4])
            material_id: str = row[5]
            shape_dict[shape_id] = dict()
            # 保证所有多边形的坐标都是逆时针方向的
            if 0 in shape_rotations:
                if not pyclipper.Orientation(shape_polygon):
                    shape = Shape(shape_id, shape_num,
                                  list(reversed(shape_polygon)),
                                  batch_id, material_id, rotate_degree=0)
                else:
                    shape = Shape(shape_id, shape_num, shape_polygon,
                                  batch_id, material_id, rotate_degree=0)

                shape.generate_offset_polygon(
                    spacing,
                    meter_limit=config['clipper']['meter_limit'],
                    arc_tolerance=config['clipper']['arc_tolerance'],
                    precision=config['clipper']['precision'])
                # shape.generate_convex_offset_polygon(spacing)
                # shape.generate_offset_rectangular(spacing)

                shape_dict[shape_id][0] = shape

            # if 180 in shape_rotations:
            #     if not pyclipper.Orientation(shape_polygon):
            #         shape = Shape(shape_id, shape_num,
            #                       rotate_180(list(reversed(shape_polygon))),
            #                       batch_id, material_id, rotate_degree=180)
            #     else:
            #         shape = Shape(shape_id, shape_num, rotate_180(shape_polygon),
            #                       batch_id, material_id, rotate_degree=180)
            #
            #     shape.generate_offset_polygon(
            #         spacing,
            #         meter_limit=config['clipper']['meter_limit'],
            #         arc_tolerance=config['clipper']['arc_tolerance'],
            #         precision=config['clipper']['precision'])
            #     # shape.generate_convex_offset_polygon(spacing)
            #     # shape.generate_offset_rectangular(spacing)
            #
            #     shape_dict[shape_id][180] = shape

            # 设置读取数量上限（debug时候会用到）
            if len(shape_dict) > max_shape_len:
                break
    return shape_dict, batch_id


def read_material_from_csv(file_name, scale=1):
    with open(file_name, encoding='utf-8') as csv_file:
        contents = csv.reader(csv_file)
        header = next(contents, None)
        row_material = next(contents, None)
        material_id = row_material[0]
        area = row_material[1].split('*')
        width = int(area[0]) * scale
        height = int(area[1]) * scale
        holes = list()
        if row_material[2]:
            contents_holes = ast.literal_eval(row_material[2])
            for index, each_hole in enumerate(contents_holes):
                coordinates = [
                    each_hole[0][0] * scale, each_hole[0][1] * scale
                ]
                hole = Hole('hole{}'.format(index), coordinates, each_hole[1] * scale)
                holes.append(hole)
        spacing = int(row_material[3]) * scale
        margin = int(row_material[4]) * scale
        material = Material(material_id, height, width, spacing, margin, holes)
    return material

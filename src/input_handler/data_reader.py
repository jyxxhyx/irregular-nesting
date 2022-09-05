from src.domain.problem import Shape, Material, Problem
from src.domain.material import Hole, IrregularMaterial
from src.geometry.rotate import rotate_180

import ast
from collections import OrderedDict
import csv
import sys
from typing import List, Tuple, Dict

import pyclipper


def read_shapes_from_csv(file_name,
                         spacing,
                         config,
                         scale: int = 1,
                         max_shape_len: int = sys.maxsize
                         ) -> Tuple[Dict[str, Dict[int, Shape]], str]:
    shape_dict: OrderedDict[str, Dict[int, Shape]] = OrderedDict()
    with open(file_name, encoding='utf-8') as csv_file:
        contents = csv.reader(csv_file)
        header = next(contents, None)
        for row in contents:
            batch_id: str = row[0]
            shape_id: str = row[1]
            shape_num: int = int(row[2])

            shape_polygon: List[List[float]] = ast.literal_eval(row[3])
            shape_polygon = [[node[0] * scale, node[1] * scale]
                             for node in shape_polygon]

            shape_rotations: Tuple[int] = ast.literal_eval(row[4])
            material_id: str = row[5]
            shape_dict[shape_id] = dict()

            if 0 in shape_rotations:
                shape_dict[shape_id][0] = _construct_shape(
                    shape_id, shape_num, shape_polygon, batch_id, material_id,
                    spacing, config, 0, is_normalize=True)

            if 180 in shape_rotations:
                shape_dict[shape_id][180] = _construct_shape(
                    shape_id, shape_num, rotate_180(shape_polygon), batch_id,
                    material_id, spacing, config, 180, is_normalize=True)

            # 设置读取数量上限（debug时候会用到）
            if len(shape_dict) > max_shape_len:
                break
    return shape_dict, batch_id


def read_material_from_csv(file_name, scale=1, is_hole_circle=True):
    with open(file_name, encoding='utf-8') as csv_file:
        contents = csv.reader(csv_file)
        header = next(contents, None)
        row_material = next(contents, None)
        material_id = row_material[0]
        is_regular = True
        shape_polygon = []
        if '*' in row_material[1]:
            area = row_material[1].split('*')
            width = int(area[0]) * scale
            height = int(area[1]) * scale
        else:
            is_regular = False
            shape_polygon = ast.literal_eval(row_material[1])
            shape_polygon = [[node[0] * scale, node[1] * scale]
                             for node in shape_polygon]
            pass
        holes = list()
        if row_material[2]:
            contents_holes = ast.literal_eval(row_material[2])
            for index, each_hole in enumerate(contents_holes):
                if is_hole_circle:
                    coordinates = [
                        each_hole[0][0] * scale, each_hole[0][1] * scale
                    ]
                    hole = Hole('hole{}'.format(index), coordinates,
                                each_hole[1] * scale)
                    holes.append(hole)
                else:
                    polygon = [[point[0] * scale, point[1] * scale] for point in each_hole]
                    hole = Hole('hole{}'.format(index), list(), 0, offset_polygon=polygon)
                    holes.append(hole)

        spacing = int(row_material[3]) * scale
        margin = int(row_material[4]) * scale
        if is_regular:
            material = Material(material_id, height, width, spacing, margin, holes)
        else:
            material = IrregularMaterial(material_id, shape_polygon, spacing, margin, holes)
    return material


def _construct_shape(shape_id, shape_num, shape_polygon, batch_id, material_id,
                     spacing, config, rotate_degree, is_normalize=True) -> Shape:
    # 保证所有多边形的坐标都是逆时针方向的
    if not pyclipper.Orientation(shape_polygon):
        shape = Shape(shape_id,
                      shape_num,
                      list(reversed(shape_polygon)),
                      batch_id,
                      material_id,
                      rotate_degree=rotate_degree, is_normalize=is_normalize)
    else:
        shape = Shape(shape_id,
                      shape_num,
                      shape_polygon,
                      batch_id,
                      material_id,
                      rotate_degree=rotate_degree, is_normalize=is_normalize)

    shape.generate_offset_polygon(
        spacing,
        meter_limit=config['clipper']['meter_limit'],
        arc_tolerance=config['clipper']['arc_tolerance'],
        precision=config['clipper']['precision'])

    return shape

from collections import namedtuple
import math
from pprint import pprint

import numpy
import pyclipper
from shapely.geometry import MultiPoint

Position = namedtuple('pos', ['x', 'y'])


class Shape:
    def __init__(self, shape_id, count, polygon, batch_id,
                 material_id, rotate_degree):
        """

        Parameters
        ----------
        shape_id
        count
        polygon：外轮廓坐标，需要逆时针方向提供
        rotate_degree
        batch_id
        material_id
        """
        self.shape_id = shape_id
        self.count = count
        self.polygon = polygon
        self.batch_id = batch_id
        self.material_id = material_id
        self.rotate_degree = rotate_degree
        self.offset_polygon = list()
        self.area = self.calculate_origin_area()
        self._calculate_extreme_values()
        self._normalize()
        self.similar_shape = self
        return

    def generate_offset_rectangular(self, offset):
        min_x = self.min_x - offset
        min_y = self.min_y - offset
        max_x = self.max_x + offset
        max_y = self.max_y + offset
        self.offset_polygon = [[min_x, min_y], [max_x, min_y], [max_x, max_y],
                               [min_x, max_y]]

    def generate_offset_polygon(self,
                                offset,
                                meter_limit=2,
                                arc_tolerance=0.25,
                                precision=1.20):
        """
        生成多边形的外延多边形（保证多边形之间的间距）。
        PyclipperOffset具体参数见如下链接：
        http://www.angusj.com/delphi/clipper/documentation/Docs/Units/ClipperLib/Classes/ClipperOffset/Properties/ArcTolerance.htm
        http://www.angusj.com/delphi/clipper/documentation/Docs/Units/ClipperLib/Classes/ClipperOffset/Properties/MiterLimit.htm
        Parameters
        ----------
        offset
        meter_limit
        arc_tolerance:
        precision

        Returns
        -------

        """
        pco = pyclipper.PyclipperOffset(miter_limit=meter_limit,
                                        arc_tolerance=arc_tolerance)
        # pco.AddPath(pyclipper.scale_to_clipper(self.polygon, scale), pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
        pco.AddPath(self.polygon, pyclipper.JT_ROUND,
                    pyclipper.ET_CLOSEDPOLYGON)
        # TODO 考虑带孔零件的情况
        self.offset_polygon = pyclipper.CleanPolygon(
            pco.Execute(offset)[0], precision)
        # self.offset_polygon = numpy.array(pyclipper.CleanPolygon(pco.Execute(offset)[0], precision))
        # self.offset_polygon = pyclipper.scale_from_clipper(self.offset_polygon, scale)
        return

    def generate_convex_offset_polygon(self,
                                       offset,
                                       meter_limit=2,
                                       arc_tolerance=0.25,
                                       precision=1.20):
        pco = pyclipper.PyclipperOffset(miter_limit=meter_limit,
                                        arc_tolerance=arc_tolerance)
        convex_polygon = MultiPoint(self.polygon).convex_hull
        convex_polygon = [[node[0], node[1]]
                          for node in list(convex_polygon.exterior.coords)]
        # draw_simple_polygon(convex_polygon)
        # pco.AddPath(pyclipper.scale_to_clipper(convex_polygon, scale), pyclipper.JT_ROUND,
        #             pyclipper.ET_CLOSEDPOLYGON)
        pco.AddPath(convex_polygon, pyclipper.JT_ROUND,
                    pyclipper.ET_CLOSEDPOLYGON)
        self.offset_polygon = pyclipper.CleanPolygon(
            pco.Execute(offset)[0], precision)
        # self.offset_polygon = pyclipper.scale_from_clipper(self.offset_polygon, scale)
        return

    def calculate_origin_area(self):
        return pyclipper.Area(self.polygon)

    def calculate_offset_area(self):
        return pyclipper.Area(self.offset_polygon)

    def calculate_rectangular_area(self):
        return (self.max_x - self.min_x) * (self.max_y - self.min_y)

    def calculate_diagonal_len(self):
        return math.sqrt((self.max_x - self.min_x)**2 +
                         (self.max_y - self.min_y)**2)

    def calculate_offset_width(self):
        return self.max_x - self.min_x

    def generate_positioned_polygon_output(self, position: Position, scale=1):
        """
        输出结果时要用到，需要根据scale还原。
        Parameters
        ----------
        position
        scale

        Returns
        -------

        """
        return [[(x + position.x) / scale, (y + position.y) / scale]
                for x, y in self.polygon]

    def generate_positioned_offset_polygon(self, position: Position):
        return [[x + position.x, y + position.y]
                for x, y in self.offset_polygon]

    def _calculate_extreme_values(self):
        self.max_x = max(point[0] for point in self.polygon)
        self.min_x = min(point[0] for point in self.polygon)
        self.max_y = max(point[1] for point in self.polygon)
        self.min_y = min(point[1] for point in self.polygon)
        return

    def _normalize(self):
        """
        调整坐标，使得polygon的min_x和min_y为0，reference point在坐标原点
        Returns
        -------

        """
        self.polygon = [[p[0] - self.min_x, p[1] - self.min_y]
                        for p in self.polygon]
        self.max_x -= self.min_x
        self.max_y -= self.min_y
        self.min_x = 0
        self.min_y = 0
        return

    def __hash__(self):
        return self.__repr__().__hash__()

    def __repr__(self):
        return '{}_{}'.format(self.shape_id, self.rotate_degree)

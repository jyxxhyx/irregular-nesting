from typing import Union, List
import math


class Hole:
    def __init__(self, hole_id, center, radius):
        self.shape_id = hole_id
        self.center = center
        self.radius = radius
        self.offset_polygon = list()
        self.offset_vertices = 0
        self.rotate_degree = 0
        self.similar_shape = self
        self.max_x = 0
        self.max_y = 0
        return

    def approximate_regular_polygon(self, number_vertices: int, spacing: int):
        """
        用一个正多边形来近似瑕疵.
        具体计算如下：
        多边形两点夹角 alpha = 2 * pi / n
        多边形边长 r = radius / cos(alpha) + spacing
        顶点坐标为 [x_c + r * cos(k * alpha), y_c + r * sin(k * alpha)]

        Parameters
        ----------
        number_vertices: 多边形边数
        spacing: 空隙

        Returns
        -------

        """
        angle = math.pi * 2 / number_vertices
        self.offset_vertices = number_vertices
        regular_polygon_radius = self.radius / math.cos(angle) + spacing
        for i in range(number_vertices):
            self.offset_polygon.append([
                self.center[0] + regular_polygon_radius * math.cos(i * angle),
                self.center[1] + regular_polygon_radius * math.sin(i * angle)
            ])
        self.max_x = max(point[0] for point in self.offset_polygon)
        self.max_y = max(point[1] for point in self.offset_polygon)
        return

    def scaled_polygon(self, scale):
        polygon = list()
        angle = math.pi * 2 / self.offset_vertices
        regular_polygon_radius = self.radius / math.cos(angle) / scale
        for i in range(self.offset_vertices):
            polygon.append([
                self.center[0] / scale +
                regular_polygon_radius * math.cos(i * angle),
                self.center[1] / scale +
                regular_polygon_radius * math.sin(i * angle)
            ])
        return polygon

    def __repr__(self):
        return '{}_{}'.format(self.shape_id, self.rotate_degree)


class Material:
    def __init__(self,
                 material_id,
                 height,
                 width,
                 spacing,
                 margin,
                 holes: Union[List[Hole], None] = None):
        """

        Parameters
        ----------
        material_id:
            面料编号
        height:
            长度
        width:
            宽度
        spacing:
            零件间隙
        margin:
            边距
        holes:
            瑕疵
        """
        self.material_id = material_id
        self.height = height
        self.width = width
        self.holes = holes
        self.spacing = spacing
        self.margin = margin
        return

    def get_polygon(self, width):
        """
        以多边形形式返回布的形状，考虑了瑕疵.
        Parameters
        ----------
        width: 实际使用宽度

        Returns
        -------

        """
        outer_polygon = [[0, 0], [width, 0], [width, self.height],
                         [0, self.height]]
        if self.holes is None:
            return outer_polygon
        else:
            whole_polygon = list()
            whole_polygon.append(outer_polygon)

            for hole in self.holes:
                whole_polygon.append(hole.offset_polygon)
            return whole_polygon

    def get_margin_polygon(self, width):
        min_x = self.margin
        min_y = self.margin
        max_x = width - self.margin
        max_y = self.height - self.margin
        return [[min_x, min_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]]

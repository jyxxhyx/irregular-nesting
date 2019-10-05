from typing import Union, List
import math


class Hole:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        self.regular_polygon = list()
        return

    def approximate_regular_polygon(self, number_vertices: int, spacing: int):
        """
        用一个正多边形来近似破损的洞.
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
        regular_polygon_radius = self.radius / math.cos(angle) + spacing
        for i in range(number_vertices):
            self.regular_polygon.append([self.center[0] + regular_polygon_radius * math.cos(i * angle),
                                         self.center[1] + regular_polygon_radius * math.sin(i * angle)])
        return


class Material:
    def __init__(self, material_id, height, width, spacing, margin, holes: Union[List[Hole], None] = None):
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
        outer_polygon = [[0, 0], [width, 0], [width, self.height], [0, self.height]]
        if self.holes is None:
            return outer_polygon
        else:
            whole_polygon = list()
            whole_polygon.append(outer_polygon)
            # TODO 此函数是画图用的，可以考虑返回圆形
            for hole in self.holes:
                whole_polygon.append(hole.regular_polygon)
            return whole_polygon

    def get_margin_polygon(self, width):
        min_x = self.margin
        min_y = self.margin
        max_x = width - self.margin
        max_y = self.height - self.margin
        return [[min_x, min_y], [max_x, min_y],
                [max_x, max_y], [min_x, max_y]]


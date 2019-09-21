from typing import Union
import math


class Hole:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        return


class Material:
    def __init__(self, material_id, height, width, spacing, margin, hole: Union[Hole, None] = None):
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
        hole:
            瑕疵
        """
        self.material_id = material_id
        self.height = height
        self.width = width
        self.hole = hole
        self.spacing = spacing
        self.margin = margin
        return

    def get_polygon(self, width):
        return [[0, 0], [width, 0], [width, self.height], [0, self.height]]

    def get_margin_polygon(self, width):
        spacing = math.ceil(self.spacing / 2)
        min_x = self.margin
        min_y = self.margin
        max_x = width - self.margin
        max_y = self.height - self.margin
        return [[min_x, min_y], [max_x, min_y],
                [max_x, max_y], [min_x, max_y]]


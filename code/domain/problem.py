from domain.shape import Shape, Position
from domain.material import Material

from pprint import pprint
from typing import List

import pyclipper


class Problem:
    def __init__(self, shapes: List[Shape], material: Material, offset_spacing):
        self.shapes = shapes
        self.material = material
        self.offset_spacing = offset_spacing
        return

    def check_orientation(self):
        print(all(pyclipper.Orientation(shape.polygon) for shape in self.shapes))
        return


from src.domain.shape import Shape, Position
from src.domain.material import Material

from pprint import pprint
from typing import List, Dict
import logging

import pyclipper


class Problem:
    def __init__(self, shapes: Dict[str, Dict[int, Shape]], material: Material,
                 offset_spacing, batch_id):
        self.shapes = shapes
        self.material = material
        self.offset_spacing = offset_spacing
        self.batch_id = batch_id
        return

    def check_orientation(self):
        logging.info(
            all(
                pyclipper.Orientation(shape.polygon)
                for list_shapes in self.shapes.values()
                for shape in list_shapes.values()))
        return

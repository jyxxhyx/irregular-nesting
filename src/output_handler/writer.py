from src.domain.problem import Shape, Problem, Material
from src.local_search.domain.solution import Solution

import csv


def write_to_csv(file_name, problem: Problem, solution: Solution, scale=1):
    with open(file_name, 'w', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file,
                                delimiter=',',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['下料批次号', '零件号', '面料号', '零件外轮廓线坐标'])
        for key, (rotation, position) in solution.positions.items():
            shape = problem.shapes[key][rotation]
            batch_id = shape.batch_id
            shape_id = shape.shape_id
            material_id = shape.material_id
            polygon = shape.generate_positioned_polygon_output(
                position, scale)
            csv_writer.writerow([batch_id, shape_id, material_id, polygon])
    return

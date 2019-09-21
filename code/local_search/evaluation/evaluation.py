from domain.problem import Problem


def calculate_objective(problem: Problem, positions):
    assert len(positions) == len(problem.shapes)
    max_x = max(positions[i].x + problem.shapes[i].max_x for i in range(len(positions)))
    min_x = min(positions[i].x + problem.shapes[i].min_x for i in range(len(positions)))
    # max_y = max(positions[i].y + problem.shapes[i].max_y for i in range(len(positions)))
    # min_y = min(positions[i].y + problem.shapes[i].min_y for i in range(len(positions)))
    return max_x - min_x


def check_feasibility():
    # TODO Apply multiple Point-in-polygon tests
    return

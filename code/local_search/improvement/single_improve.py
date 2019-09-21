from local_search.domain.solution import Solution
from local_search.evaluation.positition import bottom_left_heuristic
from local_search.evaluation.evaluation import calculate_objective
from local_search.framework.base_alg import BaseAlg
from domain.problem import Problem

from copy import copy, deepcopy
import sys


def single_improve(solution: Solution, problem: Problem, i: int, alg: BaseAlg):
    """
    给定一个序列和一个要改变的形状序号i，做局部改善（目前还没用到）
    Parameters
    ----------
    solution
    problem
    i
    alg

    Returns
    -------

    """
    temp_objective = sys.maxsize
    temp_solution = None
    sequence = copy(solution.sequences)
    for j in range(len(sequence)):
        if j != i:
            # Do move
            sequence[i], sequence[j] = sequence[j], sequence[i]
            positions = bottom_left_heuristic(problem, sequence)
            objective = calculate_objective(problem, positions)
            if objective < temp_objective:
                temp_solution = Solution(copy(sequence), deepcopy(positions), objective)
            if objective < alg.get_best_objective():
                return True, Solution(copy(sequence), deepcopy(positions), objective)
            # Undo move
            sequence[i], sequence[j] = sequence[j], sequence[i]
    else:
        return False, temp_solution

from domain import problem
from geometry import nfp_generator
from input_handler import data_reader
from local_search.framework.tabu_search import TabuSearch
from local_search.domain.solution import Solution
from output_handler import drawer, writer

import math
import os
from pprint import pprint
from timeit import default_timer as timer


def _solve_one_instance(material_file, shape_file, nick_name):
    """
    求解一个算例。
    Parameters
    ----------
    material_file: 面料输入路径
    shape_file: 零件输入路径
    nick_name: 用户昵称（输出文件要用）

    Returns
    -------

    """
    start = timer()

    material = data_reader.read_material_from_csv(material_file)

    # TODO 目前多边形外延比较保守（pyclipper计算中会有取整，造成误差），保证可行解
    offset_spacing = math.ceil(material.spacing / 2) + 1

    shape_list = data_reader.read_shapes_from_csv(shape_file, offset_spacing)
    batch = shape_list[0].batch_id
    print('Start to solve batch {}!'.format(batch))

    instance = problem.Problem(shape_list, material, offset_spacing)

    total_area = sum(shape.area for shape in shape_list)
    print('Total area of shapes:\t{:.3f}m2'.format(total_area / 1000000))

    # 解下料问题的主要部分
    tabu_search = TabuSearch(instance)
    tabu_search.solve()

    # 获得结果，输出
    solution = tabu_search.get_best_solution()
    objective = tabu_search.get_best_objective()

    print('Material length:\t{:.3f}m'.format(objective / 1000))
    print('Material area:\t{:.3f}m2'.format(objective * material.height / 1000000))
    utilization = total_area / (objective * material.height)
    print('Material utilization:\t{:.3f}%'.format(utilization))
    file_name = '{}_{}_{:.3f}.csv'.format(nick_name, batch, utilization)
    file_name = os.path.join(os.pardir, 'submit', 'DatasetA', file_name)
    writer.write_to_csv(file_name, instance, solution)
    file_name = '{}_{}_{:.3f}.pdf'.format(nick_name, batch, utilization)
    file_name = os.path.join(os.pardir, 'figure', 'DatasetA', file_name)
    drawer.draw_result(instance, solution.objective, solution.positions, file_name)
    end = timer()
    print('Total solution time:\t{:.3f}s\n'.format(end - start))
    return


def main():
    material_str = 'mianliao'
    shape_str = 'lingjian'
    nick_name = 'jiangyincaijiao1'

    data_dir = os.path.join(os.pardir, 'data')
    for root, dirs, files in os.walk(data_dir):
        # 遍历不同的dataset文件夹
        for input_dir in dirs:
            instance_dir = os.path.join(root, input_dir)
            # 遍历各dataset下面不同算例文件
            for file in os.listdir(instance_dir):
                # 根据面料输入来确定算例
                if shape_str in file:
                    pass
                elif material_str in file:
                    material_file = os.path.join(instance_dir, file)
                    shape_file = material_file.replace(material_str, shape_str)
                    _solve_one_instance(material_file, shape_file, nick_name)


if __name__ == '__main__':
    main()

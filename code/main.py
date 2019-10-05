from domain import problem
from geometry import nfp_generator
from input_handler import data_reader
from local_search.framework.tabu_search import TabuSearch
from local_search.domain.solution import Solution
from output_handler import drawer, writer

import logging
import logging.config
import math
import os
from pprint import pprint
from timeit import default_timer as timer
import yaml


def setup_logging(logging_config_path="logging.yaml", level=logging.INFO):
    """
    Set up logging file configuration

    Args:
    logging_config_path (str):   logging configuration file path,
                                    by default, it is current path
    level (logging object):      logging.INFO (by default), logging.DEBUG ...

    Return:
    None

    Raise:
    None
    """

    # check configuration path
    path = logging_config_path
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        # if path does not exist, use default logging configuration, output logging.log
        logging.basicConfig(level=level,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='logging.log',
                            filemode='w')


def _solve_one_instance(material_file, shape_file, nick_name, scale=1):
    """
    求解一个算例。
    Parameters
    ----------
    material_file: 面料输入路径
    shape_file: 零件输入路径
    nick_name: 用户昵称（输出文件要用）
    scale: 图形缩放比例

    Returns
    -------

    """
    logger = logging.getLogger(__name__)
    start = timer()

    instance, batch = _construct_instance(material_file, shape_file, scale)

    # 解下料问题的主要部分
    tabu_search = TabuSearch(instance)
    # tabu_search.initialize_nfps()
    tabu_search.initialize_nfps_pool()
    tabu_search.solve()

    # 获得结果，输出
    solution = tabu_search.get_best_solution()
    objective = tabu_search.get_best_objective()

    _output_solution(instance, solution, objective, scale, nick_name, batch)

    end = timer()
    logger.info('Total solution time:\t{:.3f}s\n'.format(end - start))
    return


def _construct_instance(material_file, shape_file, scale):
    material = data_reader.read_material_from_csv(material_file, scale)

    # TODO 目前多边形外延比较保守（pyclipper计算中会有取整，造成误差），保证可行解
    offset_spacing = math.ceil(material.spacing / 2) + 1

    shape_list = data_reader.read_shapes_from_csv(shape_file, offset_spacing, scale)
    batch = shape_list[0].batch_id
    logging.info('Start to solve batch {}!'.format(batch))

    instance = problem.Problem(shape_list, material, offset_spacing)
    return instance, batch


def _output_solution(instance, solution, objective, scale, nick_name, batch):
    logger = logging.getLogger(__name__)
    material = instance.material
    total_area = sum(shape.area for shape in instance.shapes)
    logging.info('Total area of shapes:\t{:.3f}m2'.format(total_area / 1000 ** 2 / scale ** 2))
    logger.info('Material length:\t{:.3f}m'.format(objective / 1000 / scale))
    logger.info('Material area:\t{:.3f}m2'.format(objective * material.height / 1000 ** 2 / scale ** 2))
    utilization = total_area / (objective * material.height)
    logger.info('Material utilization:\t{:.3f}%'.format(utilization * 100))
    file_name = '{}_{}_{:.3f}.csv'.format(nick_name, batch, utilization)
    file_name = os.path.join(os.pardir, 'submit', 'DatasetA', file_name)
    writer.write_to_csv(file_name, instance, solution)
    file_name = '{}_{}_{:.3f}.pdf'.format(nick_name, batch, utilization)
    file_name = os.path.join(os.pardir, 'figure', 'DatasetA', file_name)
    drawer.draw_result(instance, solution.objective, solution.positions, file_name)
    return


def _check_create_result_directory(input_dir):
    """
    检查输出、图片路径是否存在。
    Parameters
    ----------
    input_dir

    Returns
    -------

    """
    output_dir = input_dir.replace('data', 'submit')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_dir = input_dir.replace('data', 'figure')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return


def main():
    material_str = 'mianliao'
    shape_str = 'lingjian'
    nick_name = 'jiangyincaijiao1'
    scale = 10

    data_dir = os.path.join(os.pardir, 'data')
    for root, dirs, files in os.walk(data_dir):
        # 遍历不同的dataset文件夹
        for input_dir in dirs:
            instance_dir = os.path.join(root, input_dir)
            # 遍历各dataset下面不同算例文件
            _check_create_result_directory(instance_dir)
            for file in os.listdir(instance_dir):
                # 根据面料输入来确定算例
                if shape_str in file:
                    pass
                elif material_str in file:
                    material_file = os.path.join(instance_dir, file)
                    shape_file = material_file.replace(material_str, shape_str)
                    _solve_one_instance(material_file, shape_file, nick_name, scale)


if __name__ == '__main__':
    logging_path = os.path.join(os.getcwd(), "logging.yaml")
    setup_logging(logging_path)
    main()

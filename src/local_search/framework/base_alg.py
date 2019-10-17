import abc


class BaseAlg:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def solve(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_best_solution(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_current_solution(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_best_objective(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_current_objective(self):
        raise NotImplementedError

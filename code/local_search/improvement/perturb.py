import random

random.seed = 0


def single_shuffle(sequence):
    """
    讲形状处理顺序进行一次打乱（简单试了一下，没啥效果）
    Parameters
    ----------
    sequence

    Returns
    -------

    """
    split_index = random.randint(1, len(sequence) - 1)
    new_sequence = sequence[split_index:] + sequence[:split_index]
    return new_sequence

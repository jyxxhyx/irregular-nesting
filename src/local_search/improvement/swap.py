from copy import copy


def swap_two_shapes(sequence, i, j):
    temp_sequence = copy(sequence)
    temp_sequence[i], temp_sequence[j] = temp_sequence[j], temp_sequence[i]
    return temp_sequence


def reverse_swap_two_shapes(sequence, i, j):
    return swap_two_shapes(sequence, i, j)

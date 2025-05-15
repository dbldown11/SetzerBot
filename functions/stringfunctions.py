import random

async def int_list_to_string(int_list):
    """Convert a list of integers to a comma-separated string."""
    return ','.join(str(i) for i in int_list)


async def string_to_int_list(string):
    """Convert a string of comma-separated integers to a list of integers."""
    return [int(i) for i in string.split(',')]

async def shuffle_list(ordered_list):
    """
    Shuffle a list while ensuring no element remains in its original position.
    """
    shuffled = ordered_list[:]
    while True:
        random.shuffle(shuffled)
        if all(shuffled[i] != ordered_list[i] for i in range(len(ordered_list))):
            return shuffled

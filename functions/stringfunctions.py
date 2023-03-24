async def int_list_to_string(int_list):
    """Convert a list of integers to a comma-separated string."""
    return ','.join(str(i) for i in int_list)


async def string_to_int_list(string):
    """Convert a string of comma-separated integers to a list of integers."""
    return [int(i) for i in string.split(',')]

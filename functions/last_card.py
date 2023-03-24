async def last_card(lst, *nums):
    """
    Find the last integer from a given set that appears in a list of integers.

    Args:
    lst (list[int]): The list of integers to search.
    *nums (int): One or more integers to find the last instance of.

    Returns:
    int: The last integer from the given set that appears in the list, or None if none are found.
    """
    last_integer = None
    for num in nums:
        try:
            index = len(lst) - lst[::-1].index(num) - 1
            if last_integer is None or index > lst.index(last_integer):
                last_integer = num
        except ValueError:
            pass
    return last_integer
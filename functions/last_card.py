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
    for card in lst:
        if card in nums:
            last_integer = card
    return last_integer
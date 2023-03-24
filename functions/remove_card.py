def remove_card(list_of_integers, integer_to_remove):
    """
    This function takes a list of integers and an integer to remove, and returns
    a new list with all instances of the integer removed.
    """
    return [integer for integer in list_of_integers if integer != integer_to_remove]
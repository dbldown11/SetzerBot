def remove_card(list_of_integers, integer_to_remove):
    """
    This function takes a list of integers and an integer to remove, and returns
    a new list with all instances of the integer removed.
    """
    new_list = [i for i in list_of_integers if i != integer_to_remove]
    return new_list
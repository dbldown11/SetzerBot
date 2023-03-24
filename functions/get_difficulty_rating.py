async def get_difficulty_rating(difficulty) -> str:
    if difficulty >= 8:
        difficulty_rating = 'very challenging'
    elif difficulty >= 4:
        difficulty_rating = 'moderately challenging'
    elif difficulty <= -8:
        difficulty_rating = 'very easy'
    elif difficulty <= -4:
        difficulty_rating = 'moderately easy'
    else:
        difficulty_rating = 'about average difficulty'

    return difficulty_rating
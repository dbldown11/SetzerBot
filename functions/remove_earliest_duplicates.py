def remove_earliest_duplicates(lst):
    seen = {}
    result = []
    for num in lst:
        seen[num] = seen.get(num, 0) + 1
        if seen[num] == 1:
            result.append(num)
        elif seen[num] > 1:
            result.remove(num)
            result.append(num)
    return result
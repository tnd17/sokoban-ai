def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def basic_heuristic(boxes, goals):
    distance = 0
    for box in boxes:
        distance += min(manhattan_distance(box, goal) for goal in goals)
    return distance
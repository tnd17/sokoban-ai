def basic_heuristic(boxes, goals):
    """
    Tính tổng khoảng cách từ mỗi hộp đến ô đích gần nhất
    """
    total_distance = 0
    for box in boxes:
        # Khoảng cách từ 1 hộp đến tập các đích
        dist = min(abs(box[0] - g[0]) + abs(box[1] - g[1]) for g in goals)
        total_distance += dist
    return total_distance
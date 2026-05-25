def fitness_func(ga_instance, solution, _):
    n = len(solution)
    conflicts = 0
    for i in range(n):
        for j in range(i + 1, n):
            # Column
            if solution[i] == solution[j]:          
                conflicts += 1
            # Diagonal
            if abs(solution[i] - solution[j]) == abs(i - j):
                conflicts += 1
    return -conflicts

def count_conflicts(board: list[int]) -> int:
    n = len(board)
    conflicts = 0
    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j]:
                conflicts += 1
            if abs(board[i] - board[j]) == abs(i - j):
                conflicts += 1
    return conflicts

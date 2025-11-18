from collections import deque
import heapq

def bfs(n, snakes, ladders):
    """
    Performs a Breadth-First Search to find the minimum number of dice throws.
    """
    board_size = n * n
    q = deque([(1, 0)])  # (current_position, distance)
    visited = {1}

    while q:
        pos, dist = q.popleft()

        if pos == board_size:
            return dist

        for i in range(1, 7):
            next_pos = pos + i
            if next_pos <= board_size:
                if next_pos in ladders:
                    next_pos = ladders[next_pos]
                elif next_pos in snakes:
                    next_pos = snakes[next_pos]

                if next_pos not in visited:
                    visited.add(next_pos)
                    q.append((next_pos, dist + 1))
    return -1 # Should not be reached in a normal board

def dijkstra(n, snakes, ladders):
    """
    Performs Dijkstra's algorithm to find the minimum number of dice throws.
    """
    board_size = n * n
    dist = {i: float('inf') for i in range(1, board_size + 1)}
    dist[1] = 0
    pq = [(0, 1)]  # (distance, current_position)

    while pq:
        d, pos = heapq.heappop(pq)

        if d > dist[pos]:
            continue

        if pos == board_size:
            return d

        for i in range(1, 7):
            next_pos = pos + i
            if next_pos <= board_size:
                if next_pos in ladders:
                    next_pos = ladders[next_pos]
                elif next_pos in snakes:
                    next_pos = snakes[next_pos]
                
                if dist[pos] + 1 < dist[next_pos]:
                    dist[next_pos] = dist[pos] + 1
                    heapq.heappush(pq, (dist[next_pos], next_pos))

    return -1 # Should not be reached in a normal board

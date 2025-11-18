# Snake and Ladder Game Problem Report

## 1. Snake and Ladder Game Problem

### i. Explain the Program Logic used to solve the problem

The program implements a classic Snake and Ladder game with a twist: instead of playing the game manually, the user is asked to guess the minimum number of dice throws required to win. The program then uses two different algorithms, Breadth-First Search (BFS) and Dijkstra's algorithm, to calculate the correct answer and compares it with the user's input.

The program is structured into the following modules:

*   **`game.py`**: This is the main module that drives the game. It handles user input for the board size, sets up the game board with random snakes and ladders, calls the algorithms to find the minimum number of throws, presents the user with a multiple-choice question, and saves the game results to a database.
*   **`algorithms.py`**: This module contains the implementations of the BFS and Dijkstra's algorithms. Both algorithms model the game board as a graph where the cells are the nodes and a dice throw represents an edge. The goal is to find the shortest path from the starting cell (1) to the final cell (N^2).
*   **`database.py`**: This module handles all interactions with the SQLite database. It includes functions to set up the database and the results table, and to save the results of each game round.
*   **`utils.py`**: This module contains utility functions, such as the `display_board` function, which provides a visual representation of the game board.
*   **`test_game.py`**: This module contains unit tests for the algorithms to ensure their correctness.

The game flow is as follows:

1.  The user is prompted to enter the size of the board (N).
2.  The program generates a random board with N-2 snakes and N-2 ladders.
3.  The program uses both BFS and Dijkstra's algorithm to calculate the minimum number of dice throws required to reach the final cell.
4.  The user is presented with three choices: the correct answer, the correct answer + 1, and the correct answer - 1.
5.  The user enters their choice.
6.  If the user's answer is correct, their name and the time taken by each algorithm are saved to the database.
7.  The user is asked if they want to play another round.

### ii. Analyze the Complexity of the algorithms based on the Program outputs & Program logic

Both the BFS and Dijkstra's algorithms are used to find the shortest path in a graph. In our case, the graph has V = N^2 vertices (the cells on the board) and each vertex has at most 6 outgoing edges (the possible dice throws).

*   **Breadth-First Search (BFS)**: BFS is an algorithm for traversing or searching tree or graph data structures. It starts at the tree root (or some arbitrary node of a graph, sometimes referred to as a 'search key') and explores the neighbor nodes first, before moving to the next level neighbors.

    *   **Time Complexity**: The time complexity of BFS is O(V + E), where V is the number of vertices and E is the number of edges. In our case, V = N^2 and E is at most 6 * N^2. Therefore, the time complexity is O(N^2).
    *   **Space Complexity**: The space complexity of BFS is O(V) = O(N^2) to store the `visited` set and the queue.

*   **Dijkstra's Algorithm**: Dijkstra's algorithm is an algorithm for finding the shortest paths between nodes in a graph, which may represent, for example, road networks. It was conceived by computer scientist Edsger W. Dijkstra in 1956 and published three years later.

    *   **Time Complexity**: The time complexity of Dijkstra's algorithm using a binary heap is O(E log V). In our case, this is O(6 * N^2 * log(N^2)) = O(N^2 * log(N)).
    *   **Space Complexity**: The space complexity of Dijkstra's algorithm is O(V) = O(N^2) to store the `dist` dictionary and the priority queue.

### iii. Comparison of the two algorithmic approaches

| Feature | Breadth-First Search (BFS) | Dijkstra's Algorithm |
| :--- | :--- | :--- |
| **Algorithm Type** | Traversal algorithm | Shortest path algorithm |
| **Graph Type** | Works on unweighted graphs | Works on weighted graphs |
| **Time Complexity** | O(N^2) | O(N^2 * log(N)) |
| **Implementation** | Simpler to implement | More complex to implement |
| **Use Case** | Finding the shortest path in an unweighted graph | Finding the shortest path in a weighted graph |

In the context of the Snake and Ladder game, the graph is unweighted, as each dice throw has a weight of 1. Therefore, BFS is the more efficient algorithm for this problem. Dijkstra's algorithm will still produce the correct result, but it will be slightly slower due to the overhead of the priority queue.

The program calculates and records the time taken by both algorithms for each game round. This allows for a practical comparison of their performance.

### iv. Chart Containing the time Taken for each algorithm Technique when run the Game Individually for 15 Game Rounds

To generate this chart, you need to run the game for 15 rounds and record the time taken by each algorithm. You can do this by running the `game.py` file and playing the game 15 times. After each round, the program will print the time taken by each algorithm. You can then collect this data and create a chart.

Here is a sample of what the data might look like. The actual values will vary depending on the board size and the specific arrangement of snakes and ladders.

| Game Round | Board Size (N) | Time Taken BFS (s) | Time Taken Dijkstra (s) |
| :--- | :--- | :--- | :--- |
| 1 | 6 | 0.00012 | 0.00015 |
| 2 | 8 | 0.00025 | 0.00030 |
| 3 | 10 | 0.00045 | 0.00055 |
| 4 | 12 | 0.00070 | 0.00085 |
| 5 | 7 | 0.00018 | 0.00022 |
| 6 | 9 | 0.00035 | 0.00042 |
| 7 | 11 | 0.00055 | 0.00065 |
| 8 | 6 | 0.00011 | 0.00014 |
| 9 | 8 | 0.00024 | 0.00029 |
| 10 | 10 | 0.00043 | 0.00053 |
| 11 | 12 | 0.00068 | 0.00082 |
| 12 | 7 | 0.00017 | 0.00021 |
| 13 | 9 | 0.00033 | 0.00040 |
| 14 | 11 | 0.00053 | 0.00063 |
| 15 | 6 | 0.00010 | 0.00013 |

### v. Database output Screenshot for Chat Content

To get the database output, you can use a database browser for SQLite. Here are the steps:

1.  Download and install a database browser for SQLite, such as [DB Browser for SQLite](https://sqlitebrowser.org/).
2.  Open the `snake_and_ladder.db` file in the DB Browser.
3.  Go to the "Browse Data" tab and select the "results" table.
4.  You will see the data that has been saved to the database. You can take a screenshot of this table.

The table will have the following columns:

*   `id`: The unique ID of the game round.
*   `player_name`: The name of the player.
*   `correct_answer`: The correct minimum number of throws.
*   `time_taken_bfs`: The time taken by the BFS algorithm.
*   `time_taken_dijkstra`: The time taken by the Dijkstra's algorithm.
*   `timestamp`: The date and time when the game was played.

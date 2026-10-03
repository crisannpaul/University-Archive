from Model.game.utils import Queue, PriorityQueue
from Model.game.game_logic import Grid


def execute_path(grid: Grid, path):
    moves = {'UP': grid.move_up(), 'DOWN': grid.move_down(), 'LEFT': grid.move_left(), 'RIGHT': grid.move_right()}
    for move in path:
        moves[move]()


def a_star(grid: Grid):
    frontier = PriorityQueue()

    explored = []

    start_state = grid.player_pos
    goal_state = grid.reward_pos
    current = Node(start_state, None, None, 0)

    frontier.push(current, 0)

    while not frontier.isEmpty():
        current = frontier.pop()
        state = current.get_state()
        explored.append((state, current.get_cost()))

        if state == goal_state:
            return get_path(current)
        else:
            successors = grid.get_successors(state)

            for succ_state, succ_action, succ_cost in successors:
                new_cost = current.get_cost() + succ_cost
                new_node = Node(succ_state, succ_action, current, new_cost)

                already_explored = False
                for node in explored:
                    exp_state, exp_cost = node

                    if (succ_state == exp_state) and (new_cost >= exp_cost):
                        already_explored = True

                if not already_explored:
                    frontier.push(new_node, new_cost + grid.manhattan_heuristic(succ_state))
                    explored.append((succ_state, new_cost))

    return get_path(current)


def search(grid: Grid):
    frontier = Queue()

    explored = []

    start_state = grid.player_pos
    goal_state = grid.reward_pos
    current = Node(start_state, None, None, 0)

    frontier.push(current)
    while not frontier.isEmpty():
        current = frontier.pop()
        state = current.get_state()
        explored.append(state)
        print(f"Current: {current}")
        print(f"Frontier: {frontier}")
        print(f"Explored: {explored}")

        if state == goal_state:
            print("Goal")
            return explored
        else:
            successors = grid.get_successors(state)
            print(f"Successors: {successors}")
            for succ_state, succ_action, _ in successors:
                if not succ_state in explored:
                    new_node = Node(succ_state, succ_action, current)
                    frontier.push(new_node)

        print("\n")
    return explored


def get_path(node):
    path = []
    while node.get_parent() != None:
        path.append(node.get_action())
        node = node.get_parent()
    path.reverse()
    return path


class Node:
    def __init__(self, state, action, parent, cost=0):
        self.state = state
        self.action = action
        self.parent = parent
        self.cost = cost

    def get_parent(self):
        return self.parent

    def get_cost(self):
        return self.cost

    def get_state(self):
        return self.state

    def get_action(self):
        return self.action

    def __str__(self):
        return f"{self.state} - {self.action}"

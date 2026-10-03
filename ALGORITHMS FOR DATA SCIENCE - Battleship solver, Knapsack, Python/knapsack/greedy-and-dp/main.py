import random
import time
import matplotlib.pyplot as plt

class Profiler:
    class Operation:
        def __init__(self):
            self._count = 0

        def count(self, increment: int = 1):
            self._count += increment

        def divide(self, val: int):
            self._count //= val

    def __init__(self, name: str = "Performance"):
        self._name = name
        self._operations: dict[str, dict[int, Profiler.Operation]] = {}

    def createOperation(self, name: str, size: int):
        if name not in self._operations:
            self._operations[name] = {}
        if size not in self._operations[name]:
            self._operations[name][size] = Profiler.Operation()
        return self._operations[name][size]
    
    def report(self):
        if len(self._operations) == 0:
            return
        if len(self._operations) < 4:
            fig, axes = plt.subplots(len(self._operations))
            fig.set_size_inches(4, 3 * len(self._operations))
            if len(self._operations) == 1:
                axes = [axes]
        else:
            # two columns
            fig, axes = plt.subplots((len(self._operations) + 1) // 2, 2)
            fig.set_size_inches(8, 1.5 * len(self._operations))
            axes = [row[0] for row in axes] + [row[1] for row in axes]
        fig.tight_layout(pad=2)
        fig.canvas.manager.set_window_title(self._name)
        for idx, (name, ops) in enumerate(self._operations.items()):
            ops = sorted(ops.items())
            x = [op[0] for op in ops]
            y = [op[1]._count for op in ops]
            axes[idx].plot(x, y)
            axes[idx].set_ylim(ymin = 0, ymax = max(y) * 1.2)
            axes[idx].set_title(name)
        crtTime = time.strftime("%Y-%m-%d-%H-%M")
        plt.savefig(f"{self._name}-{crtTime}.pdf")
        plt.show()

class Item:
    def __init__(self, i, vi, wi, op: Profiler.Operation):
        self.i = i
        self.profitability = vi / wi
        self.op = op

    def __lt__(self, other):
        self.op.count(1)
        return self.profitability < other.profitability
    

TEST_KNAPSACK = [
    ([5, 3, 3], [3, 2, 2], 4),
    ([60, 100, 120], [10, 20, 30], 50),
    ([80, 40, 60, 20], [15, 10, 25, 5], 35),
    # ([50, 70, 80, 90], [10, 20, 30, 40], 60),
    # ([100, 200, 150, 50], [20, 30, 25, 10], 70),
    # ([70, 90, 110, 130], [15, 25, 35, 45], 80),
    # ([85, 95, 105, 115], [12, 22, 32, 42], 90),
    # ([55, 65, 75, 85], [11, 21, 31, 41], 100)
]

def knapsack_fractional(v, w, W, op: Profiler.Operation = Profiler.Operation()):
    sol = []
    n = len(v)
    op.count(2)
    P = [Item(i, vi, wi, op) for i, (vi, wi) in enumerate(zip(v, w))] 

    P.sort(reverse=True)

    value = 0.0
    weight = 0
    for j in range(n):
        i = P[j].i
        op.count(2)
        if weight + w[i] <= W:
            op.count(3)
            sol.append((i, 1.0))
            weight += w[i]
            value += v[i]
        else:
            op.count(1)
            if weight < W:
                op.count(5)
                f = (W - weight) / w[i]
                sol.append((i, f))
                value += f * v[i]
            break

    return value, sol

def knapsack_greedy(v, w, W, op: Profiler.Operation = Profiler.Operation()):
    sol = []
    n = len(v)
    op.count(2)
    P = [Item(i, vi, wi, op) for i, (vi, wi) in enumerate(zip(v, w))] 


    P.sort(reverse=True)

    value = 0.0
    weight = 0
    for j in range(n):
        i = P[j].i
        op.count(2)
        if weight + w[i] <= W:
            op.count(3)
            sol.append(i)
            weight += w[i]
            value += v[i]

    return value, sol

def knapsack_dynamic(v, w, W, op: Profiler.Operation = Profiler.Operation()):
    n = len(v)
    dp = [[0] * (W + 1) for _ in range(n+1)] # Fill the whole matrix with 0 values
    op.count((n+1) * (W + 1))
    for i in range(1, n+1):
        for j in range (1, W+1):
            if w[i-1] > j:
                dp[i][j] = dp[i-1][j]
                op.count(1)
            else:
                alternative =  dp[i-1][j-w[i-1]] + v[i-1]
                dp[i][j] = max(dp[i-1][j], alternative)
                op.count(4)

    sol = []
    i = n
    j = W
    while i > 0:
        if dp[i][j] > dp[i-1][j]:
            sol.append(i-1)
            j -= w[i-1]
            op.count(3)
        i -= 1
        op.count(1)
    sol.reverse()
    return dp[n][W], sol

def demo():
    for v, w, W in TEST_KNAPSACK:
        print(f"\n{'='*5} For items={list(zip(v,w))} and {W=} {'='*5}")

        value, sol = knapsack_fractional(v, w, W)
        print(f"Knapsack fractional: {value=}, {sol=}")
        
        value, sol = knapsack_greedy(v, w, W)
        print(f"Knapsack greedy: {value=}, {sol=}")

        value, sol = knapsack_dynamic(v, w, W)
        print(f"Knapsack dynamic: {value=}, {sol=}")
        print("="*80)



def perf():
    p = Profiler()

    NR_TESTS = 5
    N_MAX = 3000
    SIZE_INCREMENT = 100
    W = 1500

    for size in range(SIZE_INCREMENT, N_MAX + 1, SIZE_INCREMENT):
        print(f"\r{size=} / {N_MAX}", end="")
        op_fractional = p.createOperation("Fractional, n varying", size)
        op_greedy = p.createOperation("Greedy, n varying", size)
        op_dynamic = p.createOperation("Dynamic, n varying", size)
        for _ in range(NR_TESTS):
            v = [random.randint(20, 50) for _ in range(size)]
            w = [random.randint(20, 50) for _ in range(size)]
            knapsack_fractional(v, w, W, op=op_fractional)
            knapsack_greedy(v, w, W, op=op_greedy)
            knapsack_dynamic(v, w, W, op=op_dynamic)
        op_fractional.divide(NR_TESTS)
        op_greedy.divide(NR_TESTS)
        op_dynamic.divide(NR_TESTS)

    N_MAX = 3000
    W_MAX = 3000
    W_INCREMENT = 100
    for W in range(W_INCREMENT, W_MAX + 1, W_INCREMENT):
        print(f"\r{W=} / {W_MAX}", end="")
        op_fractional = p.createOperation("Fractional, W varying", W)
        op_greedy = p.createOperation("Greedy, W varying", W)
        op_dynamic = p.createOperation("Dynamic, W varying", W)
        for _ in range(NR_TESTS):
            v = [random.randint(20, 50) for _ in range(size)]
            w = [random.randint(20, 50) for _ in range(size)]
            knapsack_fractional(v, w, W, op=op_fractional)
            knapsack_greedy(v, w, W, op=op_greedy)
            knapsack_dynamic(v, w, W, op=op_dynamic)
        op_fractional.divide(NR_TESTS)
        op_greedy.divide(NR_TESTS)
        op_dynamic.divide(NR_TESTS)
    p.report()


if __name__ == "__main__":
    demo()
    perf()
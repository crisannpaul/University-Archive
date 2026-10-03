import random
import time
import matplotlib.pyplot as plt

class Profiler:
    def __init__(self, name: str = "Performance"):
        self._name = name
        self._times: dict[str, dict[int, float]] = {}

    def addTime(self, name: str, size: int, elapsed: float):
        if name not in self._times:
            self._times[name] = {}
        if size not in self._times[name]:
            self._times[name][size] = 0.0
        self._times[name][size] += elapsed
    
    def report(self):
        fig, axes = plt.subplots(2)
        fig.set_size_inches(8, 8)
        fig.tight_layout(pad=2)
        fig.canvas.manager.set_window_title(self._name)
        for name, times in self._times.items():
            times = sorted(times.items())
            x = [t[0] for t in times]
            y = [t[1] for t in times]
            axes[0].plot(x, y, label=name)
            axes[1].plot(x, y, label=name)
        axes[1].set_yscale("log")
        axes[0].legend()
        axes[1].legend()
        
        crtTime = time.strftime("%Y-%m-%d-%H-%M")
        plt.savefig(f"{self._name}-{crtTime}.pdf")
        plt.show()


TEST_KNAPSACK = [
    # ([5, 3, 3], [3, 2, 2], 4),
    # ([60, 100, 120], [10, 20, 30], 50),
    # ([80, 40, 60, 20], [15, 10, 25, 5], 35),
    ([7, 5, 4, 1, 8, 2, 6, 4], [2, 9, 6, 3, 3, 4, 2, 5], 22)
    # ([50, 70, 80, 90], [10, 20, 30, 40], 60),
    # ([100, 200, 150, 50], [20, 30, 25, 10], 70),
    # ([70, 90, 110, 130], [15, 25, 35, 45], 80),
    # ([85, 95, 105, 115], [12, 22, 32, 42], 90),
    # ([55, 65, 75, 85], [11, 21, 31, 41], 100)
]

def knapsack_bruteforce(v: list[int], w: list[int], W: int):
    sol = []
    maxValue = 0
    n = len(v)
    for s in range(1, 2 ** n):
        value = weight = 0
        crtSol = []
        i = 0
        while s > 0:
            if s % 2 == 1:
                crtSol.append(i)
                value += v[i]
                weight += w[i]
            i += 1
            s //= 2
        if weight <= W and value > maxValue:
            maxValue = value
            sol = crtSol

    return maxValue, sol


def compute_for_subset(s: int, v: list[int], w: list[int]):
    value = 0
    weight = 0
    n = len(v)
    for i in range(n):
        if (s >> i) & 1:
            value += v[i]
            weight += w[i]
    return value, weight

def binary_search(L: list[tuple[int, int, int]], target_weight: int):
    # L is sorted by weight
    low = 0
    high = len(L) - 1
    result = (0, 0, 0)  # Default to zero if no valid subset is found
    while low <= high:
        mid = (low + high) // 2
        weight, value, s = L[mid]
        if weight <= target_weight:
            result = L[mid]
            low = mid + 1
        else:
            high = mid - 1
    return result

def expand_solution(sol: tuple[int, int], na: int):
    s1, s2 = sol
    indices = []
    # Extract indices from the first half
    for i in range(na):
        if (s1 >> i) & 1:
            indices.append(i)
    # Extract indices from the second half
    nb = s2.bit_length()
    for i in range(nb):
        if (s2 >> i) & 1:
            indices.append(na + i)
    return indices

def knapsack_mitm(v: list[int], w: list[int], W: int):
    n = len(v)
    na = n // 2
    nb = n - na
    va, vb = v[:na], v[na:]
    wa, wb = w[:na], w[na:]

    # Generate all possible combinations of the first half
    L = []
    for s in range(1 << na):
        value, weight = compute_for_subset(s, va, wa)
        if weight <= W:
            L.append((weight, value, s))  # Store weight first for sorting
    # Sort L by weight
    L.sort()

    # Remove dominated pairs (keep subsets with higher value for given weight)
    newL = []
    maxValue = -1
    for weight, value, s in L:
        if value > maxValue:
            newL.append((weight, value, s))
            maxValue = value
    L = newL

    maxValue = 0
    sol = (0, 0)
    # For each subset of the second half
    for s in range(1 << nb):
        value, weight = compute_for_subset(s, vb, wb)
        if weight <= W:
            # Remaining capacity after selecting items from the second half
            remaining_weight = W - weight
            # Find the best subset from the first half within the remaining capacity
            element = binary_search(L, remaining_weight)
            total_value = value + element[1]
            if total_value > maxValue:
                maxValue = total_value
                sol = (element[2], s)
    sol = expand_solution(sol, na)
    return maxValue, sol

def demo():
    for v, w, W in TEST_KNAPSACK:
        print(f"\n{'='*5} For items={list(zip(v,w))} and {W=} {'='*5}")

        value, sol = knapsack_bruteforce(v, w, W)
        print(f"Knapsack fractional: {value=}, {sol=}")
        print("="*80)

def test():
    def validate(sol, v, w, W, V):
        if len(sol) != len(set(sol)):
            return False
        if min(sol) < 0 or max(sol) >= len(v):
            return False
        if sum(w[i] for i in sol) > W:
            return False
        if sum(v[i] for i in sol) != V:
            return False
        return True

    random.seed(10)
    fail = False
    for _ in range(1000):
        n = random.randint(4, 15)
        v = [random.randint(20, 50) for _ in range(n)]
        w = [random.randint(20, 50) for _ in range(n)]
        W  = sum(w) * 3 // 4

        value1, sol1 = knapsack_bruteforce(v, w, W)
        value2, sol2 = knapsack_mitm(v, w, W)

        if not validate(sol1, v, w, W, value1) or not validate(sol2, v, w, W, value2) or value1 != value2:
            print(f"Error: {v=}, {w=}, {W=}")
            print(f"Bruteforce: {value1=}, {sol1=}")
            print(f"MitM: {value2=}, {sol2=}")
            fail = True
            break

    if not fail:
        print("All tests passed")

def perf():
    p = Profiler()

    NR_TESTS = 5
    N_MAX = 20
    SIZE_INCREMENT = 2
    W = 10 * N_MAX // 2

    for size in range(SIZE_INCREMENT, N_MAX + 1, SIZE_INCREMENT):
        print(f"\r{size=} / {N_MAX}", end="")
        tests = []
        for _ in range(NR_TESTS):
            v = [random.randint(20, 50) for _ in range(size)]
            w = [random.randint(20, 50) for _ in range(size)]
            tests.append((v, w))

        # Measure time for knapsack_bruteforce
        time_start = time.perf_counter()
        for (v, w) in tests:
            knapsack_bruteforce(v, w, W)
        elapsed = time.perf_counter() - time_start
        elapsed /= NR_TESTS
        p.addTime("Bruteforce", size, elapsed)

        # Measure time for knapsack_mitm
        time_start = time.perf_counter()
        for (v, w) in tests:
            knapsack_mitm(v, w, W)
        elapsed = time.perf_counter() - time_start
        elapsed /= NR_TESTS
        p.addTime("MitM", size, elapsed)

    p.report()

if __name__ == "__main__":
    test()
    # demo()
    # perf()
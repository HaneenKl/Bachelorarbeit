"""Stockmeyer counters and lower bounds for f(n,k)"""
from zimin import zimin_index


def tau(n):
    if n == 0:
        return 1
    return 2 ** tau(n - 1)


def counter_of_order_n(i, n):
    """Return the i-th counter of order n as a list of symbols."""
    if n == 1:
        return ["{}_1".format(i)]

    num_blocks = tau(n - 1)
    bits = [(i >> j) & 1 for j in range(num_blocks)]

    word = []

    for j in range(num_blocks):
        word += counter_of_order_n(j, n - 1)
        word.append("{}_{}".format(bits[j], n))

    return word


def show(word):
    """Return a string representation of the word."""
    return " ".join(word)


###tests############################################################################
## test to show lenght, f(n,k) > tau(n)-1, and zimin_index([[0]]_n) < n and the word itself
def test_counters3(max_n):
    for n in range(1, max_n + 1):
        for i in range(tau(n)):
            w = counter_of_order_n(i, n)
            print("[[{}]]_{} = {}  (length={})".format(i, n, show(w), len(w)))
        print()


# test_counters3(4)


def testt_counters(max_n):
    for n in range(1, max_n + 1):
        for i in range(tau(n)):
            w = counter_of_order_n(i, n)
            print("[[{}]]_{} = {}  (length={})".format(i, n, show(w), len(w)))
        print()


# testt_counters(4)


def expected_zimin(i, n):
    if n == 1:
        return 1
    if n == 2:
        return 2 if i in (0, 3) else 1
    if n == 3:
        return 2
    return n - 1  # n >= 4


def test_counters(max_n):
    for n in range(1, max_n + 1):
        for i in range(tau(n)):
            got = zimin_index(counter_of_order_n(i, n))
            exp = expected_zimin(i, n)
            status = "ok" if got == exp else "FAIL"
            print(f"[[{i}]]_{n}: got={got} expected={exp} {status}")
        print()


# test_counters(4)

### test zimin_index on counters
# Expected (Theorem 5):
#   [[0]]_1 = 1,  [[1]]_1 = 1
#   [[0]]_2 = 2,  [[1]]_2 = 1,  [[2]]_2 = 1,  [[3]]_2 = 2
#   [[i]]_3 = 2   for all i in [0, 15]
#   [[i]]_n = n-1 for all n >= 4
def test_zimin_index_on_counters():
    for n in [1, 2, 4]:
        for i in range(tau(n)):
            w = counter_of_order_n(i, n)
            print("[[{}]]_{} = {}  ->  zimin_index = {}".format(i, n, show(w), zimin_index(w)))
        print()


# test_zimin_index_on_counters()

# Witness for Corollary 1: f(n, 2n-1) > tau(n) - 1
# Needs both: len([[0]]_n) >= tau(n)-1  AND  zimin_index([[0]]_n) < n (avoids Z_n)
def test_witness_for_corollary_1():
    def L(n):
        if n == 1:
            return 1
        return tau(n - 1) * (L(n - 1) + 1)

    for n in [1, 2, 3, 4, 5]:
        w = counter_of_order_n(0, n)
        length = len(w)
        zi = zimin_index(w)
        print("n={}:  length={:>4}   tau(n)-1={:>4}   L_n={:>4}   "
              "zimin_index={}   avoids Z_{}={}   =>  f({},{}) > {}".format(
            n, length, tau(n) - 1, L(n), zi, n, zi < n, n, 2 * n - 1, length))

# test_witness_for_corollary_1()

"""Zimin patterns and avoidable patterns"""


########################################################################################################################
########################## Zimin patterns: Zimin type and Zimin index of a word x ######################################
########################## Source: Searching for Zimin patterns by Rytter ##############################################

def zimin_type(x):
    """Compute the Zimin Type of word x. Matching a Zimin pattern in a word x"""
    x = [None] + x  # fix 3: pad so x[1] is the first char
    m = len(x) - 1
    b = [0] * (m + 1)  # fix 1 & 2: three separate, pre-sized lists
    ztype = [0] * (m + 1)
    sb = [0] * (m + 1)
    t = s = 0
    b[1] = 0
    ztype[0] = 0
    b[0] = -1
    ztype[1] = 1

    for i in range(2, len(x)):
        # Compute b[i]
        while t >= 0 and x[t + 1] != x[i]:
            t = b[t]
        t = t + 1
        b[i] = t
        # Compute s(=sb[i])
        while s >= 0 and (2 * s + 1 >= i or x[s + 1] != x[i]):
            s = b[s]
        s = s + 1
        # Enforce the condition for shortest border and fall back if needed
        while 2 * s >= i:
            s = b[s]
        sb[i] = s
        # Compute ztype[i]
        ztype[i] = ztype[s] + 1
    return ztype


def zimin_index(x):
    """Compute the Zimin Index of a word x. Encountering a Zimin pattern in a word x"""
    best = 0
    for start in range(len(x)):
        ztype = zimin_type(x[start:])
        best = max(best, max(ztype))
    return best


########################################################################################################################
######################### Pattern: avoidable or not on words of infinite length? #######################################
######################### Source: Lothaire, Algebraic Combinatorics on Words     #######################################

def pairs(p):
    """Return list of pairs of consecutive elements in p."""
    list_of_pairs = []
    for i in range(len(p) - 1):
        list_of_pairs.append((p[i], p[i + 1]))
    return list_of_pairs


def nonempty_subsets(elements):
    """Return all non-empty subsets of a set of elements iteratively."""
    subsets = []
    elements = list(elements)
    n = len(elements)
    for i in range(1, 1 << n):
        subset = {elements[j] for j in range(n) if (i & (1 << j))}
        subsets.append(subset)
    return subsets


def adjacency_graph(p):
    """Build bipartite graph from pattern p and find connected components."""
    graph = {}
    for x in p:
        graph.setdefault((x, "L"), set())
        graph.setdefault((x, "R"), set())
    for a, b in pairs(p):
        graph[(a, "L")].add((b, "R"))
        graph[(b, "R")].add((a, "L"))
    return graph


def reachable(graph, starts):
    """Compute all nodes in the connected component of the start nodes."""
    visited = set(starts)
    stack = list(starts)
    while stack:
        node = stack.pop()
        for neighbor_node in graph.get(node, ()):
            if neighbor_node not in visited:
                visited.add(neighbor_node)
                stack.append(neighbor_node)
    return visited


def is_free_set(p, f, graph=None):
    """Check whether the set f is free in pattern p."""
    if graph is None:
        graph = adjacency_graph(p)
    components = reachable(graph, [(x, "L") for x in f])
    c_r = {x for x, side in components if side == "R"}
    return set(f).isdisjoint(c_r)


def free_sets(p):
    """Check if the pattern p is free."""
    graph = adjacency_graph(p)
    return [f for f in nonempty_subsets(set(p)) if is_free_set(p, f, graph)]


def is_reducible(p):
    """ Check if the pattern p is reducible using recursion and memoization."""
    memo = {}

    def rec(pattern):
        key = frozenset(pattern)
        if key in memo:
            return memo[key]
        if len(pattern) == 0:
            memo[key] = True
            return True
        result = False
        fsets = free_sets(pattern)
        for f in fsets:
            q = [x for x in pattern if x not in f]
            if rec(q):
                result = True
                break
        memo[key] = result
        return result

    return rec(p)


def is_avoidable(p):
    """pattern reducible iff pattern unavoidable."""
    return "unavoidable" if is_reducible(p) else "avoidable"


############################################# test #####################################################################
if __name__ == "__main__":
    print("Zimin Type of the word baaabaaa:", zimin_type(list("baaabaaa"))[-1])
    print("Zimin Index of the word baaabaaa:", zimin_index(list("baaabaaa")))
    print("The pattern abacdbaeabdcdbd is:", is_avoidable(list("abacdbaeabdcdbd")))

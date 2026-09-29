from pysat.solvers import Solver
from itertools import count
from zimin import is_free_set
"""
  SAT-Encoding of Loraithes reduction algorithm for arbitrary patterns:
  p is unavoidable  <=>  p can be reduced to the empty word by successively deleting free sets.
  CNF formula is satisfiable  <=>  p is reducible  <=>  p is unavoidable.
"""

######################################## encoding of the cnf ############################
"""
Build the CNF formula for the SAT solver. 
The CNF is satisfiable iff the pattern is reducible (unavoidable).

States and steps:
state i = 0....t, where t = number of distinct letters in the pattern.
step i = 0....t, where step i is the deletion of letters (at least one letter) in state i to get state i+1.

Variables:
pres[i][x] = True if letter x is present in state i, False if deleted
rL[i][x] = True if in step i, node (x,L) is reachable from some node (y,R) for y deleted in step i
rR[i][x] = True if in step i, node (x,R) is reachable from some node (y,L) for y deleted in step i

"x is deleted in step i" = pres[i][x] and not pres[i+1][x]

Rules = Clauses:
R1: every letter x is present in state 0; 
    clause: pres[0][x]
    
R2: every letter x is deleted in state t; 
    clause: not pres[t][x]
    
R3: if letter x is deleted in step i, then x cannot be present in state i+1; 
    clause: pres[i+1][x] -> pres[i][x] <=> not pres[i+1][x] or pres[i][x]
    
R4: the walk starts at the left copy of every deleted letter x in step i;
    clause: (x deleted in step i) -> rL[i][x] <=> not pres[i][x] or pres[i+1][x] or rL[i][x]
    
R5: the walk must not reach the right copy of a deleted letter x in step i;
    clause: (x deleted in step i) -> not rR[i][x] <=> not pres[i][x] or pres[i+1][x] or not rR[i][x]
    
R6: for positions j < k with letters u = p[j], v = p[k] and
                         S = letters between them:
                         the edge (u,L) — (v,R) exists in state i if u and v are present
                         and every letter in S is deleted. The walk follows it both ways:
                         (u, v present and S deleted and rL[i][u]) -> rR[i][v]
                         (u, v present and S deleted and rR[i][v]) -> rL[i][u]
                         clauses: not pres[i][u] or not pres[i][v] or OR over all s in S of pres[i][s] or not rL[i][u] or rR[i][v]
                                  not pres[i][u] or not pres[i][v] or OR over all s in S of pres[i][s] or not rR[i][v] or rL[i][u]
"""


def candidate_edges(p):
    """(u, v, letters in between) for all position pairs that can become neighbors."""
    edges = set()
    for i in range(len(p)):
        between = set()
        for j in range(i + 1, len(p)):
            u, v = p[i], p[j]
            if u not in between and v not in between:
                edges.add((u, v, frozenset(between)))
            between.add(p[j])
            if p[i] in between:
                break
    return edges


def encode(p):
    alph = sorted(set(p), key=p.index)
    t = len(alph)
    new = count(1)
    pres = [{x: next(new) for x in alph} for _ in range(t + 1)]
    rL = [{x: next(new) for x in alph} for _ in range(t)]
    rR = [{x: next(new) for x in alph} for _ in range(t)]
    cls = []

    for x in alph:
        cls.append([pres[0][x]])  # R1
        cls.append([-pres[t][x]])  # R2
        for i in range(t):
            cls.append([-pres[i + 1][x], pres[i][x]])  # R3

    edges = candidate_edges(p)
    for i in range(t):
        p = pres[i]
        for x in alph:
            deleted = [-p[x], pres[i + 1][x]]  # condition "x deleted in step t"
            cls.append(deleted + [rL[i][x]])  # R4
            cls.append(deleted + [-rR[i][x]])  # R5
        for u, v, S in edges:
            active = list(dict.fromkeys([-p[u], -p[v]])) + [p[k] for k in S]
            cls.append(active + [-rL[i][u], rR[i][v]])  # R6: (u,L) -> (v,R)
            cls.append(active + [-rR[i][v], rL[i][u]])  # R6: (v,R) -> (u,L)
    return cls, pres, alph, t


######################################## checking the certificate ######################################################
def check_certificate(p, steps):
    q = list(p)
    for F in steps:
        if not F or not is_free_set(q, F):
            return False
        q = [x for x in q if x not in F]
    return q == []


######################################## SAT solver #######################################
def sat_reduce(p):
    p = list(p)
    if not p:
        return []
    cls, pres, alph, t = encode(p)
    with Solver(bootstrap_with=cls) as solver:
        if not solver.solve():
            return None
        true = {l for l in solver.get_model() if l > 0}
    steps = []
    for i in range(t):
        d = {x for x in alph if pres[i][x] in true and pres[i + 1][x] not in true}
        if d:
            steps.append(d)
    if not check_certificate(p, steps):
        print("Error: certificate does not reduce the pattern to empty.")
        return None
    return steps


def is_avoidable(p):
    """True: p is irreducible -> avoidable; False: p is reducible -> unavoidable."""
    return sat_reduce(p) is None


######################################## testing the SAT solver ########################################################
def test(p):
    print("Testing pattern:", p)
    steps = sat_reduce(p)
    if steps is None:
        print("Pattern is avoidable (irreducible).")
    else:
        print("Pattern is unavoidable (reducible). Deletion steps:", steps)


test("abacbdge")

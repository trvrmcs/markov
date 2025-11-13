from typing import Iterable, Callable, Iterator


import math
from markov import (
    hot,
    cold,
    InitialProbabilities,
    TransitionProbabilities,
    ObservationLikelihoods,
    Temperature,
    Observation,
    STATES,
)
from itertools import product
from fractions import Fraction

type Alpha = dict[Temperature, Fraction]
type V = dict[Temperature, Fraction]
type Backpointer = dict[Temperature, Temperature] | dict[Temperature, None]  # I think?

ZERO = Fraction(0, 1)
ONE = Fraction(1, 1)

_sum = sum


def sum(it: Iterable[Fraction]) -> Fraction:
    return _sum(it, ZERO)


def prod(it: Iterable[Fraction]) -> Fraction:
    return math.prod(it, start=ONE)


def argmax[T](ls: Iterable[T], f: Callable[[T], Fraction]) -> T:
    return max(ls, key=f)


def p_observations_given_states(
    B: ObservationLikelihoods,
    states: list[Temperature],
    observations: list[Observation],
) -> Fraction:
    return prod(
        [
            B[state][observation]
            for state, observation in (zip(states, observations, strict=True))
        ]
    )


def p_states(
    pi: InitialProbabilities, a: TransitionProbabilities, states: list[Temperature]
) -> Fraction:
    assert len(states)
    return pi[states[0]] * prod(
        [a[previous][state] for state, previous in zip(states[1:], states[:-1])]
    )


def brute_force_most_likely_sequence(
    pi: InitialProbabilities,
    a: TransitionProbabilities,
    b: ObservationLikelihoods,
    observations: list[Observation],
):
    return max(
        [list(sequence) for sequence in product(STATES, repeat=len(observations))],
        key=lambda states: p_states(pi, a, states)
        * p_observations_given_states(b, states, observations),
    )


def first_alpha(
    b: ObservationLikelihoods, pi: InitialProbabilities, o: Observation
) -> Alpha:
    """
    For each state, the probability of seeing `o` as the first
    observation

    """
    return {state: pi[state] * b[state][o] for state in STATES}


def next_alpha(
    alpha: Alpha, a: TransitionProbabilities, b: ObservationLikelihoods, o: Observation
) -> Alpha:
    """
    Given the last `alpha` the probability of seeing observation `o` for each state.
    """
    return {
        current: sum(alpha[prev] * a[prev][current] for prev in STATES) * b[current][o]
        for current in STATES
    }


def forward(
    pi: InitialProbabilities,
    a: TransitionProbabilities,
    b: ObservationLikelihoods,
    observations: list[Observation],
) -> Iterator[Alpha]:
    assert len(observations)
    first = observations[0]
    remaining = observations[1:]

    alpha = first_alpha(b, pi, first)

    for o in remaining:
        yield alpha
        alpha = next_alpha(alpha, a, b, o)
    yield alpha


def first_v(b: ObservationLikelihoods, pi: InitialProbabilities, o: Observation) -> V:
    # Exactly the same as `first_alpha`
    return {cold: pi[cold] * b[cold][o], hot: pi[hot] * b[hot][o]}


def next_v(
    v: V, a: TransitionProbabilities, b: ObservationLikelihoods, o: Observation
) -> V:
    """
    Identical to `next_alpha` except we use `max` rather than `sum` over previous path
    probabilities
    """
    return {
        current: max(v[prev] * a[prev][current] * b[current][o] for prev in STATES)
        for current in STATES
    }


def virterbi(
    pi: InitialProbabilities,
    a: TransitionProbabilities,
    b: ObservationLikelihoods,
    observations: list[Observation],
) -> Iterator[V]:
    """
    This yields the matrix `virterbi` from Figure A.9

    """
    assert len(observations)
    first = observations[0]
    remaining = observations[1:]

    v = first_v(b, pi, first)

    for o in remaining:
        yield v
        v = next_v(v, a, b, o)
    yield v


def next_backpointer(
    v_previous: V, a: TransitionProbabilities, b: ObservationLikelihoods, o: Observation
) -> Backpointer:
    return {
        s: argmax(STATES, lambda s_: v_previous[s_] * a[s_][s] * b[s][o])
        for s in STATES
    }


def backpointers(
    vs: list[V],
    a: TransitionProbabilities,
    b: ObservationLikelihoods,
    observations: list[Observation],
) -> Iterator[Backpointer]:
    """
    So at any given time t,
    the Backpointer is a mapping from states to most likely previous states.
    """

    bp: Backpointer = {state: None for state in STATES}

    for v, o in zip(vs[:-1], observations[1:], strict=True):
        # Note we use virterbi[t-1]
        yield bp

        bp = next_backpointer(v, a, b, o)

    yield bp


def bestpath(
    pi: InitialProbabilities,
    a: TransitionProbabilities,
    b: ObservationLikelihoods,
    observations: list[Observation],
) -> list[Temperature]:
    vs = list(virterbi(pi, a, b, observations))

    _backpointers = list(backpointers(vs, a, b, observations))

    def _inner() -> Iterator[Temperature]:
        bestpathpointer: Temperature = max(vs[-1].items(), key=lambda pair: pair[1])[0]

        state: Temperature | None = bestpathpointer

        for bp in reversed(list(backpointers(vs, a, b, observations))):
            assert state is not None
            yield state
            state = bp[state]

        assert state is None
        # We've arrived at the beginning.

    return list(reversed(list(_inner())))

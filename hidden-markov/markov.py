from fractions import Fraction
import random

from enum import Enum
from typing import Iterator

ONE = Fraction(1, 1)


class Temperature(Enum):
    cold = "cold"
    hot = "hot"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


# Type aliases
type Observation = int
type InitialProbabilities = dict[Temperature, Fraction]
type TransitionProbabilities = dict[Temperature, dict[Temperature, Fraction]]
type ObservationLikelihoods = dict[Temperature, dict[Observation, Fraction]]


# constants
cold, hot = Temperature.cold, Temperature.hot

STATES = [cold, hot]


#
def weighted_choice[T](d: dict[T, Fraction]) -> T:
    assert sum(d.values()) == ONE
    population, weights = zip(*d.items())
    return random.choices(population, weights)[0]


OBSERVATIONS: set[Observation] = {1, 2, 3}


class Markov:
    def __init__(self, a: TransitionProbabilities, pi: InitialProbabilities):
        self.a = a

        assert set(a.keys()) == set(STATES)
        for value in a.values():
            assert set(value.keys()) == set(STATES)
            assert sum(value.values()) == 1

        assert set(pi.keys()) == set(STATES)

        assert sum(pi.values()) == 1
        self.state = weighted_choice(pi)

    def __iter__(self) -> Iterator[Temperature]:
        return self

    def __next__(self) -> Temperature:
        self.state = weighted_choice(self.a[self.state])

        return self.state


class HiddenMarkov:
    def __init__(self, markov: Markov, b: ObservationLikelihoods):
        self.markov = markov

        self.b = b

        assert set(b.keys()) == set(markov.a.keys())
        for value in b.values():
            assert set(value.keys()) == OBSERVATIONS
            assert sum(value.values()) == 1

    def __iter__(self) -> Iterator[Observation]:
        return self

    def __next__(self) -> Observation:
        state = next(self.markov)
        return weighted_choice(self.b[state])

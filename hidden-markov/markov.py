from fractions import Fraction
import random
 
from enum import Enum
from typing import Any 


class Temperature(Enum):
    cold = "cold"
    hot = "hot"

    def __str__(self) -> str:
        return self.value
    def __repr__(self) -> str:
        return self.value
    


cold, hot = Temperature.cold, Temperature.hot

STATES = [cold, hot]


ICE_CREAMS_EATEN = [1, 2, 3]


def weighted_choice(d: dict[Any, Fraction]):
    population, weights = zip(*d.items())
    return random.choices(population, weights)[0]


class Markov:
    def __init__(
        self,
        a: dict[
            Temperature, dict[Temperature, Fraction]
        ],  # state transition probabilities
        pi: dict[Temperature, Fraction],  # Initial state probabilities
    ):
        self.a = a

        assert set(a.keys()) == set(STATES)
        for value in a.values():
            assert set(value.keys()) == set(STATES)
            assert sum(value.values()) == 1

        assert set(pi.keys()) == set(STATES)

        assert sum(pi.values()) == 1
        self.state = weighted_choice(pi)

    def __iter__(self):
        return self

    def __next__(self):
        self.state = weighted_choice(self.a[self.state])

        return self.state


class HiddenMarkov:
    def __init__(self, markov: Markov, b: dict[Temperature, dict[int, Fraction]]):
        self.markov = markov

        self.b = b

        assert set(b.keys()) == set(markov.a.keys())
        for value in b.values():
            assert set(value.keys()) == set(ICE_CREAMS_EATEN)
            assert sum(value.values()) == 1

    def __iter__(self):
        return self

    def __next__(self):
        state = next(self.markov)
        return weighted_choice(self.b[state])

from markov import (
    hot,
    cold,
    InitialProbabilities,
    TransitionProbabilities,
    ObservationLikelihoods,
)
from fractions import Fraction


A: TransitionProbabilities = {
    cold: {
        cold: Fraction(5, 10),
        hot: Fraction(5, 10),
    },
    hot: {
        cold: Fraction(4, 10),
        hot: Fraction(6, 10),
    },
}
 
B: ObservationLikelihoods = {
    cold: {
        1: Fraction(5, 10),
        2: Fraction(4, 10),
        3: Fraction(1, 10),
    },
    hot: {
        1: Fraction(2, 10),
        2: Fraction(4, 10),
        3: Fraction(4, 10),
    },
}

# Initial state probabilities

PI: InitialProbabilities = {cold: Fraction(2, 10), hot: Fraction(8, 10)}

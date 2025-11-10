from typing import Iterable 
from itertools import islice 


from markov  import Temperature, Fraction, hot, cold

def forward_algorithm(
    pi: dict[Temperature, Fraction],
    a: dict[Temperature, dict[Temperature, Fraction]],
    b: dict[Temperature, dict[int, Fraction]],
    observations: Iterable,
):
    i = iter(observations)
    for o in islice(i, 0, 1):
        alpha = {cold: pi[cold] * b[cold][o], hot: pi[hot] * b[hot][o]}
        yield (o, alpha)

    for o in i:
        alpha = {
            cold: (+alpha[hot] * a[hot][cold] + alpha[cold] * a[cold][cold])
            * b[cold][o],
            hot: (alpha[hot] * a[hot][hot] + alpha[cold] * a[cold][hot]) * b[hot][o],
        }
        yield (o, alpha)



    
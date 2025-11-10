from pathlib import Path

from collections import defaultdict, Counter

import random
import textwrap
from itertools import islice


class WordCounts:
    def __init__(self, words: list[str]) -> None:
        counters1: defaultdict[str, Counter] = defaultdict(lambda: Counter())
        counters2: defaultdict[tuple[str, str], Counter] = defaultdict(
            lambda: Counter()
        )
        counters3: defaultdict[tuple[str, str, str], Counter] = defaultdict(
            lambda: Counter()
        )

        (
            a,
            b,
            c,
        ) = None, None, None
        for d in words + words[:4]:
            if a is not None:
                assert isinstance(a, str)
                assert isinstance(b, str)
                assert isinstance(c, str)
                counters1[a][b] += 1
                counters2[(a, b)][c] += 1
                counters3[(a, b, c)][d] += 1

            a, b, c = b, c, d

        self.counters1 = {**counters1}
        self.counters2 = {**counters2}
        self.counters3 = {**counters3}

    @classmethod
    def from_paths(cls, *sources: Path) -> "WordCounts":
        table = DEFAULT_TRANSLATION_TABLE

        words = [
            word
            for source in sources
            for word in source.read_text().translate(table).split(" ")
        ]
        return WordCounts(words)

    def chain(self, seed: str) -> "VariableChain":
        return VariableChain(self, seed)

    def counter(self, a: str, b: str, c: str, i: int) -> Counter:
        if i == 3:
            if (counter := self.counters3.get((a, b, c))) is None:
                # may be empty, if our chain has produced a triple
                # that doesn't exist in the original text.

                i = 2
        if i == 2:
            if (counter := self.counters2.get((b, c))) is None:
                i = 1
        if i == 1:
            counter = self.counters1[c]
            assert len(counter)

        assert counter is not None
        return counter


class VariableChain:
    "variable-word markov chain"

    def __init__(self, word_counts: WordCounts, seed: str) -> None:
        self.rng = random.Random(x=seed)
        self.word_counts = word_counts

        self.a, self.b, self.c = self.rng.choice(
            list(self.word_counts.counters3.keys())
        )

    def __repr__(self) -> str:
        return f"VariableChain(Elements. Current: '{self.a} {self.b} {self.c}')"

    def __iter__(self):
        return self

    def __next__(self) -> str:
        # First: are we basing our next word on 1,2 or 3 preceding ones?
        a, b, c = self.a, self.b, self.c

        # prefer the 3-tuple version mostly
        i = self.rng.choices([3, 2, 1], weights=[5, 1, 1])[0]

        counter = self.word_counts.counter(a, b, c, i)

        choices, weights = zip(*counter.items())

        d = self.rng.choices(choices, weights)[0]

        self.a, self.b, self.c = self.b, self.c, d

        return self.a

    def random_words(self, count: int) -> list[str]:
        print(len(self.word_counts.counters1))
        words = list(self.word_counts.counters1.keys())

        return self.rng.choices(words, k=count)

    def babble(self, wordcount=150) -> str:
        text = " ".join(islice(self, wordcount))
        return textwrap.fill(text, replace_whitespace=False)


DEFAULT_TRANSLATION_TABLE = str.maketrans(
    {"”": "'", "“": "'", "—": " ", "_": "", "\n": "\n "}
)



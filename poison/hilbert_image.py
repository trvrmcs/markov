from PIL import Image, ImageFilter
from PIL.ImageFile import ImageFile
from typing import Iterator
from collections import defaultdict, Counter
import random
from itertools import islice
from hilbertcurve.hilbertcurve import HilbertCurve
from pathlib import Path


HERE = Path(__file__).parent
SOURCE_PATH = HERE.parent / "images" / "gray.512.png"


def format_me_(x):
    return "some text "


def point_to_index(point):
    x, y = point
    return y * 512 + x


def index_to_point(i):
    y, x = divmod(i, 512)
    return [x, y]


class CurveSwitcher:
    def __init__(self) -> None:
        curve = HilbertCurve(p=9, n=2)

        self.distance_to_index = [
            point_to_index(curve.point_from_distance(distance))
            for distance in range(512 * 512)
        ]

        self.index_to_distance = [
            curve.distance_from_point(index_to_point(index))
            for index in range(512 * 512)
        ]

    def to_hilbert(self, pixels):
        output = [0 for _ in range(512 * 512)]
        for i, pixel in enumerate(pixels):
            distance = self.index_to_distance[i]

            output[distance] = pixel
        return output

    def to_cartesian(self, pixels):
        output = [0 for _ in range(512 * 512)]
        for distance, pixel in enumerate(pixels):
            i = self.distance_to_index[distance]
            assert output[i] == 0
            output[i] = pixel
        return output


class PixelCounts:
    def __init__(self, source: ImageFile, switcher: CurveSwitcher) -> None:
        assert source.size == (512, 512)

        a, b, c = None, None, None
        counters:defaultdict[tuple[int,int,int], Counter] = defaultdict(lambda: Counter())
        hilbert_pixels = switcher.to_hilbert(source.getdata())

        for pixel in hilbert_pixels + hilbert_pixels[:3]:
            if a is not None:
                assert b is not None 
                assert c is not None 
                counters[(a, b, c)][pixel] += 1
            a, b, c = b, c, pixel

        self.counters = counters


def pixel_chain(counts: PixelCounts, seed: str) -> Iterator:
    rng = random.Random(x=seed)
    a, b, c = rng.choice(list(counts.counters.keys()))

    while True:
        yield c
        counter = counts.counters[(a, b, c)]
        choices, weights = zip(*counter.items())
        a = b
        b = c
        c = rng.choices(choices, weights)[0]


class Creator:
    def __init__(self, source: Path):
        switcher = CurveSwitcher()
        source_image = Image.open(source)
        assert source_image.size == (512, 512)
        assert source_image.mode == "L"
        self.counts = PixelCounts(source_image, switcher)
        self.switcher = switcher

    def create(self, seed: str):
        hilbert_pixels = islice(pixel_chain(self.counts, seed), 512 * 512)
        cartesian_pixels = self.switcher.to_cartesian(hilbert_pixels)
        image = Image.frombytes("L", (512, 512), bytes(cartesian_pixels))
        return image
        blurred = image.filter(ImageFilter.GaussianBlur(2))
        return blurred

from pygef import ParseGEF
import numpy as np
import os
import cProfile

cwd = os.path.dirname(__file__)


def main():
    for _ in range(0, 1000):
        gef = ParseGEF("pygef/files/example.gef")


if __name__ == "__main__":
    main()

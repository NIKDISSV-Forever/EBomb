import argparse

import EBomb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--targets', '-t', type=str, nargs='+', default=[])
    parser.add_argument('--threads-count', '-tc', type=int)
    parser.add_argument('--proxy', action=argparse.BooleanOptionalAction)
    parser.add_argument('--forever', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--verbose', action=argparse.BooleanOptionalAction, default=True)
    EBomb.EBomb(**parser.parse_args().__dict__)


if __name__ == '__main__':
    main()

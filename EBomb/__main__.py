import argparse

import EBomb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--targets', '-t', type=str, nargs='+')
    parser.add_argument('--threads-count', '-tc', type=int)
    parser.add_argument('--proxy', action=argparse.BooleanOptionalAction)
    parser.add_argument('--forever', '-f', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--verbose', '-v', action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()
    print(args)
    EBomb.EBomb(**args.__dict__)


if __name__ == '__main__':
    main()

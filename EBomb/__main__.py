import argparse

import EBomb

if not hasattr(argparse, 'BooleanOptionalAction'):
    class BooleanOptionalAction(argparse.Action):
        def __init__(self, option_strings, dest, default=None, type=None,
                     choices=None, required=False, help=None, metavar=None):

            _option_strings = []
            for option_string in option_strings:
                _option_strings.append(option_string)
                if option_string.startswith('--'):
                    option_string = '--no-' + option_string[2:]
                    _option_strings.append(option_string)
            if help is not None and default is not None and default is not argparse.SUPPRESS:
                help += " (default: %(default)s)"
            super().__init__(
                option_strings=_option_strings,
                dest=dest,
                nargs=0,
                default=default,
                type=type,
                choices=choices,
                required=required,
                help=help,
                metavar=metavar)

        def __call__(self, parser, namespace, values, option_string=None):
            if option_string in self.option_strings:
                setattr(namespace, self.dest, not option_string.startswith('--no-'))

        def format_usage(self):
            return ' | '.join(self.option_strings)


    argparse.BooleanOptionalAction = BooleanOptionalAction


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('targets', type=str, nargs='+',
                        help='Email addresses separated by spaces.')
    parser.add_argument('--threads-count', '-tc', type=int)
    parser.add_argument('--proxy', action=argparse.BooleanOptionalAction, help='Use proxy.')
    parser.add_argument('--forever', action=argparse.BooleanOptionalAction, default=True,
                        help='Run forever, otherwise only one circle.')
    parser.add_argument('--verbose', action=argparse.BooleanOptionalAction, default=True,
                        help='Display something on the screen.')
    args = parser.parse_args().__dict__
    tc = args.pop('threads_count')
    EBomb.EBomb(**args).start(tc)


if __name__ == '__main__':
    main()

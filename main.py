import argparse

from boostnote import BoostnoteCollection

def boostnote_stats(args):
    col = BoostnoteCollection.from_dir(args.path)
    print(col.stats())

def argparse_install_boostnote_stats(parser: argparse.ArgumentParser):
    parser.add_argument('path')

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='cmd')

    boostnote_stats_parser = subparsers.add_parser('boostnote-stats')
    argparse_install_boostnote_stats(boostnote_stats_parser)

    args = parser.parse_args()

    if args.cmd == 'boostnote-stats':
        boostnote_stats(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


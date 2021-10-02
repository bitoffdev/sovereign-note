import argparse

from boostnote import BoostnoteCollection


def boostnote_stats(args):
    col = BoostnoteCollection.from_dir(args.path)
    print(col.stats())


def argparse_install_boostnote_stats(parser: argparse.ArgumentParser):
    parser.add_argument("path")


def argparse_install_boost2jex(parser: argparse.ArgumentParser):
    parser.add_argument("path")


def argparse_install_jex2boost(parser: argparse.ArgumentParser):
    parser.add_argument("path")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")

    boostnote_stats_parser = subparsers.add_parser("boostnote-stats")
    argparse_install_boostnote_stats(boostnote_stats_parser)

    boost2jex_parser = subparsers.add_parser("boost2jex")
    argparse_install_boost2jex(boost2jex_parser)

    jex2boost_parser = subparsers.add_parser("jex2boost")
    argparse_install_jex2boost(jex2boost_parser)

    args = parser.parse_args()

    if args.cmd == "boostnote-stats":
        boostnote_stats(args)
    elif args.cmd == "boost2jex":
        import convert_boostnote_to_jex as boost2jex
        boost2jex.main(args.path)
    elif args.cmd == "jex2boost":
        import convert_jex_to_boostnote as jex2boost
        jex2boost.main(args.path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


import argparse
import logging

from . import convert_boostnote_to_jex as boost2jex
from . import convert_jex_to_boostnote as jex2boost
from .boostnote import BoostnoteCollection
from .joplin import JoplinTarStore, store_get_stats

logger = logging.getLogger(__name__)


def argparse_install_boostnote_stats(parser: argparse.ArgumentParser):
    parser.add_argument(
        "path", help="Path to the parent directory containing boostnote.json"
    )


def argparse_install_jexstats(parser: argparse.ArgumentParser):
    parser.add_argument("path", help="Path to the Joplin JEX file")


def argparse_install_boost2jex(parser: argparse.ArgumentParser):
    parser.add_argument(
        "path", help="Path to the parent directory containing boostnote.json"
    )


def argparse_install_jex2boost(parser: argparse.ArgumentParser):
    parser.add_argument("path", help="Path to the Joplin JEX file")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")

    boostnote_stats_parser = subparsers.add_parser(
        "booststats", help="Display statistics about a Boost Note directory and exit."
    )
    argparse_install_boostnote_stats(boostnote_stats_parser)

    jexstats_parser = subparsers.add_parser(
        "jexstats", help="Display statistics about a Joplin JEX file and exit."
    )
    argparse_install_jexstats(jexstats_parser)

    boost2jex_parser = subparsers.add_parser(
        "boost2jex", help="Convert a Boost Note Legacy directory to a Joplin JEX file"
    )
    argparse_install_boost2jex(boost2jex_parser)

    jex2boost_parser = subparsers.add_parser(
        "jex2boost", help="Convert a Joplin JEX file to a Boost Note Legacy directory"
    )
    argparse_install_jex2boost(jex2boost_parser)

    args = parser.parse_args()

    if args.cmd == "booststats":
        col = BoostnoteCollection.from_dir(args.path)
        print(col.stats())
    elif args.cmd == "jexstats":
        col = JoplinTarStore(args.path)
        print(store_get_stats(col))
    elif args.cmd == "boost2jex":
        boost2jex.main(args.path)
    elif args.cmd == "jex2boost":
        jex2boost.main(args.path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

import enum
import json
import os
import tempfile
from pathlib import Path

import cson

from sovereign_note import convert_boostnote_to_jex as boost2jex
from sovereign_note import convert_jex_to_boostnote as jex2boost


class FileComparison(enum.Enum):
    EQUAL = 1
    DIFFERENT = 2
    IGNORE = 3


def get_relpaths(base):
    paths = set()
    for dirname, _, leaves in os.walk(base):
        for leaf in leaves:
            paths.add(os.path.relpath(os.path.join(dirname, leaf), base))
    return paths


def cmpfiles(ax, bx):
    if ax[-5:] == ".cson":
        with open(ax) as fh:
            acontents = cson.load(fh)
        with open(bx) as fh:
            bcontents = cson.load(fh)
        return (
            FileComparison.EQUAL
            if recdiff(acontents, bcontents)
            else FileComparison.DIFFERENT
        )
    elif ax[-5:] == ".json":
        with open(ax) as fh:
            acontents = json.load(fh)
        with open(bx) as fh:
            bcontents = json.load(fh)
        return (
            FileComparison.EQUAL
            if recdiff(acontents, bcontents)
            else FileComparison.DIFFERENT
        )
    else:
        return FileComparison.IGNORE


def recdiff(a, b):
    if type(a) != type(b):
        return False
    elif isinstance(a, dict):
        for k, v in a.items():
            if k not in b:
                return False
            # XXX Don't compare the values for the color key, since we know that Joplin does not support colors in folders.
            if k == "color":
                return True
            if not recdiff(v, b[k]):
                return False
        return True
    elif isinstance(a, list):
        if len(a) != len(b):
            return False
        return all(recdiff(a2, b2) for a2, b2 in zip(a, b))
    else:
        return a == b
    raise Exception("Unexpected State")


def assert_equal_boostnote(a, b):
    a_relpaths = get_relpaths(a)
    b_relpaths = get_relpaths(b)
    common_relpaths = a_relpaths & b_relpaths
    result = {}
    for relpath in common_relpaths:
        result[relpath] = cmpfiles(os.path.join(a, relpath), os.path.join(b, relpath))
    assert all(
        x in [FileComparison.EQUAL, FileComparison.IGNORE] for x in result.values()
    )


def test_convert():
    parent = Path(__file__).resolve().parent
    reference_boost = parent / "resources" / "example-boostnote-collection"
    jex_loc = tempfile.mktemp()
    boost_loc = tempfile.mkdtemp()
    # Convert from boostnote to JEX
    boost2jex.main(reference_boost, jex_loc)
    # Convert JEX back to boostnote
    jex2boost.main(jex_loc, boost_loc)
    # Verify that no information was lost in the conversion
    assert_equal_boostnote(reference_boost, boost_loc)

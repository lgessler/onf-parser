# -*- coding: utf-8 -*-
from importlib.metadata import version, PackageNotFoundError

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from onf_parser.parse import parse_file, parse_files, parse_file_string
from onf_parser.models import (
    PlainSentence,
    TreebankedSentence,
    Tree,
    Prop,
    PropArg,
    Coref,
    Name,
    Sense,
    Leaf,
    Sentence,
    Mention,
    Chain,
    Section,
)

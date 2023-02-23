# -*- coding: utf-8 -*-
from pkg_resources import DistributionNotFound, get_distribution

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound

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

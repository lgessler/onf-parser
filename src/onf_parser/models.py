
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class PlainSentence:
    string: str


@dataclass
class TreebankedSentence:
    string: str
    tokens: List[str]


@dataclass
class SpeakerInformation:
    name: Optional[str] = None
    start_time: Optional[str] = None
    stop_time: Optional[str] = None


@dataclass
class Tree:
    tree_string: str


@dataclass
class Leaves:
    raw: str


@dataclass
class Sentence:
    plain_sentence: Optional[PlainSentence] = None
    treebanked_sentence: Optional[TreebankedSentence] = None
    speaker_information: Optional[SpeakerInformation] = None
    tree: Optional[Tree] = None
    leaves: Optional[Leaves] = None


@dataclass
class Mention:
    sentence_id: int
    token_id_range: Tuple[int, int]
    tokens: List[str]


@dataclass
class Chain:
    id: str
    chain_type: str
    mentions: List[Mention]


@dataclass
class Section:
    sentences: List[Sentence]
    chains: Optional[List[Chain]]

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict


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
class PropArg:
    token_id: int
    height: int
    token: str


@dataclass
class Prop:
    label: str
    args: Dict[str, List[PropArg]]


@dataclass
class Coref:
    type: str
    chain_id: str
    token_id_range: Tuple[int, int]
    tokens: List[str]


@dataclass
class Name:
    type: str
    token_id_range: Tuple[int, int]
    tokens: List[str]


@dataclass
class Sense:
    label: str


@dataclass
class Leaf:
    token_id: int
    token: str
    prop: Optional[Prop] = None
    coref: Optional[Coref] = None
    name: Optional[Name] = None
    sense: Optional[Sense] = None


@dataclass
class Sentence:
    plain_sentence: Optional[PlainSentence] = None
    treebanked_sentence: Optional[TreebankedSentence] = None
    speaker_information: Optional[SpeakerInformation] = None
    tree: Optional[Tree] = None
    leaves: Optional[Leaf] = None
    name: Optional[Name] = None


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

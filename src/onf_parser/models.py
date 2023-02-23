from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict


@dataclass
class PlainSentence:
    """
    The untokenized sentence as it originally appeared in the source material, or transcribed with typical
    English orthographic conventions.

    Arguments:
        string: str - the raw sentence string
    """

    string: str


@dataclass
class TreebankedSentence:
    """
    The sentence after it has been enriched with null elements (such as *PRO* for control).

    Arguments:
        string: str - the tokenized and enriched sentence, with a single space between each token.
        tokens: List[str] - for convenience, the tokens which constitute the argument.
    """

    string: str
    tokens: List[str]


@dataclass
class SpeakerInformation:
    """
    A piece of metadata which normally represents a speaker and when they began and stopped talking in a media
    file which the document is sourced from. Note that this field may have different meanings in some subcorpora,
    such as the Bible subcorpus.

    Arguments:
        name: Optional[str] - usually, name of the speaker
        start_time: Optional[str] - usually, decimal-formatted second offset into the media file when speaking began
        stop_time: Optional[str] - usually, decimal-formatted second offset into the media file when speaking stopped
    """

    name: Optional[str] = None
    start_time: Optional[str] = None
    stop_time: Optional[str] = None


@dataclass
class Tree:
    """
    The raw Penn Treebank S-expression which represents the tree for a sentence.

    Attributes:
        tree_string: str - S-expression formatted PTB tree.
    """

    tree_string: str


@dataclass
class PropArg:
    """
    Represents a single argument for a PropBank annotation.

    Attributes:
        token_id: int - 0-indexed offset of the head token of this argument
        height: int - the number of levels up in the tree you need to go relative to `token_id` to find the
                      constituent which corresponds to the argument's projection in the tree.
        tokens: List[str] - for convenience, the tokens which constitute the argument.
    """

    token_id: int
    height: int
    tokens: List[str]


@dataclass
class Prop:
    """
    A representation of a PropBank annotation for a given token. Used by Leaf.

    Attributes:
        label: str - the PropBank label for this annotation
        args: Dict[str, List[PropArg]] - the arguments for the PropBank annotation
    """

    label: str
    args: Dict[str, List[PropArg]]


@dataclass
class Coref:
    """
    Coreference label for a coreferent mention. Used by Leaf.

    Attributes:
        type: str - Coreference type. Attested values are "APPOS HEAD", "APPOS ATTRIB", "IDENT"
        chain_id: str - ID of the chain that the mention belongs to. Cf. Sentence.chains
        token_id_range: Tuple[int, int] - *INCLUSIVE* 0-indexed range of tokens in the sentence which constitute
                                          the mention.
        tokens: List[str] - for convenience, the tokens which constitute the mention
    """

    type: str
    chain_id: str
    token_id_range: Tuple[int, int]
    tokens: List[str]


@dataclass
class Name:
    """
    Named entity recognition label. Used by Leaf.

    Attributes:
        type: str - Entity type. Attested values are:
                   'TIME', 'MONEY', 'PERSON', 'PRODUCT', 'QUANTITY',
                   'ORG', 'DATE', 'LOC', 'FAC', 'CARDINAL', 'LAW',
                   'WORK_OF_ART', 'GPE', 'LANGUAGE', 'PERCENT',
                   'NORP', 'ORDINAL', 'EVENT'
        token_id_range: Tuple[int, int] - *INCLUSIVE* 0-indexed range of tokens in the sentence which constitute
                                          the mention of this entity.
        tokens: List[str] - for convenience, the tokens which constitute the mention
    """

    type: str
    token_id_range: Tuple[int, int]
    tokens: List[str]


@dataclass
class Sense:
    """
    Word sense disambiguation label. Used by Leaf.

    Attributes:
        label: str - WordNet sense label
    """

    label: str


@dataclass
class Leaf:
    """
    Representation of a token containing token- and span-level annotations for propbanking, coreference,
    named entity recognition, and word sense disambiguation.

    Attributes:
        token_id: int - 0-indexed offset of this token in the sentence
        token: str - form of the token as it appears in the tree
        prop: Optional[Prop] - propbanking information
        coref: Optional[Coref] - coreference information
        name: Optional[Name] - NER information
        sense: Optional[Sense] - WSD information
    """

    token_id: int
    token: str
    prop: Optional[Prop] = None
    coref: Optional[Coref] = None
    name: Optional[Name] = None
    sense: Optional[Sense] = None


@dataclass
class Sentence:
    """
    Represents most of the annotations in OntoNotes for a given sentence.

    Attributes:
        plain_sentence: Optional[PlainSentence] - the sentence before processing
        treebanked_sentence: Optional[TreebankedSentence] - the sentence after tokenization and addition of nulls
        speaker_information: Optional[SpeakerInformation] - optional metadata usually describing the speaker
        tree: Optional[Tree] - the Penn Treebank tree for this sentence formatted as an S-expression
        leaves: Optional[List[Leaf]] - contains tokens which contain token- and span-level annotations for NER,
                                       coreference, word sense disambiguation, and propbanking
    """

    plain_sentence: Optional[PlainSentence] = None
    treebanked_sentence: Optional[TreebankedSentence] = None
    speaker_information: Optional[SpeakerInformation] = None
    tree: Optional[Tree] = None
    leaves: Optional[List[Leaf]] = None


@dataclass
class Mention:
    """
    Represents a single mention of an entity within a Chain.

    Attributes:
        sentence_id: int - 0-indexed index of the sentence the mention occurs in in the document
        token_id_range: Tuple[int, int] - *INCLUSIVE* range of tokens which constitute the mention
        tokens: List[str] - for convenience, the tokens which constitute the mention
    """

    sentence_id: int
    token_id_range: Tuple[int, int]
    tokens: List[str]


@dataclass
class Chain:
    """
    Represents a coreference chain for a single entity within a document.

    Attributes:
        id: str - the unique identifier of this chain within the document. Often but not necessarily an integer.
        type: str - either APPOS for apposition, or IDENT for normal coreference
        mentions: List[Mention] - the mentions of the entity forming the chain
    """

    id: str
    type: str
    mentions: List[Mention]


@dataclass
class Section:
    """
    Represents a document in OntoNotes, aka a section.

    Attributes:
        sentences: List[Sentence] - a list of `Sentence` objects containing most annotations
        chains: List[Chain] - a list of `Chain` objecst each describing a single coreference chain
    """

    sentences: List[Sentence]
    chains: Optional[List[Chain]]

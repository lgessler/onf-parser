from glob import glob
import re
from typing import Tuple, List

import onf_parser.models as models

LEAF_ID_PATTERN = re.compile(r"^\s\s\s\s(\d+)\s+(\S.*)$")

ATTRIBUTE_PATTERN = re.compile(r"^\s*(?:(?:[*!]\s)?\s*(\w+): (.*))|(?:\s+!\s+(\w+): (.*))")
PROP_ARG_PATTERN = re.compile(r"^(\S+)\s+(?:\* )?-> (\d+):(\d+),\s+(.*)$")
NONFIRST_PROP_ARG_PATTERN = re.compile(r"^(?:\* )?-> (\d+):(\d+),\s+(.*)")

COREF_PATTERN = re.compile(r"(\w+(?:\s\w+)?)\s+(\S+)\s+(\d+)-(\d+)\s?(.*)$")
NAME_PATTERN = re.compile(r"(\w+)\s+(\d+)-(\d+)\s?(.*)$")


def begins_with(chunk, s):
    return chunk[: len(s)] == s


def parse_plain_sentence(s):
    sentence = " ".join(s.strip() for s in s.split("\n")[2:])
    return models.PlainSentence(sentence)


def parse_treebanked_sentence(s):
    sentence = " ".join(s.strip() for s in s.split("\n")[2:])
    return models.TreebankedSentence(sentence, sentence.split(" "))


def parse_speaker_information(s):
    lines = [l.strip() for l in s.split("\n")[2:]]
    attrs = {}
    for line in lines:
        if begins_with(line, "name:"):
            attrs["name"] = line.split("name: ")[1]
        elif begins_with(line, "start time:"):
            attrs["start_time"] = line.split("start time: ")[1]
        elif begins_with(line, "stop time:"):
            attrs["stop_time"] = line.split("stop time: ")[1]
    return models.SpeakerInformation(**attrs)


def parse_tree(s):
    begin = s.find(" " * 4)
    return models.Tree(s[begin + 4 :])


def parse_extra_attribute_tokens(content_lines, i):
    extra_tokens = []
    while (
        i + 1 < len(content_lines)
        and not re.match(NONFIRST_PROP_ARG_PATTERN, content_lines[i + 1])
        and not re.match(PROP_ARG_PATTERN, content_lines[i + 1])
        and not re.match(ATTRIBUTE_PATTERN, content_lines[i + 1])
    ):
        i += 1
        extra_tokens.append(content_lines[i].strip())
    return i, extra_tokens


def parse_prop(content_lines):
    i = 1
    args = {}
    while i < len(content_lines):
        m = re.match(PROP_ARG_PATTERN, content_lines[i])
        if m is None:
            raise Exception(f"Prop arg line failed to parse: {content_lines[i]}")

        i, extra_tokens = parse_extra_attribute_tokens(content_lines, i)
        key, token_id, height, tokens = m.groups()
        tokens = [tokens] + extra_tokens
        args[key] = [models.PropArg(int(token_id), int(height), tokens)]
        i += 1

        m = re.match(NONFIRST_PROP_ARG_PATTERN, content_lines[i]) if i < len(content_lines) else None
        while i < len(content_lines) and m is not None:
            i += 1
            i, extra_tokens = parse_extra_attribute_tokens(content_lines, i)
            token_id, height, tokens = m.groups()
            tokens = [tokens] + extra_tokens
            args[key].append(models.PropArg(int(token_id), int(height), tokens))

    return models.Prop(content_lines[0].strip(), args)


def parse_coref(content_lines):
    m = re.match(COREF_PATTERN, content_lines[0].strip())
    i, extra_tokens = parse_extra_attribute_tokens(content_lines, 0)
    coref_type, chain_id, start, end, tokens = m.groups()
    tokens = tokens.strip()
    tokens = " ".join([tokens] + extra_tokens)
    start = int(start)
    end = int(end)
    return models.Coref(coref_type, chain_id, (start, end), tokens.split(" "))


def parse_name(content_lines):
    m = re.match(NAME_PATTERN, content_lines[0].strip())
    i, extra_tokens = parse_extra_attribute_tokens(content_lines, 0)
    name_type, start, end, tokens = m.groups()
    tokens = tokens.strip()
    tokens = " ".join([tokens] + extra_tokens)
    start = int(start)
    end = int(end)
    return models.Name(name_type, (start, end), tokens.split(" "))


def parse_sense(content_lines):
    assert len(content_lines) == 1
    return models.Sense(content_lines[0].strip())


def parse_attribute(lines, i):
    line = lines[i]
    m = re.match(ATTRIBUTE_PATTERN, line)
    if m is None:
        raise Exception(f"Expected attribute but couldn't find one: {line}")
    name, content = [x for x in m.groups() if x is not None]
    content_lines = [content]
    while (
        i + 1 < len(lines)
        and re.match(ATTRIBUTE_PATTERN, lines[i + 1]) is None
        and re.match(LEAF_ID_PATTERN, lines[i + 1]) is None
    ):
        i += 1
        content_lines.append(lines[i].strip())
    if name == "prop":
        return name, parse_prop(content_lines), i
    elif name == "coref":
        return name, parse_coref(content_lines), i
    elif name == "name":
        return name, parse_name(content_lines), i
    elif name == "sense":
        return name, parse_sense(content_lines), i
    else:
        raise Exception(f"Unrecognized prop: {name}")


def parse_leaves(s):
    leaves = []

    lines = [l for l in s.strip().split("\n")[2:]]
    leaf = None
    i = 0
    while i < len(lines):
        l = lines[i]
        m = re.match(LEAF_ID_PATTERN, l)
        is_leaf = m is not None
        if is_leaf:
            if leaf is not None:
                leaves.append(leaf)
            token_id, token = m.groups()
            leaf = models.Leaf(int(token_id), token)
        else:
            attribute_kind, attribute, i = parse_attribute(lines, i)
            if attribute_kind == "prop":
                leaf.prop = attribute
            elif attribute_kind == "coref":
                leaf.coref = attribute
            elif attribute_kind == "name":
                leaf.name = attribute
            elif attribute_kind == "sense":
                leaf.sense = attribute
        i += 1
    return leaves


def parse_mention(s):
    # Ignore HEAD and ATTRIB at the beginning for (APPOS)
    s = s[15:].strip()
    i = s.find(" ")
    indexes = s[:i]
    tokens = s[i:].strip().split(" ")
    sentence_id, token_range = indexes.split(".")
    begin, end = token_range.split("-")
    return models.Mention(int(sentence_id), (int(begin), int(end)), tokens)


def parse_chains(s):
    chains = []
    raw_chains = s.split("\n\n")[1:]

    for chain in raw_chains:
        chain = chain.split("\n")
        header = chain[0].strip()
        _, id, type = header.split(" ")
        type = type[1:-1]
        mentions = []

        i = 1
        while i < len(chain):
            mention_lines = [chain[i]]
            while i + 1 < len(chain) and chain[i + 1][:18] == (" " * 18):
                i += 1
                mention_lines.append(chain[i].strip())
            mentions.append(parse_mention(" ".join(mention_lines)))
            i += 1
        chains.append(models.Chain(id=id, type=type, mentions=mentions))

    return chains


CHUNK_PREFIXES = {
    "BREAK": "-" * 120,
    "PLAIN_SENTENCE": "Plain sentence:",
    "TREEBANKED_SENTENCE": "Treebanked sentence:",
    "SPEAKER_INFORMATION": "Speaker information:",
    "TREE": "Tree:",
    "LEAVES": "Leaves:",
}

PARSE_FUNCTIONS = {
    "PLAIN_SENTENCE": parse_plain_sentence,
    "TREEBANKED_SENTENCE": parse_treebanked_sentence,
    "SPEAKER_INFORMATION": parse_speaker_information,
    "TREE": parse_tree,
    "LEAVES": parse_leaves,
}


def recognize_chunk(chunk):
    for ctype, cprefix in CHUNK_PREFIXES.items():
        if begins_with(chunk, cprefix):
            return ctype, chunk
    raise Exception(f"Unrecognized chunk: {chunk}")


def parse_section(s):
    pieces = s.split("=" * 120)
    body = pieces[0].strip()
    tail = pieces[1].strip() if len(pieces) > 1 else None
    # assert tail is None or "Coreference chains for" in tail
    # assert tail is None or len([l for l in tail.split("\n") if l[0:5] == '-----']) == 1, tail
    # if len(pieces) > 2:
    #     raise ValueError(f"More =*120 delimiters than expected: {len(pieces)}")

    raw_chunks = [c.strip() for c in body.split("\n\n")]
    tagged_chunks = [recognize_chunk(c) for c in raw_chunks]

    sentences = []
    parts = {}
    for ctype, chunk in tagged_chunks:
        if ctype == "BREAK":
            if len(parts) > 0:
                sentences.append(models.Sentence(**parts))
                parts = {}
        else:
            parsed = PARSE_FUNCTIONS[ctype](chunk)
            parts[ctype.lower()] = parsed

    chains = parse_chains(tail) if tail is not None else None
    return models.Section(sentences, chains)


def split_sections(s):
    sections = []

    last_break = 0
    while True:
        next_index = s.find("=" * 120, last_break)
        section_break = s.find("-" * 120, next_index)
        if section_break == -1:
            sections.append(s[last_break:])
            break
        else:
            sections.append(s[last_break:section_break])

        last_break = section_break

    return sections


def parse_file_string(s: str) -> List[models.Section]:
    """
    Parse a string that is in the OntoNotes Normal Form format.

    Arguments:
        s - file contents

    Returns:
        A list of Sections contained within that file.
    """
    sections = split_sections(s)
    return [parse_section(sec) for sec in sections]


def parse_file(filepath: str) -> List[models.Section]:
    """
    Parse a single .onf file.

    Arguments:
        filepath: str - the path to the .onf file

    Returns:
        A list of Sections contained within that file.
    """
    with open(filepath, "r") as f:
        return parse_file_string(f.read())


def parse_files(directory_path: str) -> List[Tuple[str, List[models.Section]]]:
    """
    Automatically find all .onf files within a directory and parses them.

    Arguments:
        directory_path: str - the directory under which you wish to recursively search for .onf files

    Returns:
        A list of 2-tuples: the first item is the filepath, and the second item is the list of Sections
        contained within that file.
    """
    parsed = []
    for filepath in sorted(glob(f"{directory_path}/**/*.onf", recursive=True)):
        parsed.append((filepath, parse_file(filepath)))
    return parsed

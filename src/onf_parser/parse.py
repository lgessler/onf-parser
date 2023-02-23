from glob import glob
import re
import onf_parser.models as models


def begins_with(chunk, s):
    return chunk[:len(s)] == s


def parse_plain_sentence(s):
    sentence = s.split("\n")[-1].strip()
    return models.PlainSentence(sentence)


def parse_treebanked_sentence(s):
    sentence = s.split("\n")[-1].strip()
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
    return models.Tree(s[begin + 4:])


def parse_leaves(s):
    return models.Leaves(raw=s)


def parse_mention(s):
    # Ignore HEAD and ATTRIB at the beginning for (APPOS)
    s = s[15:].strip()
    print(s)
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
            while i + 1 < len(chain) and chain[i+1][:18] == (" " * 18):
                i += 1
                mention_lines.append(chain[i].strip())
            mentions.append(parse_mention(" ".join(mention_lines)))
            i += 1
        chains.append(models.Chain(id=id, chain_type=type, mentions=mentions))

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


class UnrecognizedChunkException(Exception):
    def __init__(self, chunk_string, message="Unrecognized chunk string:"):
        self.chunk_string = chunk_string
        super().__init__(message)


def recognize_chunk(chunk):
    for ctype, cprefix in CHUNK_PREFIXES.items():
        if begins_with(chunk, cprefix):
            return ctype, chunk
    raise UnrecognizedChunkException(chunk)


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


def parse_file_string(s):
    sections = split_sections(s)
    return [parse_section(sec) for sec in sections]


def parse_file(filepath):
    with open(filepath, 'r') as f:
        return parse_file_string(f.read())


def parse_files(directory_path):
    parsed = []
    for filepath in sorted(glob(f'{directory_path}/**/*.onf', recursive=True)):
        parsed.append(parse_file(filepath))
    return parsed

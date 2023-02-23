Introduction
============

``onf-parser`` is a lightweight pure Python library for parsing the OntoNotes Normal Form format
(``.onf`` -- cf. `section 6.3 <https://catalog.ldc.upenn.edu/docs/LDC2013T19/OntoNotes-Release-5.0.pdf>`_).


Installation
============
Note that Python >=3.9 is required due to our dependency on ``dataclasses``::

    pip install onf-parser

Usage
=====
There are three top-level functions::

    from onf_parser import parse_files, parse_file, parse_file_string
    # read a single file
    sections = parse_file('ontonotes/some/file.onf')
    # or parse a raw string
    sections = parse_file_string(s)
    # read all .onf files in a single directory
    files = parse_file('ontonotes/')

For each file, a list of ``Section`` objects (which correspond to documents for the purposes of annotation) will
be available::

    files = parse_files("ontonotes/arabic")
    for filepath, sections in files:
        for section in sections:
            coref_chains = section.chains
            for chain in coref_chains:
                print(chain.type)
                print(chain.id)
                print(chain.mentions)
            for sentence in section.sentences:
                print(sentence.plain_sentence)
                print(sentence.treebanked_sentence)
                print(sentence.speaker_information)
                print(sentence.tree)
                print(sentence.leaves)

See `model classes <https://github.com/lgessler/onf-parser/blob/master/src/onf_parser/models.py>`_ for more information.

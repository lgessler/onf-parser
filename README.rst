Introduction
============
``onf-parser`` is a lightweight pure Python library for parsing the OntoNotes Normal Form format
(``.onf`` -- cf. `section 6.3 <https://catalog.ldc.upenn.edu/docs/LDC2013T19/OntoNotes-Release-5.0.pdf>`_).


Installation
============
Note that Python >=3.7 is required due to our dependency on ``dataclasses``.

.. code-block:: bash

   pip install onf-parser

Usage
=====
There are three top-level functions:

.. code-block:: python

   from onf_parser import parse_files, parse_file, parse_file_string
   # read a single file
   sections = parse_file('ontonotes/some/file.onf')
   # or parse a raw string
   sections = parse_file_string(s)
   # read all .onf files in a single directory
   files = parse_file('ontonotes/')

For each file, a list of ``Section`` objects (which correspond to documents for the purposes of annotation) will
be available:

.. code-block:: python

   for filepath, sections in files:
       for section in sections:
           coref_chains = section.chains
           for chain in coref_chains:
               print(chain.type)
               print(chain.id)
               print(chain.mentions)
               for mention in chain.mentions:
                   print(mention.sentence_id)
                   print(mention.tokens)
           for sentence in section.sentences:
               print(sentence.plain_sentence)
               print(sentence.plain_sentence.string)

               print(sentence.treebanked_sentence)
               print(sentence.treebanked_sentence.string)
               print(sentence.treebanked_sentence.tokens)

               print(sentence.speaker_information)
               print(sentence.speaker_information.name)
               print(sentence.speaker_information.start_time)
               print(sentence.speaker_information.stop_time)

               print(sentence.tree)
               print(sentence.tree.tree_string)

               print(sentence.leaves)
               for leaf in sentence.leaves:
                   print(leaf.token)
                   print(leaf.token_id)

                   # NER
                   print(leaf.name)
                   print(leaf.name.type)
                   print(leaf.name.token_id_range)
                   print(leaf.name.tokens)

                   # Coreference
                   print(leaf.coref)
                   print(leaf.coref.type)
                   print(leaf.coref.token_id_range)
                   print(leaf.coref.tokens)

                   # WordNet sense
                   print(leaf.sense)
                   print(leaf.sense.label)

                   # PropBank
                   print(leaf.prop.label)
                   print(leaf.prop)
                   for arg_label, arg_spans in leaf.prop.args.items():
                       print(arg_label)
                       for arg_span in arg_spans:
                           print(arg_span)

See `model classes <https://github.com/lgessler/onf-parser/blob/master/src/onf_parser/models.py>`_ for more information.

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import logging


class Vocabulary(object):
    EOL_ID = 2  # end of line
    _EOL = "_EOL"

    PAD_ID = 1
    _PAD = "_PAD"

    UNK_ID = 0
    _UNK = "_UNK"

    def __init__(self, vocabulary_path):
        self.vocab = None
        self.rev_vocab = None
        self.vocabulary_path = vocabulary_path
        self.build_vocab = False
        self.load_vocabulary(vocabulary_path)
        self.counts = {}

    def get_id(self, token):
        if self.build_vocab:
            if token not in self.vocab:
                self.vocab[token] = len(self.rev_vocab)
                self.rev_vocab.append(token)
                self.counts[token] = 0

            self.counts[token] += 1

            return self.vocab[token]
        else:
            return self.vocab.get(token, Vocabulary.UNK_ID)

    def get_value(self, id):
        if id >= len(self.rev_vocab):
            return str(self._UNK, id)
        return self.rev_vocab[id]

    def load_vocabulary(self, vocabulary_path):
        if vocabulary_path is not None and os.path.isfile(vocabulary_path):
            self.rev_vocab = []
            with open(vocabulary_path, encoding='utf-8', mode='r') as f:
                self.rev_vocab.extend(f.readlines())
            self.rev_vocab = [line.strip('\n') for line in self.rev_vocab]
            self.vocab = dict([(x, y) for (y, x) in enumerate(self.rev_vocab)])
        else:
            self.build_vocab = True
            self.vocab = {Vocabulary._UNK: Vocabulary.UNK_ID, Vocabulary._PAD: Vocabulary.PAD_ID, Vocabulary._EOL: Vocabulary.EOL_ID}
            self.rev_vocab = [Vocabulary._UNK, Vocabulary._PAD, Vocabulary._EOL]

    def finish_vocab(self, min_count):
        if self.build_vocab:
            logging.info("Размер готового словаря {0}.".format(len(self.rev_vocab)))
            self.vocab = {Vocabulary._UNK: Vocabulary.UNK_ID, Vocabulary._PAD: Vocabulary.PAD_ID, Vocabulary._EOL: Vocabulary.EOL_ID}
            self.rev_vocab = [Vocabulary._UNK, Vocabulary._PAD, Vocabulary._EOL]

            for pair in sorted(self.counts.items(), key=lambda x: x[1], reverse=True):
                if pair[1] < min_count:
                    break
                self.vocab[pair[0]] = len(self.rev_vocab)
                self.rev_vocab.append(pair[0])
            logging.info("Size of pruned vocabulary {0}.".format(len(self.rev_vocab)))

            self.save()
            self.build_vocab = False

    def save(self):
        if self.build_vocab:
            with open(self.vocabulary_path, encoding='utf-8', mode='w') as vocab_file:
                vocab_file.write("\n".join(self.rev_vocab))

    def size(self):
        return len(self.vocab)

#!/usr/bin/python3
# -*- coding: utf-8 -*-


import unicodedata
from iso639 import languages
import numpy as np

from src.data.Data import Data


class Dataset(Data):
    def __init__(self, params, original_filename, vocabulary_path=None,
                 only_eval=False, use_eol=False, text_to_eval=None):
        Data.__init__(self, original_filename, vocabulary_path, params, use_eol, text_to_eval)

        self.only_eval = only_eval  # if the file does not have targets
        if text_to_eval is not None:
            self.only_eval = True

    def encode_line(self, line):
        if len(line) == 0:
            return []

        if self.unicode_normalization:
            line = unicodedata.normalize('NFD', line)

        if self.only_eval:
            return [-1] + [self.src_vocab.get_id(token) for token in list(line)]

        split = line.split(' ', 1)
        if len(split) == 1:
            return []

        return [-1 - self.trg_vocab.get_id(split[0])] + [self.src_vocab.get_id(token) for token in list(split[1])]

    def get_batch(self):
        if self.gen is None:
            self.gen = self.get_generator()

        batch_inputs = np.empty((self.max_length, self.batch_size), dtype=np.int)
        batch_outputs = np.empty((self.max_length, self.batch_size), dtype=np.int)
        lengths = np.zeros(self.batch_size, dtype=np.int)
        for i in range(self.batch_size):
            self.increase_batch()
            for j in range(self.max_length):
                src, trg = next(self.gen)
                if src != self.src_vocab.PAD_ID:
                    lengths[i] = j + 1
                batch_inputs[j, i] = src
                batch_outputs[j, i] = trg
        return batch_inputs, batch_outputs, lengths

    def get_target_name(self, id, type="orig"):
        if type == "orig":
            return self.trg_vocab.get_value(id)
        try:
            if len(self.trg_vocab.get_value(id)) == 2:
                l = languages.get(part1=self.trg_vocab.get_value(id))
            elif len(self.trg_vocab.get_value(id)) == 3:
                l = languages.get(part3=self.trg_vocab.get_value(id))

            if type == "iso2":
                lang = l.part1
            elif type == "iso3":
                lang = l.part3
            else:
                lang = l.name
        except Exception:
            lang = self.trg_vocab.get_value(id)

        # some languages do not have ISO-2 for example
        if len(lang) == 0:
            return self.trg_vocab.get_value(id)
        return lang

    def get_source_name(self, id):
        return self.src_vocab.get_value(id)

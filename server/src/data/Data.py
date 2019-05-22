#!/usr/bin/python3
# -*- coding: utf-8 -*-

import abc
import os
import logging

from src.vocab.Vocabulary import Vocabulary


class Data(object):
    def __init__(self, original_filename, vocabulary_path, params=None,
                 use_eol=False, text_to_eval=None):
        self.prepared_data = False
        self.original_filename = original_filename
        self.encoding = 'utf-8'

        if vocabulary_path is None:
            self.vocabulary_path = original_filename
        else:
            self.vocabulary_path = vocabulary_path

        self.batch_number = 0
        self.skip_lines = 0
        self.line_num = 0
        self.use_eol = use_eol
        self.file_finished = False
        self.max_length = params.params.get("max_length")
        self.unicode_normalization = params.params.get("unicode_normalization")
        self.batch_size = params.params.get("batch_size")

        self.src_vocab = Vocabulary(self.vocabulary_path + ".src.vocab")
        self.trg_vocab = Vocabulary(self.vocabulary_path + ".trg.vocab")
        self.gen = None
        self.text_to_eval = text_to_eval

    def prepare_data(self, min_count=0):
        filename = self.original_filename + ".ids"
        if not os.path.isfile(filename):
            if min_count > 0 and self.src_vocab.build_vocab:
                logging.info('Датасет не подготовлен. Подготавливаем словарь...')
                self.src_vocab.finish_vocab(min_count)
                self.trg_vocab.finish_vocab(0)
            logging.info('Датасет ещё не подготовлен. Подготавливаем {0}...'.format(filename))

            with open(filename, encoding=self.encoding, mode='w') as tokens_file:
                counter = 0
                iters = self.file_iterator()
                for elements in iters:
                    tokens_file.write(" ".join(str(x) for x in elements) + "\n")
            self.src_vocab.save()
            self.trg_vocab.save()
            logging.info("Датасет готов.")

        self.prepared_data = True

    def restart(self, new_filename=None, encoding='utf-8'):
        if new_filename is not None:
            self.original_filename = new_filename
            self.encoding = encoding

        self.file_finished = False
        self.line_num = 0
        self.gen = self.get_generator()

    def file_iterator(self):
        if self.prepared_data:
            filename = self.original_filename + ".ids"
            with open(filename, encoding=self.encoding, mode="r") as file:
                for line in file:
                    self.line_num += 1
                    if self.skip_lines > 0:
                        self.skip_lines -= 1
                        continue

                    yield line.split()
        else:
            if self.text_to_eval is None:
                with open(self.original_filename, encoding=self.encoding, mode='r') as data_file:
                    for line in data_file:
                        self.line_num += 1
                        if self.skip_lines > 0:
                            self.skip_lines -= 1
                            continue

                        line = line.strip()
                        if len(line) == 0:
                            continue
                        yield self.encode_line(line)
            else:
                yield self.encode_line(self.text_to_eval)

    @abc.abstractmethod
    def encode_line(self, line):
        return

    def increase_batch(self):
        self.batch_number += 1

    def skip_n_lines(self, skip_lines=0):
        logging.info("Пропущено {0} строк.".format(skip_lines))
        self.skip_lines = skip_lines

    def get_trained_lines(self):
        return self.line_num

    def is_finished(self):
        return self.file_finished

    def get_generator(self):
        iters = self.file_iterator()
        trg = -1
        for elements in iters:

            for x in elements:
                x = int(x)
                if x < 0:
                    # targets are moved by -1
                    trg = -x - 1
                    continue

                yield x, trg

            batch = self.batch_number

            while batch == self.batch_number:
                yield self.src_vocab.PAD_ID, self.trg_vocab.PAD_ID

        self.file_finished = True

        while True:
            yield self.src_vocab.PAD_ID, self.trg_vocab.PAD_ID

    def vocab_size(self):
        return [self.src_vocab.size(), self.trg_vocab.size()]

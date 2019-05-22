#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import time
import os

import numpy as np

from src.nn.BiRNN import Model
from src.vocab.Vocabulary import Vocabulary
from src.data.Dataset import Dataset
from src.params.Parameters import Parameters


class NNHelper(object):
    def __init__(self, sess, trained_model=None, params=None, prepare_train_set=True):
        start = time.time()

        self.session = sess
        self.params = Parameters('PARAMS')

        if trained_model:
            self.params.load_params(trained_model)
            logging.info('Загружается модель {0}'.format(trained_model))
        else:
            self.params = params

        self.train_set = Dataset(self.params, os.path.join('data', self.params.get('corpus_name'), 'train'), only_eval=False)
        self.langs = {}

        with open(os.path.join('data', self.params.get('corpus_name'), 'labels'), 'r') as f:
            for line in f.readlines():
                split = line.strip().split(' ', 1)
                self.langs[split[0]] = split[1]

        if prepare_train_set:
            self.train_set.prepare_data(self.params.get('min_count'))

        self.model = Model(self.session, self.params, self.train_set.vocab_size())

        if trained_model:
            self.model.saver.restore(self.session, os.path.join('models', self.params.get('corpus_name'), trained_model))

        print('Модель подготовлена за {0} секунд'.format(str(int(time.time() - start))))

    def detect_lang(self, text):
        datafile = Dataset(self.params, None, os.path.join('data', self.params.get('corpus_name'), 'train'), text_to_eval=text)

        guesses = np.zeros(self.train_set.vocab_size()[1], np.int)
        total = 0
        while not datafile.is_finished():
            batch_xs, _, lengths = datafile.get_batch()

            outs = self.model.eval(self.session, batch_xs, lengths)

            for j in range(len(outs[0])):
                for i in range(len(outs)):
                    max = outs[i][j]

                    if batch_xs[i][j] == datafile.trg_vocab.PAD_ID:
                        break

                    guesses[max] += 1

                    total += 1
        best = np.argmax(guesses)
        acc = 0
        if total > 0:
            acc = float(guesses[best]) / float(total)

        return datafile.get_target_name(best, type='name'), acc

    def test(self, dataset):
        datafile = Dataset(self.params, os.path.join('data', dataset, 'test'), os.path.join('data', self.params.get('corpus_name'), 'train'))
        datafile.prepare_data(self.params.get('min_count'))
        start = time.time()

        logging.info('Тестирование начато. Датасет для тестирования - {0}.'.format(dataset))
        corr = [0, 0]
        while not datafile.is_finished():
            batch_xs, batch_ys, lengths = datafile.get_batch()

            dropout = 1
            _, out = self.model.run(self.session, batch_xs, batch_ys, lengths, dropout)
            corr = np.sum([corr, out], axis=0)

        logging.info('Тестирование закончено за {0} секунд'.format(str(int(time.time() - start))))

        return corr

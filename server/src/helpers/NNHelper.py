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

        return self.langs[datafile.get_target_name(best, type='orig')], acc

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

    def train(self):
        self.train_set.skip_n_lines(self.params.get('trained_lines'))

        dev = Dataset(self.params, os.path.join('data', self.params.get('corpus_name'), 'dev'), os.path.join('data', self.params.get('corpus_name'), 'train'))
        dev.prepare_data(self.params.get('min_count'))
        start = time.time()
        cycle_time = time.time()
        logging.info('Процесс обучения запущен')
        stop = False
        loss_per_epoch = []
        accuracy_per_epoch = []

        while not stop:
            self.params.params['step'] += 1
            batch_xs, batch_ys, lengths = self.train_set.get_batch()
            l, _ = self.model.run(self.session, batch_xs, batch_ys, lengths, self.params.get('dropout'))
            loss_per_epoch.append(l)

            stop = self.check_stopfile('STOP_IMMEDIATELY')

            if time.strftime('%H') == self.params.get('time_stop'):
                stop = True

            if self.params.get('step') % self.params.get('steps_per_checkpoint') == 0 or stop:
                c_time = time.time()
                corr = [0, 0]

                while not dev.is_finished():
                    dev_batch_xs, dev_batch_ys, lengths = dev.get_batch()

                    dropout = 1
                    _, out = self.model.run(self.session, dev_batch_xs, dev_batch_ys, lengths, dropout)
                    corr = np.sum([corr, out], axis=0)

                result = (corr[0] / corr[1]) * 100
                accuracy_per_epoch.append(float(corr[0]) / float(corr[1]))

                self.params.params['trained_lines'] = self.train_set.get_trained_lines()
                self.model.save(self.session, self.params.get('step'), result)

                print('''Итерация: {0},
                Точность: {1}% {2},
                Времени на шаг: {3} секунд
                Время обучения: {4} минут
                Время: {5}'''.format(self.paramsget('step') * self.params.get('batch_size'),
                                     result,
                                     corr,
                                     (c_time - cycle_time) / self.params.get('steps_per_checkpoint'),
                                     int((time.time() - start) / 60), time.strftime('%H:%M:%S')))

                cycle_time = time.time()

                stop = stop or self.check_stopfile('STOP_MODEL')
                if self.params.get('step') >= self.params.get('max_iters'):
                    stop = True

            if self.train_set.is_finished():
                avg_loss = np.mean(loss_per_epoch)
                avg_test_accuracy = np.mean(accuracy_per_epoch)

                summ = self.sess.run(self.model.performance_summaries, feed_dict={self.model.tf_loss_ph: avg_loss,
                                                                                  self.model.tf_accuracy_ph: avg_test_accuracy})
                self.model.sum_writer.add_summary(summ, self.params.get('epochs'))

                loss_per_epoch.clear()
                accuracy_per_epoch.clear()

                self.params.params["epochs"] += 1
                logging.info("Эпоха {0} начата.".format(self.params.get('epochs')))
                self.train_set.restart()

        print("Обучение закончено за " + str(int(time.time() - start)) + " секунд")


    def check_stopfile(self, filename):
        stop = False
        with open(filename, mode="r") as stp:
            for line in stp:
                if line.strip() == self.params.params["corpus_name"]:
                    logging.info("Stopping training on command from stopfile.")

                    stop = True
                    break

        if stop:
            # remove command from file
            f = open(filename, "r")
            lines = f.readlines()
            f.close()

            f = open(filename, "w")
            for line in lines:
                if line.strip() != self.params.params["corpus_name"]:
                    f.write(line)
            f.close()

        return stop

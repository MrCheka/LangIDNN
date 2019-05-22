import os

import numpy as np
import tensorflow as tf
import time
import logging
import inspect
from tensorflow.contrib import rnn
from tensorflow.contrib import legacy_seq2seq

from src.nn.IModel import IModel


class Model(IModel):
    def __init__(self, sess, params, vocabs_size):
        IModel.__init__(self, vocabs_size)

        self.params = params

        self.batch_size = self.params.get("batch_size")
        self.max_length = self.params.get("max_length")
        self.size = self.params.get("size")
        self.num_layers = self.params.get("num_layers")
        self.learning_rate = self.params.get("learning_rate")
        self.embedding_size = self.params.get("embedding_size")
        self.incorrect = [0] * self.max_length
        self.global_step = 0
        self.corpus_name = self.params.get("corpus_name")
        self.cell_type = self.params.get('cell_type')

        logging.info('''Конфигурация модели:
        количество слоёв - {0}
        количество ячеек - {1}
        размер embedding слоя - {2}
        размер словаря - {3}
        размер входа - {4}
        размер batch - {5}'''.
                     format(self.num_layers,
                            self.size,
                            self.embedding_size,
                            self.vocab_sizes,
                            self.max_length,
                            self.batch_size))

        with tf.variable_scope('forward'):
            forward_cell = self.getMultiRNNCell(self.cell_type, self.num_layers, self.size)

        with tf.variable_scope('backward'):
            backward_cell = self.getMultiRNNCell(self.cell_type, self.num_layers, self.size)

        self.inputs = [tf.placeholder(tf.int32, shape=[None], name="inputs{0}".format(i)) for i in range(self.max_length)]
        self.targets = [tf.placeholder(tf.int32, shape=[None], name="targets{0}".format(i)) for i in range(self.max_length)]

        self.sentence_lengths = tf.placeholder(tf.int64, shape=[None], name="sequence_lengths")
        self.dropout_placeholder = tf.placeholder(tf.float32, shape=[], name="dropout")

        self.word_embeddings = tf.Variable(tf.random_uniform([self.vocab_sizes[0], self.embedding_size], -1.0, 1.0))
        embedded_inputs = [tf.nn.embedding_lookup(self.word_embeddings, input_) for input_ in self.inputs]
        dropped_embedded_inputs = [tf.nn.dropout(i, self.dropout_placeholder) for i in embedded_inputs]

        weights = {
            'out': tf.Variable(tf.random_uniform([2 * self.size, self.vocab_sizes[1]]), name="out-weight")
        }
        biases = {
            'out': tf.Variable(tf.random_uniform([self.vocab_sizes[1]]), name="out-bias")
        }

        logging.getLogger().setLevel(logging.CRITICAL)
        with tf.variable_scope('BiRNN-net'):
            outputs = rnn.static_bidirectional_rnn(forward_cell, backward_cell, dropped_embedded_inputs, sequence_length=self.sentence_lengths, dtype=tf.float32)

        logging.getLogger().setLevel(logging.INFO)

        self.out = []
        self.probs = []
        for o in outputs[0]:
            intermediate_out = tf.matmul(o, weights['out']) + biases['out']
            self.out.append(intermediate_out)
            self.probs.append(tf.nn.softmax(intermediate_out))

        loss = legacy_seq2seq.sequence_loss_by_example(self.out, self.targets, [tf.ones([self.batch_size])] * self.max_length, self.vocab_sizes[1])

        self.cost = tf.reduce_sum(loss) / self.batch_size

        with tf.name_scope('performance'):
            self.tf_loss_ph = tf.placeholder(tf.float32, shape=None, name='loss_summary')
            self.tf_loss_summary = tf.summary.scalar('loss', self.tf_loss_ph)

            self.tf_accuracy_ph = tf.placeholder(tf.float32, shape=None, name='accuracy_summary')
            self.tf_accuracy_summary = tf.summary.scalar('accuracy', self.tf_accuracy_ph)

        self.updates = tf.train.AdamOptimizer(self.learning_rate).minimize(loss)
        self.saver = tf.train.Saver(max_to_keep=0)
        self.performance_summaries = tf.summary.merge([self.tf_loss_summary, self.tf_accuracy_summary])
        self.sum_writer = tf.summary.FileWriter('summaries', sess.graph)

        sess.run(tf.global_variables_initializer())
        logging.info("Нейронная сеть инициализирована.")

    def getLSTMCell(self, size):
        if 'reuse' in inspect.getfullargspec(rnn.LSTMCell.__init__).args:
            return rnn.LSTMCell(size, forget_bias=1.0, reuse=tf.get_variable_scope().reuse)
        else:
            return rnn.LSTMCell(size, forget_bias=1.0)

    def getGRUCell(self, size):
        if 'reuse' in inspect.getfullargspec(rnn.GRUCell.__init__).args:
            return rnn.GRUCell(size, reuse=tf.get_variable_scope().reuse)
        else:
            return rnn.GRUCell(size)

    def getMultiRNNCell(self, cell_type, num_layers, size):
        if (cell_type == 'lstm'):
            return rnn.MultiRNNCell([self.getLSTMCell(size) for _ in range(num_layers)])
        else:
            return rnn.MultiRNNCell([self.getGRUCell(size) for _ in range(num_layers)])

    def feed(self, inputs, sentence_lengths, dropout, targets=None):
        input_feed = {}
        for l in range(self.max_length):
            input_feed[self.inputs[l].name] = inputs[l]
            if targets is not None:
                input_feed[self.targets[l].name] = targets[l]

        input_feed[self.sentence_lengths.name] = sentence_lengths
        input_feed[self.dropout_placeholder.name] = dropout
        return input_feed

    def eval(self, session, inputs, sentence_lengths, langs_mask=None):
        input_feed = self.feed(inputs, sentence_lengths, 1)

        outs = session.run(self.out, input_feed)

        result = np.zeros((self.max_length, self.batch_size), dtype=np.int)
        for j in range(self.batch_size):
            for i in range(self.max_length):
                result[i][j] = np.argmax(outs[i][j])

        return result

    def run(self, session, inputs, targets, sentence_lengths, dropout):
        input_feed = self.feed(inputs, sentence_lengths, dropout, targets=targets)

        cost, out = session.run([self.cost, self.out], input_feed)

        return cost, self.compute_correctness(out, targets)

    def compute_correctness(self, outputs, targets):
        correct = 0
        total = 0
        for j in range(self.batch_size):
            for i in range(self.max_length):
                if np.argmax(outputs[i][j]) == targets[i][j]:
                    correct += 1
                else:
                    self.incorrect[i] += 1

                total += 1
        return [correct, total]

    def save(self, session, step, result):
        directory = "models/" + self.corpus_name
        if not os.path.exists(directory):
            os.makedirs(directory)

        identification = "/BiRNN.%d.step%d.m%d_s%d-l%d.model" % (time.time(), step, self.max_length, self.size, self.num_layers)

        filename = directory + identification

        self.saver.save(session, filename)
        self.params.save_result(result, identification)
        print("Модель сохранена в " + filename)

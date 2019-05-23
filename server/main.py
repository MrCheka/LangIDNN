import tensorflow as tf
import argparse
import logging

from src.helpers.NNHelper import NNHelper
from src.controller.Controller import Controller
from src.params.Parameters import Parameters


def createParser():
    parser = argparse.ArgumentParser(prog='langid_server',
                                     description='''Это серверная часть
                                     идентификатора языка с использованием нейронных сетей''',
                                     epilog='(c) Дипломный проект Байко Станислава Леоновича, ИИ-13, БрГТУ',
                                     add_help=False)

    parent_group = parser.add_argument_group(title='Параметры')
    parent_group.add_argument('--help', '-h', action='help', help='Справка')

    subparsers = parser.add_subparsers(dest='mode',
                                       title='Возможные комманды',
                                       description='Команды, которые должны быть в качестве первого параметра %(prog)s.')

    server_parser = subparsers.add_parser('server',
                                          add_help=False,
                                          help='Запуск программы в режиме сервера',
                                          description='''Запуск в режиме сервера.
                                              В этом режиме программа предоставляет API для идентификации языка.''')

    server_group = server_parser.add_argument_group(title='Параметры')
    server_group.add_argument('--model', '-m', required=True,
                              help='Модель нейронной сети, используемая для идентификации.', metavar='МОДЕЛЬ')
    server_group.add_argument('--address', '-a', default='127.0.0.1',
                              help='Адрес для прослушивания. По умолчанию 127.0.0.1 (localhost)', metavar='АДРЕС')
    server_group.add_argument('--port', '-p', default='8888', help='Порт для прослушивания. По умолчанию 8888.',
                              metavar='ПОРТ')
    server_group.add_argument('--help', '-h', action='help', help='Справка')

    train_parser = subparsers.add_parser('train',
                                         add_help=False,
                                         help='Запуск программы в режиме обучения',
                                         description='''Запуск программы в режиме обучения.
                                             В этом режиме предоставляются возможности для обучения модели нейронной сети.''')

    train_group = train_parser.add_argument_group(title='Параметры')
    train_group.add_argument('--model', '-m', help='Модель нейронной сети для продолжения обучения', metavar='МОДЕЛЬ')
    train_group.add_argument('--dataset', '-d', help='Название датасета, используемого для обучения', metavar='ДАТАСЕТ')
    train_group.add_argument('--unicode', '-u', help='Использовать unicode нормализацию', action='store_true', default=False)
    train_group.add_argument('--size', '-s', help='Размер каждого слоя модели', type=int, default=500)
    train_group.add_argument('--embedding_size', '-e', help='Размер embedding слоя', type=int, default=200)
    train_group.add_argument('--layers', '-l', help='Количество слоёв', type=int, default=1)
    train_group.add_argument('--dropout', help='Вероятность dropout', type=float, default=0.5)
    train_group.add_argument('--learning_rate', help='Минимальная ошибка на валидационной выборке', type=float, default=0.0001)
    train_group.add_argument('--max_iters', help='Максимальное количество итераций', type=int)
    train_group.add_argument('--checkpoint', '-c', help='Количество итераций для сохранения модели', type=int, default=5000)
    train_group.add_argument('--batch_size', '-b', help='Размер порции данных, подаваемых на нейронную сеть', type=int, default=64)
    train_group.add_argument('--time_stop', '-t', help='Количество часов на обучение', type=int)
    train_group.add_argument('--input', '-i', help='Размер входа', type=int, default=200)
    train_group.add_argument('--cell_type', help='Тип ячеек', choices=['lstm', 'gru'], default='gru')
    train_group.add_argument('--help', '-h', action='help', help='Справка')

    test_parser = subparsers.add_parser('test',
                                        add_help=False,
                                        help='Запуск программы в режиме тестирования',
                                        description='''Запуск программы в режиме тестирования
                                            В этом режиме предоставляются возможности для тестирования модели нейронной сети.''')

    test_group = test_parser.add_argument_group(title='Параметры')
    test_group.add_argument('--model', '-m', required=True, help='Модель нейронной сети для тестирования.',
                            metavar='МОДЕЛЬ')
    test_group.add_argument('--dataset', '-d', help='Название датасета, используемого для тестирования', metavar='ДАТАСЕТ')
    test_group.add_argument('--text', '-t', help='Текст для идентификации языка.', metavar='ТЕКСТ')
    test_group.add_argument('--file', '-f', help='Текстовый файл для идентификации языка.', metavar='ФАЙЛ')
    test_group.add_argument('--help', '-h', action='help', help='Справка')

    return parser


def run_server(namespace):
    model = namespace.model
    address = namespace.address
    port = namespace.port

    with tf.Session() as sess:
        contr = Controller(sess, model)
        contr.run(address, port)


def run_train(namespace):
    params = Parameters('PARAMS')

    if namespace.model:
        model = namespace.model
    elif namespace.dataset:
        dataset = namespace.dataset

        params.add_integer('min_count', 0)
        params.add_integer('trained_lines', 0)
        params.add_integer('step', 0)

    if namespace.unicode:
        params.add_bool('unicode_normalization', True)
    if namespace.size:
        params.add_integer('size', namespace.size)
    if namespace.embedding_size:
        params.add_integer('embedding_size', namespace.embedding_size)
    if namespace.layers:
        params.add_integer('num_layers', namespace.layers)
    if namespace.dropout:
        params.add_float('dropout', namespace.dropout)
    if namespace.learning_rate:
        params.add_float('learning_rate', namespace.learning_rate)
    if namespace.max_iters:
        params.add_integer('max_iters', namespace.max_iters)
    if namespace.checkpoint:
        params.add_integer('steps_per_checkpoint', namespace.checkpoint)
    if namespace.batch_size:
        params.add_integer('batch_size', namespace.batch_size)
    if namespace.time_stop:
        params.add_string('time_stop', namespace.time_stop)
    if namespace.input:
        params.add_integer('max_length', namespace.input)
    if namespace.cell_type:
        params.add_string('cell_type', namespace.cell_type)

    with tf.Session() as sess:
        helper = NNHelper(sess, model, params)
        helper.train()


def run_test(namespace):
    if namespace.text:
        text = namespace.text
    elif namespace.file:
        with open(namespace.file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif namespace.dataset:
        dataset = namespace.dataset
    else:
        raise Exception('Не указан текст или файл для идентификации')

    with tf.Session() as sess:
        helper = NNHelper(sess, namespace.model)
        if dataset:
            acc = helper.test(dataset)

            print('Точность определения - {0}% {1}'.format(100*acc[0]/acc[1], acc))
        else:
            lang, acc = helper.detect_lang(text)

            print('Результат:\n')
            print('Язык - {0}'.format(lang))
            print('Точность определения - {0}%'.format(acc*100))


if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args()

    if namespace.mode == 'server':
        run_server(namespace)
    elif namespace.mode == 'train':
        run_train(namespace)
    elif namespace.mode == 'test':
        run_test(namespace)
    else:
        logging.error('Ошибка во время выбора режима работы приложения. Попробуйте ещё раз.')

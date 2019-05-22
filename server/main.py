import tensorflow as tf
import argparse
import logging

from src.helpers.NNHelper import NNHelper
from src.controller.Controller import Controller


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

    return


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

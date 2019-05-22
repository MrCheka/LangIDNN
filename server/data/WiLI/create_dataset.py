import codecs
import pandas as pd

def main():
    x_test = [line.strip() for line in codecs.open('x_test.txt', 'r', 'utf-8')]
    y_test = [line.strip() for line in codecs.open('y_test.txt', 'r', 'utf-8')]
    train = ['%s %s\n' % (y_test[i], value) for i,value in enumerate(x_test)]

    new_train = []
    for i, value in enumerate(train):
        if i % 10 == 0:
            continue
        new_train.append(value)

    with codecs.open('test', 'w', 'utf-8') as f:
        f.writelines(new_train)


def labels():
    data = pd.read_csv('labels.csv', sep=';')
    labels = ['{0} {1}\n'.format(i.Label, i.English) for i in data.itertuples()]

    with codecs.open('labels', 'w', 'utf-8') as f:
        f.writelines(labels)


if __name__ == '__main__':
    labels()
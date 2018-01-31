import random
import subprocess
import sys
import os

from sklearn_crfsuite.metrics import flat_classification_report

base = "/usr/bin/java -Xmx10g -cp stanford-ner-2017-06-09/stanford-ner.jar " \
       "edu.stanford.nlp.ie.crf.CRFClassifier -prop stanford_ner.prop "


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def generate_folds(folds=3):
    sentences = []
    sentence = []
    with open(sys.argv[1]) as f_input:
        for line in f_input:
            if len(line) == 1 and len(sentence) >= 1:
                sentences.append(sentence)
                sentence = []
            elif len(line) > 1:
                parts = line.strip().split('\t')
                sentence.append((parts[0], parts[1]))

    random.shuffle(sentences, random.random)
    print("total", len(sentences))
    print("k_folds: ", folds)
    per_fold = round(len(sentences) / float(folds))
    print("per fold: ", per_fold)
    data_folds = list(chunks(sentences, per_fold + 1))
    for i in range(len(data_folds)):
        fold = data_folds[i]
        with open("fold_" + str(i), "wt") as f_out:
            for sentence in fold:
                for token in sentence:
                    f_out.write(token[0] + '\t' + token[1] + '\n')
                f_out.write('\n')


def run(train_data, test_data, fold):
    print("Training on {} and testing on {}".format(train_data, test_data))
    stanford_crf = "-trainFile corpus/{} " \
                   "-testFile corpus/{} " \
                   "1>tagged_fold_{}.csv " \
                   "2>results_fold_{}.txt " \
                   "-serializeTo model_{}.ser.gz".format(train_data, test_data, fold, fold, fold)
    full_cmd = base + stanford_crf
    print(full_cmd)
    p = subprocess.Popen(full_cmd, shell=True)
    sts = os.waitpid(p.pid, 0)


def evaluate():
    results = ['tagged_fold_0.csv', 'tagged_fold_1.csv', 'tagged_fold_2.csv', 'tagged_fold_3.csv',
               'tagged_fold_4.csv']

    sentences_original = []
    sentences_predicted = []

    for i in range(len(results)):
        with open(results[i], 'rt') as f_input:
            sentence_original = []
            sentence_predicted = []

            for line in f_input:
                line_parts = line.split('\t')
                if len(line_parts) == 3:
                    word, true, predicted = line.split('\t')
                    sentence_original.append(true)
                    sentence_predicted.append(predicted.strip())
                elif len(line_parts) == 1 and line_parts[0] == '\n':
                    sentences_original.append(sentence_original)
                    sentences_predicted.append(sentence_predicted)
                    sentence_original = []
                    sentence_predicted = []

    labels = ['B-LOC', 'I-LOC',
              'B-ORG', 'I-ORG',
              'B-PER', 'I-PER',
              'B-WRK', 'I-WRK']

    results = flat_classification_report(sentences_original, sentences_predicted, digits=3,
                                         labels=labels)
    print(results)


def main():

    # generate_folds(folds=5)

    experiments = [('fold_1_2_3_4', 'fold_0'), ('fold_0_2_3_4', 'fold_1'),
                   ('fold_0_1_3_4', 'fold_2'), ('fold_0_1_2_4', 'fold_3'),
                   ('fold_0_1_2_3', 'fold_4')]

    for fold in range(len(experiments)):
        data = experiments[fold]
        run(data[0], data[1], fold)

    # evaluate()


if __name__ == "__main__":
    main()

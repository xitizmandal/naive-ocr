#!/usr/bin/env python3

import config
from mnist import MNIST
import numpy as np
import matplotlib.pyplot as plt
from ann import HyperParameters, ANN
from featurizer import featurize, one_hot_encoder
from eval import Evaluator, Result
from utils import dump_shit

def load_train():
    mndata = MNIST("./data/mnist/")
    return mndata.load_training()

def convert_prob_to_label(y):
    return np.argmax(y, axis=1).reshape( (len(y), 1) )

def build_model(topology, config, hyperparams, batch_size, epoch, X_train, Y_train):
    ann = ANN(topology, config, hyperparams, epoch)
    print("training using mini batch GD...")
    costs = ann.train_in_batch(X_train, Y_train, batch_size)
    return ann, costs

def evaluate_model(model, num_classes, X_test, Y_test):
    predicted = model.predict(X_test)
    target_label = convert_prob_to_label(Y_test)
    predicted_label = convert_prob_to_label(predicted)
    target = np.ravel(target_label)
    predicted = np.ravel(predicted_label)

    evaluator = Evaluator(num_classes)
    accuracy = evaluator.calculate_accuracy(target, predicted)
    cm, precisions, recalls = evaluator.calculate_metrics(target, predicted)
    precision = np.mean(precisions)
    recall = np.mean(recalls)
    f1 = 2 * precision * recall / (precision + recall)

    return Result(cm, accuracy, precisions, precision, recalls, recall, f1)


def main():
    print("loading mnist dataset...")
    images, labels = load_train()
    N = len(images)
    train_size = 50000
    test_size = N-train_size

    """
    print("shuffling...")
    dataset = list(zip(images, labels))
    np.random.shuffle(dataset)
    images, labels = zip(*dataset)
    """

    X_train = np.array(images[0:train_size] )
    Y_train = np.array(labels[0:train_size] )
    X_train = X_train/255
    Y_train = one_hot_encoder(Y_train)

    X_test = np.array(images[ train_size:N])
    X_test = X_test/255
    Y_test = np.array(labels[ train_size:N])
    Y_test = one_hot_encoder(Y_test)

    # lr, m, lr-decay
    hyperparams = HyperParameters(0.02, 0.8, 0.00001, 0.1)
    topology = [X_train[0].shape[0], 30, 10]
    batch_size = 25
    epoch = 30
    model, costs = build_model(topology, config.SIGMOID_SOFTMAX_CROSSENTROPY,
                               hyperparams, batch_size, epoch,
                               X_train, Y_train)
    plt.plot(costs)
    plt.show()

    result_train = evaluate_model(model, 10, X_train, Y_train)
    print("Train metrics...")
    print(result_train)

    result_test = evaluate_model(model, 10, X_test, Y_test)
    print("Test metrics...")
    print(result_test)

    dump_shit(config.FILE_RESULT, topology, hyperparams,
              train_size, test_size,
              batch_size, epoch,
              result_train, result_test)

    while True:
        inp = input("Predict? y/n :: ")
        if inp == 'n':
            print("Hell yeah! I'm gonna break free...")
            break
        try:
            test = featurize("data/test.jpg")
            predicted = model.predict(test)
            label = convert_prob_to_label(predicted)
            print("Predicted label ==> {}".format(label))
        except FileNotFoundError:
            print("Oh shit! Something's wrong with the test file...")

if __name__ == "__main__":
    main()


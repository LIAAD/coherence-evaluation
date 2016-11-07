"""
========================================================
Topics discovery using LDA
========================================================
"""

# Author: Arian Pasquali

from __future__ import print_function
from time import time
import os
import pickle
import lda
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import logging

N_TOP_WORDS = 10
N_BASE_ITERATIONS = 1500
dataset_name = "20newsgroups"


def main():
    logger.info("Loading features ...")

    f_input_features = open("../../data/processed/20newsgroups-bag-of-words.pkl", "rb")
    f_input_vocab = open("../../data/processed/20newsgroups-vocabulary.pkl", 'rb')

    # open database
    conn = sqlite3.connect('../../data/topics.db')

    c = conn.cursor()

    logger.info("Clear data")

    c.execute('DELETE FROM `topics` WHERE `dataset_name` == "' + dataset_name + '" ')
    conn.commit()

    features = pickle.load(f_input_features)
    feature_names = pickle.load(f_input_vocab)

    f_input_features.close()
    f_input_vocab.close()

    vocab = feature_names

    # n_topics_range = xrange(100,10)
    n_topics_range = [20]

    for n_topics in n_topics_range:

        topics = []
        logger.info("Applying LDA model ...")
        t0 = time()

        n_iterations = N_BASE_ITERATIONS + (n_topics * 10)

        model = lda.LDA(n_topics=n_topics,
                        n_iter=n_iterations,
                        random_state=1)

        model.fit(features)

        logger.info("LDA ready in %0.3fs." % (time() - t0))

        topic_word = model.topic_word_

        topic = {"n_topics": n_topics, "topics": {}}

        for i, topic_dist in enumerate(topic_word):
            topic_words = np.array(vocab)[np.argsort(topic_dist)][:-N_TOP_WORDS - 1:-1]

            logger.info('Topic {}: {}'.format(i, ' '.join(topic_words)))
            ngrams = ' '.join(topic_words)
            doc = (int(i), int(n_topics), dataset_name, ngrams)
            topics.append(doc)

        c.executemany('INSERT INTO `topics`(`topic_id`,`n_topics`,`dataset_name`,`ngrams`) VALUES (?,?,?,?);', topics)

        conn.commit()
        conn.close()

        plot_title = 'Loglikelihoods vs Iterations (n_topics : ' + str(n_topics) + ')'
        plot_filename = "reports/figures/" + str(n_topics) + '_topics_lda_loglikelihoods.png'

        plt.figure()
        plt.plot(model.loglikelihoods_[5:])
        plt.title(plot_title)
        # plt.show()
        plt.savefig(plot_filename)

        logger.info("Plot loglikelihood at " + plot_filename)




if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(__name__)
    # logger.info('making final data set from raw data')

    # not used in this stub but often useful for finding various files
    # project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    # load_dotenv(find_dotenv())

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    main()

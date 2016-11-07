"""
========================================================
Compute topics interpretability
========================================================
"""

# Author: Arian Pasquali

from __future__ import print_function
from topic_coherence import UCI, UMass
import logging
import os
import sqlite3

internal_index = "20newsgroups"
test_es_address = "localhost:9200"

def print_scores(scores):
    logger.info("Results ----------------------------------------")
    for topic in sorted(scores, key=lambda name: name["topic_id"]):
        logger.info('{},{},{},{}'.format(topic["topic_id"],
                                         topic["ngrams"],
                                         topic["scores"]["intrinsic"]["uci"],
                                         topic["scores"]["intrinsic"]["umass"]
                                         ))

def print_top_topics(scores, coherence_type, coherence_measure):
    logger.info("------------------------------------------------")
    logger.info("Most coherent topics using {} {}".format(coherence_type, coherence_measure))
    for topic in sorted(scores, key=lambda name: name["scores"][coherence_type][coherence_measure], reverse=True):
        logger.info('Topic {}: coherence {}: {}'.format(topic["topic_id"],
                                                        topic["scores"][coherence_type][coherence_measure],
                                                        topic["ngrams"]))

def persist_results(c, results):
    tuples = []

    for item in results:
        doc = (int(item["n_topics"]),
               int(item["topic_id"]),
               item["ngrams"],
               item["dataset_name"],
               item["scores"]["intrinsic"]["umass"],
               item["scores"]["intrinsic"]["uci"]
               )
        tuples.append(doc)

    c.executemany(
        'INSERT INTO `topic_coherence_scores`(`n_topics`,`topic_id`,`ngrams`,`dataset_name`,`intrinsic_umass`,`intrinsic_uci`) VALUES (?,?,?,?,?,?)',
        tuples)


def main():
    dataset_name = "20newsgroups"

    intrinsic_uci = UCI(internal_index, "page", test_es_address)
    intrinsic_umass = UMass(internal_index, "page", test_es_address)

    conn = sqlite3.connect('../../data/topics.db')

    c = conn.cursor()

    logger.info("Clear data")
    c.execute('DELETE FROM `topic_coherence_scores` WHERE `dataset_name` == "' + dataset_name + '" ')
    conn.commit()

    resultset = c.execute('SELECT * FROM `topics` ORDER BY `topic_id` ASC')

    scores = []

    for row in resultset:
        topic_id = row[0]
        n_topics = row[1]
        dataset_name = row[2]
        ngrams = row[3]

        logger.info('[{}] N_Topics [{}], Topic {}: {}'.format(dataset_name, n_topics, topic_id, ngrams))

        ngrams_list = ngrams.split(" ")

        intrinsic_umass_score = intrinsic_umass.fit(ngrams_list)
        # intrinsic_uci_score = intrinsic_uci.fit(ngrams_list)
        intrinsic_uci_score = 0

        doc = {
            "n_topics": int(n_topics),
            "topic_id": int(topic_id),
            "dataset_name": dataset_name,
            "ngrams": ngrams,
            "scores": {
                "intrinsic": {
                "umass": intrinsic_umass_score,
                "uci": intrinsic_uci_score
                }
            }
        }
        scores.append(doc)

    persist_results(c, scores)

    print_scores(scores)
    print_top_topics(scores,"intrinsic","umass")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(__name__)
    logger.info('Compute topic coherence scores')

    # not used in this stub but often useful for finding various files
    # project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    # load_dotenv(find_dotenv())

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    main()

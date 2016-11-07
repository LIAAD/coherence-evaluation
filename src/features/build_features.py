from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.datasets import fetch_20newsgroups
from dotenv import find_dotenv, load_dotenv
import preprocessing
import pickle
import logging
import os

BASE_WORKDIR = "../../"

n_features = 50000


# Load the 20 newsgroups dataset and vectorize it. We use a few heuristics
# to filter out useless terms early on: the posts are stripped of headers,
# footers and quoted replies, and common English words, words occurring in
# only one document or in at least 95% of the documents are removed.
###############################################################################

# @click.command()
# @click.option('--elastic_address', default="http://localhost:9200", prompt='Inform Elastic Search Address', help='ElasticSearch address')
# @click.option('--elastic_index' default="20newsgroup",help='The person to greet.')
def main():
    logger.info("Loading 20 Newsgroups Dataset and extracting features...")
    dataset = fetch_20newsgroups(subset='all',
                                 categories=None,
                                 shuffle=False,
                                 random_state=42,
                                 remove=('headers', 'footers', 'quotes'))

    logger.info("Running data preparation process. This might take a while ...")
    corpus = [preprocessing.clean_text(x) for x in dataset.data]

    vectorizer = CountVectorizer(analyzer='word',
                                 ngram_range=(1, 1),
                                 min_df=20,
                                 stop_words='english',
                                 lowercase=True,
                                 max_df=0.90,
                                 max_features=n_features)

    matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names()

    output_matrix = open(BASE_WORKDIR + '/data/processed/20newsgroups-bag-of-words.pkl', 'wb')

    logger.info("Dumping bag-of-words to tmp file")
    # Pickle dictionary using protocol 0.
    pickle.dump(matrix, output_matrix)

    output_matrix.close()

    output_vocab = open(BASE_WORKDIR + '/data/processed/20newsgroups-vocabulary.pkl', 'wb')

    logger.info("Dumping vocabulary to tmp file")
    # Pickle dictionary.
    pickle.dump(feature_names, output_vocab)

    output_vocab.close()

    logger.info("Done!")
    logger.info("%d documents" % len(dataset.data))
    logger.info("%d categories" % len(dataset.target_names))


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(__name__)
    # logger.info('making final data set from raw data')

    # not used in this stub but often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    main()

# -*- coding: utf-8 -*-
import os
import click
import logging
from dotenv import find_dotenv, load_dotenv

from elasticsearch import Elasticsearch
from sklearn.datasets import fetch_20newsgroups


@click.command()
@click.option('--elastic_address', default="localhost:9200", prompt='Inform Elastic Search Address',
              help='ElasticSearch address')
@click.option('--elastic_index', default="20newsgroups", help='The person to greet.')
def main(elastic_address, elastic_index):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """

    es = Elasticsearch(elastic_address)

    logger.info("Loading 20 newsgroups dataset")

    dataset = fetch_20newsgroups(subset='all',
                                 shuffle=True,
                                 random_state=42,
                                 remove=('headers', 'footers', 'quotes'))

    logger.info("%d documents" % len(dataset.data))
    logger.info("%d categories" % len(dataset.target_names))

    i = 0
    for doc in dataset.data:
        try:
            logger.info("indexing document " + str(i))
            body = {'text': doc.decode('utf-8', errors='ignore')}
            es.create(index=elastic_index, doc_type='page', body=body, id=i)
        except:
            logger.warn("Document already exists in the index. Ignoring it.")

        i += 1

    logger.info(elastic_index + " index ready on elasticsearch")


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

    main()

# -*- coding: utf-8 -*-
import os
import click
import logging
from dotenv import find_dotenv, load_dotenv
import sqlite3
from sqlite3 import OperationalError

@click.command()
def main():
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger.info("Creating sqlite database")

    conn = sqlite3.connect('data/topics.db')

    c = conn.cursor()

    f = open("src/data/create_database.sql", "rw")
    statements = f.readlines()

    # Create tables
    for statement in statements:
        try:
            c.execute(statement)

        except OperationalError:
            logger.error("failed to create table")

    # Save (commit) the changes
    conn.commit()

    # Close the connection if we are done with it.
    conn.close()

    logger.info("Local database is ready ready")

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

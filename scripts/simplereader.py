#!/usr/bin/env python3

"""
Trivial API reader/writer for testing
"""


import logging
import argparse
import poefixer


DEFAULT_DSN='sqlite:///:memory:'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--debug', action='store_true', help='Debugging output')
    parser.add_argument(
        '-d', '--database-dsn', action='store',
        default=DEFAULT_DSN,
        help='Database connection string for SQLAlchemy')
    return parser.parse_args()

def pull_data(database_dsn, logger):
    """Grab data from the API and insert into the DB"""

    db = poefixer.PoeDb(db_connect=database_dsn, logger=logger)
    api = poefixer.PoeApi(logger=logger)

    db.create_database()

    while True:
        for stash in api.get_next():
            logger.debug("Inserting stash...")
            db.insert_api_stash(stash, with_items=True)
        logger.info("Stash pass complete.")
        db.session.commit()


if __name__ == '__main__':
    options = parse_args()

    logger = logging.getLogger('poefixer')
    if options.debug:
        loglevel = 'DEBUG'
    else:
        loglevel = 'INFO'
    logger.setLevel(loglevel)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    pull_data(database_dsn=options.database_dsn, logger=logger)


# vim: et:sw=4:sts=4:ai:

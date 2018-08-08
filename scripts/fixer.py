#!/usr/bin/env python3

"""
Perform analysis on the PoE pricing database for various purposes
"""


import re
import sys
import time
import logging
import argparse

import sqlalchemy

import poefixer
import poefixer.postprocess.currency as currency


DEFAULT_DSN='sqlite:///:memory:'


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-d', '--database-dsn',
        action='store', default=DEFAULT_DSN,
        help='Database connection string for SQLAlchemy')
    parser.add_argument(
        '-v', '--verbose',
        action='store_true', help='Verbose output')
    parser.add_argument(
        '--debug',
        action='store_true', help='Debugging output')
    parser.add_argument(
        'mode',
        choices=('currency',), # more to come...
        nargs=1,
        action='store', help='Mode to run in.')
    add_currency_arguments(parser)
    return parser.parse_args()

def add_currency_arguments(argsparser):
    """Add arguments relevant only to the currency processing"""

    argsparser.add_argument(
        '--start-time', action='store', type=int,
        help='The first Unix timestamp to process')
    argsparser.add_argument(
        '--continuous', action='store_true',
        help='Once processing is complete, start over')

def do_fixer(db, options, logger):
    mode = options.mode
    assert len(mode) == 1, "Only one mode allowed"
    mode = mode[0]
    if mode == 'currency':
        # Crunch and update currency values
        start_time = options.start_time
        continuous = options.continuous
        currency.CurrencyPostprocessor(
            db=db,
            start_time=start_time,
            continuous=continuous,
            logger=logger).do_currency_postprocessor()
    else:
        raise ValueError("Expected execution mode, got: " + mode)


if __name__ == '__main__':
    options = parse_args()
    echo = False

    logger = logging.getLogger('poefixer')
    if options.debug:
        loglevel = 'DEBUG'
        echo = True
    elif options.verbose:
        loglevel = 'INFO'
    else:
        loglevel = 'WARNING'
    logger.setLevel(loglevel)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.debug("Set logging level: %s" % loglevel)

    db = poefixer.PoeDb(
        db_connect=options.database_dsn, logger=logger, echo=echo)
    db.session.bind.execution_options(stream_results=True)
    do_fixer(db, options, logger)


# vim: et:sw=4:sts=4:ai:

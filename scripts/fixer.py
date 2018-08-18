#!/usr/bin/env python3

"""
Perform analysis on the PoE pricing database for various purposes
"""


import argparse
import cProfile
import logging
import pstats
import re
import sys
import time

import sqlalchemy

import poefixer
import poefixer.postprocess.currency as currency
import poefixer.extra.logger as plogger


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
        '--trace',
        action='store_true', help='Diagnostic code profiling mode')
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
    argsparser.add_argument(
        '--limit',
        action='store', type=int, help='Limit processing to this many records')

def do_fixer(db, options, logger):
    mode = options.mode
    assert len(mode) == 1, "Only one mode allowed"
    mode = mode[0]
    if mode == 'currency':
        # Crunch and update currency values
        start_time = options.start_time
        continuous = options.continuous
        limit = options.limit
        currency.CurrencyPostprocessor(
            db=db,
            start_time=start_time,
            continuous=continuous,
            limit=limit,
            logger=logger).do_currency_postprocessor()
    else:
        raise ValueError("Expected execution mode, got: " + mode)

class FixerProfiler(cProfile.Profile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enable()

    def fixer_report(self):
        self.disable()
        #buffer = io.StringIO()
        pstats.Stats(self).sort_stats('cumulative').print_stats()
        # = pstats.Stats(pr, stream=s).sort_stats(sortby)
        #ps.print_stats()
        #print(s.getvalue())



if __name__ == '__main__':
    options = parse_args()
    echo = False

    if options.debug:
        loglevel = 'DEBUG'
        echo = True
    elif options.verbose:
        loglevel = 'INFO'
    else:
        loglevel = 'WARNING'
    logger = plogger.get_poefixer_logger(loglevel)
    logger.debug("Set logging level: %s" % loglevel)

    db = poefixer.PoeDb(
        db_connect=options.database_dsn, logger=logger, echo=echo)
    db.session.bind.execution_options(stream_results=True)

    if options.trace:
        profiler = FixerProfiler()
    do_fixer(db, options, logger)
    if options.trace:
        profiler.fixer_report()


# vim: et:sw=4:sts=4:ai:

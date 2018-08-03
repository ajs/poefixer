#!/usr/bin/env python3

"""
Trivial API reader/writer for testing
"""


import argparse
import poefixer


DEFAULT_DSN='sqlite:///:memory:'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--database-dsn', action='store',
        default=DEFAULT_DSN,
        help='Database connection string for SQLAlchemy')
    return parser.parse_args()

def pull_data(database_dsn):
    db = poefixer.PoeDb(db_connect=database_dsn)
    api = poefixer.PoeApi()

    db.create_database()

    while True:
        for stash in api.get_next():
            print("Inserting stash...")
            db.insert_api_stash(stash, with_items=True)
        print("Pass complete.")
        db.session.commit()


if __name__ == '__main__':
    options = parse_args()
    pull_data(database_dsn=options.database_dsn)


# vim: et:sw=4:sts=4:ai:

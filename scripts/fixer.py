#!/usr/bin/env python3

"""
Perform analysis on the PoE pricing database for various purposes
"""


import re
import sys
import time
import logging
import argparse
import poefixer
import sqlalchemy


DEFAULT_DSN='sqlite:///:memory:'
PRICE_RE = re.compile(r'\~(price|b\/o)\s+(\S+) (\w+)')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--database-dsn', action='store',
        default=DEFAULT_DSN,
        help='Database connection string for SQLAlchemy')
    parser.add_argument(
        'mode', action='store', help='Mode to run in.')
    return parser.parse_args()

def pull_data(database_dsn):
    db = poefixer.PoeDb(db_connect=database_dsn)
    api = poefixer.PoeApi()

    db.create_database()

    while True:
        for stash in api.get_next():
            print("Inserting stash...")
            db.insert_api_stash(stash, with_items=True)
        db.session.commit()

def do_fixer(db, mode):
    if mode == 'currency':
        # Crunch and update currency values
        do_currency_fixer(db)
    else:
        raise ValueError("Expected execution mode, got: " + mode)

def parse_note(note):
    currencies = {
        "alch": "Orb of Alchemy",
        "alt": "Orb of Alteration",
        "blessed": "Blessed Orb",
        "chance": "Orb of Chance",
        "chaos": "Chaos Orb",
        "chisel": "Cartographer's Chisel",
        "chrom": "Chromatic Orb",
        "divine": "Divine Orb",
        "exa": "Exalted Orb",
        "fuse": "Orb of Fusing",
        "gcp": "Gemcutter's Prism",
        "jew": "Jeweller's Orb",
        "regal": "Regal Orb",
        "regret": "Orb of Regret",
        "scour": "Orb of Scouring",
        "vaal": "Vaal Orb"}

    if note is not None:
        match = PRICE_RE.search(note)
        if match:
            try:
                (sale_type, amt, currency) = match.groups()
                if '/' in amt:
                    num, den = amt.split('/', 1)
                    amt = float(num) / float(den)
                else:
                    amt = float(amt)
                if  currency in currencies:
                    return (amt, currencies[currency])
            except ValueError:
                # If float() fails it raises ValueError, so we just
                # TODO Need logging here, once we integrate python
                # logging handling.
                pass
    return (None, None)

def do_currency_fixer(db):
    """Process all of the currency data we've seen to date."""

    now = time.time()
    last_week = now - (7*24*60*60) # close enough, don't sweat leap time, etc
    query = db.session.query(poefixer.Item, poefixer.Stash)
    query = query.add_columns(
        poefixer.Item.typeLine, poefixer.Item.note, poefixer.Item.updated_at,
        poefixer.Stash.stash, poefixer.Item.name, poefixer.Stash.public,
        poefixer.Item.id, poefixer.Item.api_id)
    # This looks wrong, but sqlalchemy turns it into "note is not NULL"
    query = query.filter(poefixer.Stash.id == poefixer.Item.stash_id)
    query = query.filter(sqlalchemy.or_(
        sqlalchemy.and_(
            poefixer.Item.note != None,
            poefixer.Item.note != ""),
        sqlalchemy.and_(
            poefixer.Stash.stash != None,
            poefixer.Stash.stash != "")))
    query = query.filter(poefixer.Stash.public == True)
    #query = query.filter(sqlalchemy.func.json_contains_path(
    #    poefixer.Item.category, 'all', '$.currency') == 1)
    query = query.filter(poefixer.Item.updated_at >= int(last_week))

    # Stashes are named with a conventional pricing descriptor and
    # items can have a note in the same format. The price of an item
    # is the item price with the stash price as a fallback.
    prices = {}
    for row in query.all():
        is_currency = 'currency' in row.Item.category
        if is_currency:
            name = row.Item.typeLine
        else:
            name = row.Item.name + " " + row.Item.typeLine
        pricing = row.Item.note
        stash_pricing = row.Stash.stash
        stash_price, stash_currency = parse_note(stash_pricing)
        price, currency = parse_note(pricing)
        if price is None:
            # No item price, so fall back to stash
            price, currency = (stash_price, stash_currency)
        if price is None or price == 0:
            continue
        print(
            "%s %sfor sale for %s %s" % (
                name,
                ("(currency) " if is_currency else ""),
                price, currency))
        existing = db.session.query(poefixer.Sale).filter(
            poefixer.Sale.item_id == row.Item.id).one_or_none()
        if not existing:
            existing = poefixer.Sale(
                item_id=row.Item.id,
                item_api_id=row.Item.api_id,
                is_currency=is_currency,
                sale_currency=currency,
                sale_amount=price,
                sale_amount_chaos=None,
                created_at=int(time.time()),
                updated_at=int(time.time()))
        else:
            existing.sale_currency = currency
            existing.sale_amount = price
            existing.sale_amount_chaos = None
            existing.updated_at = int(time.time())
        db.session.add(existing)
    db.session.commit()

if __name__ == '__main__':
    options = parse_args()
    db = poefixer.PoeDb(db_connect=options.database_dsn)
    db.session.bind.execution_options(stream_results=True)

    logger = logging.getLogger('poefixer')
    if options.debug:
        loglevel = 'DEBUG'
    elif options.verbose:
        loglevel = 'INFO'
    else:
        loglevel = 'WARNING'
    logger.setLevel(loglevel)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.debug("Set logging level: %s" % loglevel)
    do_fixer(db, options.mode, logger)


# vim: et:sw=4:sts=4:ai:

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
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-d', '--database-dsn',
        action='store', default=DEFAULT_DSN,
        help='Database connection string for SQLAlchemy')
    parser.add_argument(
        'mode',
        choices=('currency',), # more to come...
        nargs=1,
        action='store', help='Mode to run in.')
    parser.add_argument(
        '-v', '--verbose',
        action='store_true', help='Verbose output')
    parser.add_argument(
        '--debug',
        action='store_true', help='Debugging output')
    return parser.parse_args()

def do_fixer(db, mode, logger):
    assert len(mode) == 1, "Only one mode allowed"
    mode = mode[0]
    if mode == 'currency':
        # Crunch and update currency values
        CurrencyFixer(db, logger).do_currency_fixer()
    else:
        raise ValueError("Expected execution mode, got: " + mode)

class CurrencyFixer:
    db = None
    logger = None

    def __init__(self, db, logger):
        self.db = db
        self.logger = logger

    def parse_note(self, note):
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
                except ValueError as e:
                    # If float() fails it raises ValueError
                    if 'float' in str(e):
                        self.logger.debug("Invalid price: %r" % note)
                    else:
                        raise
        return (None, None)

    def _currency_query(self, block_size, offset):
        """
        Get a query from Item (linked to Stash) that are above the
        last processed item id. Return a query that will fetch `block_size`
        rows starting at `offset`.
        """

        Item = poefixer.Item
        processed_item = self.get_last_processed_item_id()

        query = self.db.session.query(poefixer.Item, poefixer.Stash)
        query = query.add_columns(
            poefixer.Item.id,
            poefixer.Item.api_id,
            poefixer.Item.typeLine,
            poefixer.Item.note,
            poefixer.Item.updated_at,
            poefixer.Stash.stash,
            poefixer.Item.name,
            poefixer.Stash.public)
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
        #query = query.filter(poefixer.Item.updated_at >= int(last_week))
        if processed_item:
            query = query.filter(poefixer.Item.id > processed_item)
        # Tried streaming, but the result is just too large for that.
        query = query.order_by(Item.id).limit(block_size)
        if offset:
            query = query.offset(offset)

        return query

    def _process_sale(self, row):
        is_currency = 'currency' in row.Item.category
        if is_currency:
            name = row.Item.typeLine
        else:
            name = row.Item.name + " " + row.Item.typeLine
        pricing = row.Item.note
        stash_pricing = row.Stash.stash
        stash_price, stash_currency = self.parse_note(stash_pricing)
        price, currency = self.parse_note(pricing)
        if price is None:
            # No item price, so fall back to stash
            price, currency = (stash_price, stash_currency)
        if price is None or price == 0:
            self.logger.debug("No sale")
            return
        self.logger.debug(
            "%s%sfor sale for %s %s" % (
                name,
                ("(currency) " if is_currency else ""),
                price, currency))
        existing = self.db.session.query(poefixer.Sale).filter(
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

        self.db.session.add(existing)

    def get_last_processed_item_id(self):
        query = db.session.query(poefixer.Sale)
        query = query.order_by(poefixer.Sale.item_id.desc()).limit(1)
        result = query.one_or_none()
        if result:
            when = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(result.updated_at))
            self.logger.debug(
                "Last processed sale for item: %s(%s)", result.item_id, when)
            query2 = db.session.query(poefixer.Item)
            query2 = query2.order_by(poefixer.Item.id.desc()).limit(1)
            result2 = query2.one_or_none()
            when2 = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(result2.updated_at))
            self.logger.debug("Last processed item in db: %s", result2.id)
            return result.item_id
        return None


    def do_currency_fixer(self):
        """Process all of the currency data we've seen to date."""

        offset = 0
        count = 0
        todo = True
        block_size = 1000 # Number of rows per block

        while todo:
            query = self._currency_query(block_size, offset)

            # Stashes are named with a conventional pricing descriptor and
            # items can have a note in the same format. The price of an item
            # is the item price with the stash price as a fallback.
            prices = {}
            count = 0
            for row in query.all():
                max_id = row.Item.id
                count += 1
                self.logger.debug("Row in %s" % row.Item.id)
                if count % 100 == 0:
                    self.logger.info("%s rows in..." % (count + offset))
                self._process_sale(row)

            todo = count == block_size
            offset += count
            db.session.commit()

if __name__ == '__main__':
    options = parse_args()

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

    db = poefixer.PoeDb(db_connect=options.database_dsn, logger=logger)
    db.session.bind.execution_options(stream_results=True)
    do_fixer(db, options.mode, logger)


# vim: et:sw=4:sts=4:ai:

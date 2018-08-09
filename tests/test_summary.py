#!/usr/bin/env python

"""A unittest for poefixer.db"""

import logging
import unittest
import collections

import poefixer
import poefixer.extra.logger as plogger
from poefixer.extra.sample_data import sample_stash_data
from poefixer.postprocess.currency import CurrencyPostprocessor


class TestPoefixerDb(unittest.TestCase):

    DB_URI = 'sqlite:///:memory:'

    def setUp(self):
        self.logger = plogger.get_poefixer_logger('WARNING')

    def _get_default_db(self):
        db = poefixer.PoeDb(db_connect=self.DB_URI, logger=self.logger)
        db.create_database()
        return db

    def test_insert_currency(self):
        """
        Test the currency summary handling on a list of
        20 reasonable offers and one that is off by an order
        of magnitude. The processing should ignore the last one
        for summary purposes and produce a mean value that is
        in line with the majority of results.
        """

        stashes = self._sample_stashes(
            ([("Chaos Orb", "Exalted Orb", 0.01) for _ in range(20)] +
             [("Chaos Orb", "Exalted Orb", 100)]))

        db = self._get_default_db()

        for stash in stashes:
            db.insert_api_stash(stash, with_items=True)
        db.session.commit()

        cp = CurrencyPostprocessor(db, None, logger=self.logger)
        cp.do_currency_postprocessor()

        query = db.session.query(poefixer.CurrencySummary)
        self.assertEqual(query.count(), 1)
        row = query.one()
        self.assertEqual(row.from_currency, "Chaos Orb")
        self.assertEqual(row.to_currency, "Exalted Orb")
        self.assertEqual(row.count, 20) # The extreme value was discarded
        self.assertAlmostEqual(row.mean, 0.01)
        self.assertEqual(row.league, 'Standard')

    def test_currency_abbreviations(self):
        """Make sure that abbreviated sale notes work"""

        # A sample of names to start
        currency_abbrevs = (
            # Official names
            "alt", "blessed", "chance", "chisel", "chrom", "divine",
            "jew", "regal", "regret", "scour", "vaal",
            # Names we saw in the data and adopted
            "c", "p", "mirror", "eshs-breachstone", "minotaur",
            "wisdom",
            # Names we got from poe.trade
            "fus", "alchemy", "gemc", "ex")

        db = self._get_default_db()
        cp = CurrencyPostprocessor(db, None, logger=self.logger)

        for currency in currency_abbrevs:
            (amt, cur) = cp.parse_note("~price 1 " + currency)
            self.assertEqual(amt, 1)
            self.assertNotEqual(cur, currency)

        # Now bulk-test all presets
        from poefixer.postprocess.currency_names import \
            OFFICIAL_CURRENCIES, UNOFFICIAL_CURRENCIES

        currencies = {}
        currencies.update(OFFICIAL_CURRENCIES)
        currencies.update(UNOFFICIAL_CURRENCIES)

        for abbrev, full in currencies.items():
            price_note = "~b/o 1/2 " + abbrev
            (amt, cur) = cp.parse_note(price_note)
            self.assertEqual(
                cur, full,
                "Parse %s failed: %r != %r" % (price_note, cur, full))
            self.assertEqual(amt, 1.0/2)

    def _sample_stashes(self, descriptors):

        stash = {
            'id': '%064x' % 123456,
            'accountName': 'JoeTest',
            'stash': 'Goodies',
            'stashType': 'X',
            'public': True,
            'league': 'Standard',
            'items': []}

        offset = 0
        for desc in descriptors:
            (from_c, to_c, price) = desc
            stash['items'].append(currency_item(from_c, offset, to_c, price))
            offset += 1

        return [poefixer.ApiStash(stash)]

def currency_item(currency, offset, ask_currency, ask_value):
    """
    Return a datastructure as if from the API for the given currency.

    Parameters:

    * `currency` - The name of the currency (e.g. "Chaos Orb")
    * `offset` - The id offset for this item.
    * `ask_currency` - The abbreviated currency in the price (e.g. "exa")
    * `ask_price` - The numeric quantity in the asking price (e.g. 1)
    """

    return {
        # Boilerplate fields:
        'w': 2, 'h': 1, 'x': 1, 'y': 1, 'ilvl': 1, 'league': 'Standard',
        'frameType': 'X', 'icon': 'X', 'identified': True, 'verified': True,
        # Currency-specific info:
        'id': '%064x' % offset, 'name': '', 'typeLine': currency,
        'note': '~price %s %s' % (ask_value, ask_currency),
        'category': {'currency': []}}


if __name__ == '__main__':
    unittest.main()

# vim: et:sts=4:sw=4:ai:

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
        db = self._get_default_db()
        stashes = self._sample_stashes()
        for stash in stashes:
            db.insert_api_stash(stash, with_items=True)

        db.session.commit()

        cp = CurrencyPostprocessor(db, None, logger=self.logger)
        cp.do_currency_postprocessor()

        query = db.session.query(poefixer.CurrencySummary)
        self.assertEqual(query.count(), 1)
        for row in query.all():
            self.assertEqual(row.from_currency, "Chaos Orb")
            self.assertEqual(row.to_currency, "Exalted Orb")
            self.assertEqual(row.count, 20)
            self.assertAlmostEqual(row.mean, 0.01)
            self.assertEqual(row.league, 'Standard')

    def _sample_stashes(self):
        stash = {
            'id': '%064x' % 123456,
            'accountName': 'JoeTest',
            'stash': 'Goodies',
            'stashType': 'X',
            'public': True,
            'league': 'Standard',
            'items': ([
                currency_item('Chaos Orb', n, "Exalted Orb", 0.01)
                    for n in range(20)] + [
                currency_item('Chaos Orb', 20, "Exalted Orb", 100)])}
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

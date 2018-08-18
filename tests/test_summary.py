#!/usr/bin/env python

"""A unittest for poefixer.db"""

import logging
import unittest
import collections

import poefixer
import poefixer.extra.logger as plogger
from poefixer.extra.sample_data import sample_stash_data
from poefixer.postprocess.currency import CurrencyPostprocessor


class CurrencyStep:
    """A linked list of currency conversion steps with prices"""

    currency = None
    price = None
    _price_float = None
    next_step = None

    def __init__(self, currency, price=None, next_step=None):
        self.currency = currency
        self.price = price
        self.next_step = next_step

        if price:
            if isinstance(price, str):
                if '/' in price:
                    num, den = price.split('/')
                    self._price_float = float(num)/float(den)
                    return
            self._price_float = float(price)

    def _get_conversion_steps(self):
        if self.price:
            assert self.next_step, "If a price is set, must have next_step"
            yield (self.currency, self.next_step.currency, self.price)
            for sample in self.next_step._get_conversion_steps():
                yield sample

    def get_sample_stashes(self):
        return sample_stashes(list(self._get_conversion_steps()))

    def conversion_price(self):
        price = self._price_float
        if self.next_step and self.next_step.price:
            price *= self.next_step.conversion_price()
        return price

    def conversion_goal(self):
        if self.next_step:
            return self.next_step.conversion_goal()
        return self.currency


class TestPoefixerDb(unittest.TestCase):

    DB_URI = 'sqlite:///:memory:'

    def setUp(self):
        self.logger = plogger.get_poefixer_logger('WARNING')

    def _get_default_db(self):
        db = poefixer.PoeDb(db_connect=self.DB_URI, logger=self.logger)
        db.create_database()
        return db

    def _currency_postprocessor(self, db, recent=None):
        return CurrencyPostprocessor(
            db, start_time=None, recent=recent, logger=self.logger)

    def test_insert_currency(self):
        """
        Test the currency summary handling on a list of
        20 reasonable offers and one that is off by an order
        of magnitude. The processing should ignore the last one
        for summary purposes and produce a mean value that is
        in line with the majority of results.
        """

        stashes = sample_stashes(
            [("Chaos Orb", "Exalted Orb", 0.01) for _ in range(20)] +
            [("Chaos Orb", "Exalted Orb", 100)])

        db = self._get_default_db()

        for stash in stashes:
            db.insert_api_stash(stash, with_items=True)
        db.session.commit()

        cp = self._currency_postprocessor(db)
        cp.do_currency_postprocessor()

        query = db.session.query(poefixer.CurrencySummary)
        self.assertEqual(query.count(), 1)
        row = query.one_or_none()
        self.assertIsNotNone(row)
        self.assertEqual(row.from_currency, "Chaos Orb")
        self.assertEqual(row.to_currency, "Exalted Orb")
        self.assertEqual(row.count, 20) # The extreme value was discarded
        self.assertAlmostEqual(row.mean, 0.01)
        self.assertEqual(row.league, 'Standard')

    def test_actual_currency_name(self):
        """
        Test the dynamic currency name handling based on data
        we have seen.
        """

        from_c = "My Precious"
        stashes = sample_stashes([(from_c, "Exalted Orb", 0.01)])

        db = self._get_default_db()

        cp = self._currency_processor_harness(db, stashes)

        # Now see if we'll use those new names
        (amt, cur) = cp.parse_note("~price 1 " + from_c)
        self.assertEqual(amt, 1)
        self.assertEqual(cur, from_c)
        # Try dashed version
        dashed_c = from_c.lower().replace(' ', '-')
        (amt, cur) = cp.parse_note("~price 1 " + dashed_c)
        self.assertEqual(amt, 1)
        # Make sure it goes back to the original
        self.assertEqual(cur, from_c)

    def _currency_processor_harness(self, db, stashes):
        for stash in stashes:
            db.insert_api_stash(stash, with_items=True)
        db.session.commit()

        cp = self._currency_postprocessor(db)
        cp.do_currency_postprocessor()
        # Second time picks up the new names we've seen
        cp.do_currency_postprocessor()

        return cp

    def _currency_valuation_check(self, conversion, alt_conversions=None):
        """Test a conversion price (conversion is a CurrencyStep list)"""

        stashes = conversion.get_sample_stashes()
        if alt_conversions:
            for alt_conv in alt_conversions:
                stashes += alt_conv.get_sample_stashes()

        db = self._get_default_db()
        cp = self._currency_processor_harness(db, stashes)
        # Repeat in order to re-add each currency, forcing
        # connections to be made.
        cp = self._currency_processor_harness(db, stashes)

        from_currency = conversion.currency
        to_currency = conversion.conversion_goal()
        self.assertEqual(
            to_currency, "Chaos Orb",
            "valuation test requires Chaos Orb target")
        price = conversion.conversion_price()

        self.assertIsNotNone(price)

        cp_price = cp.find_value_of(from_currency, "Standard", 1)

        self.assertIsNotNone(
            cp_price,
            "Conversion from %s->chaos" % from_currency)
        self.assertAlmostEqual(price, cp_price)

    def test_exalt_for_chaos(self):
        """Test pricing of ex -> chaos"""

        self._currency_valuation_check(
            CurrencyStep("Exalted Orb", 100, CurrencyStep("Chaos Orb")))

    def text_exalt_for_chrom_for_chaos(self):
        """Test price of ex -> chrom -> chaos"""

        self._currency_valuation_check(
            CurrencyStep(
                "Exalted Orb", 500, CurrencyStep(
                    "Chromatic Orb", "1/5", CurrencyStep("Chaos Orb"))))

    def test_currency_abbreviations(self, single=None, should_be=None):
        """
        Make sure that abbreviated sale notes work

        If passed `single`, it is used as the one currency
        abbreviation to test. This is for regressions.

        If `single` is provided, then `should_be` can be set
        to the expected expansion.
        """

        if single:
            currency_abbrevs = (single,)
        else:
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
        cp = self._currency_postprocessor(db)

        for currency in currency_abbrevs:
            (amt, cur) = cp.parse_note("~price 1 " + currency)
            self.assertEqual(amt, 1)
            self.assertNotEqual(cur, currency)
            if should_be:
                self.assertEqual(cur, should_be)

        if single:
            return

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

    def test_exalt_regression(self):
        self.test_currency_abbreviations(
            single='exalt', should_be='Exalted Orb')

    def test_trans_regression(self):
        self.test_currency_abbreviations(
            single='trans', should_be='Orb of Transmutation')

    def test_anull_regression(self):
        """Common spelling error"""

        self.test_currency_abbreviations(
            single='orb-of-anullment', should_be='Orb of Annulment')


def sample_stashes(descriptors):

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

#!/usr/bin/env python

"""A unittest for poefixer.db"""

import logging
import unittest
import collections

import poefixer
from poefixer.extra.sample_data import sample_stash_data


class TestPoefixerDb(unittest.TestCase):

    def _get_default_db(self):
        db = poefixer.PoeDb(db_connect='sqlite:///:memory:')
        db.create_database()
        return db

    def test_initial_setup(self):
        db = self._get_default_db()

    def test_insert_no_items(self):
        db = self._get_default_db()
        stashes = self._sample_stashes()
        for stash in stashes:
            db.insert_api_stash(stash, with_items=False)

    def test_insert_with_items(self):
        db = self._get_default_db()
        stashes = self._sample_stashes()
        for stash in stashes:
            db.insert_api_stash(stash, with_items=True)

    def _sample_stashes(self):
        return [poefixer.ApiStash(s) for s in sample_stash_data()]


if __name__ == '__main__':
    unittest.main()

# vim: et:sts=4:sw=4:ai:

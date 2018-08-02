#!/usr/bin/env python3

"""
The core classes used by the PoE API python interface. To jump right in, see
the `PoeApi` class.
"""


import re
import sys
import time
import requests
import datetime
import collections
import rapidjson as json


__author__ = "Aaron Sherman <ajs@ajs.com>"
__copyright__ = "Copyright 2018, Aaron Sherman"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Aaron Sherman"
__email__ = "ajs@ajs.com"


POE_STASH_API_ENDPOINT = 'http://www.pathofexile.com/api/public-stash-tabs'


class PoeApiData:
    """
    A base class for data that is similar to a namedtuple, but for which
    individual property behaviors can be overwritten

    To use, simply subclass and set the "fields" attribute to the list of
    fields in the data structure. If you write your own property, simply
    access the underlying datastructure via `self._data` which, at the
    top-level is a dict of field names and values.

    Example:

    class Thing(PoeApiData):
        fields = ['field1', 'field2']

        @property
        def field3(self):
            return self.field1 + self.field2

    """

    fields = None

    def __init_subclass__(cls):
        def data_getter(name):
            """Because python doesn't have real closures"""
            return property(lambda  self: self._data.get(name, None))

        super().__init_subclass__()
        assert cls.fields, "Incorrectly initialized PoeApiData class"
        added = []
        for field in cls.fields:
            if not hasattr(cls, field):
                added += [field]
                setattr(cls, field, data_getter(field))

    def __init__(self, data):
        self._data = data


class Item(PoeApiData):
    name_cleaner_re = re.compile(r'^\<\<.*\>\>')
    fields = [
        "abyssJewel", "additionalProperties", "artFilename",
        "category", "corrupted", "cosmeticMods", "craftedMods",
        "descrText", "duplicated", "elder", "enchantMods",
        "explicitMods", "flavourText", "frameType", "h", "icon",
        "id", "identified", "ilvl", "implicitMods", "inventoryId",
        "isRelic", "league", "lockedToCharacter", "maxStackSize", "name",
        "nextLevelRequirements", "note", "properties", "prophecyDiffText",
        "prophecyText", "requirements", "secDescrText", "shaper",
        "socketedItems", "sockets", "stackSize", "support",
        "talismanTier", "typeLine", "utilityMods", "verified", "w", "x",
        "y" ]

    def _clean_markup(self, value):
        return re.sub(self.name_cleaner_re, '', value)

    @property
    def typeLine(self):
        return self._clean_markup(self._data['typeLine'])

    @property
    def name(self):
        return self._clean_markup(self._data['name'])


class Stash(PoeApiData):
    fields = [
        'accountName', 'lastCharacterName', 'id', 'stash', 'stashType',
        'items', 'public' ]

    @property
    def items(self):
        for item in self._data['items']:
            yield Item(item)


class PoeApi:
    """
    This is the core API class. To access the PoE API, simply instantiate
    this class and call its "get_next" method as many times as you want to
    get a generator of stashes.

    Example:

    api = PoeApi()
    while True:
        for stash in api.get_next():
            # do something with stash such as:
            for item in stash.items:
                # do something with the item such as:
                print(stash.name, ", ", stash.typeLine)

    Optional instantiation parameters:

    * `next_id` - The id of the first result to be fetched (internal to
                  the HTTP API.
    * `rate` - The number of seconds (float) to wait between requests.
               Defaults to 1.1. Changing this can result in server-side rate-
               limiting.
    * `api_root` - The PoE stash API root. Generally don't change this unless
                   you have a mock server you use for testing.
    """

    api_root = POE_STASH_API_ENDPOINT
    next_id = None
    rate = 1.1

    def __init__(self, next_id=None, rate=None, api_root=None):
        self.next_id = next_id
        if rate is not None:
            self.rate = datetime.timedelta(seconds=rate)
        if api_root is not None:
            self.api_root = api_root
        self.last_time = None

    def rate_wait(self):
        if self.last_time:
            now = datetime.datetime.now()
            delta = now - self.last_time
            if delta.total_seconds() < self.rate:
                remaining = self.rate - delta.total_seconds()
                time.sleep(remaining)
        self.set_last_time()

    def set_last_time(self):
        self.last_time = datetime.datetime.now()

    def get_next(self):
        self.rate_wait()
        data, self.next_id = self._get_data(next_id=self.next_id)
        return self.stash_generator(data)

    def stash_generator(self, data):
        for stash in data:
            yield Stash(stash)

    def _get_data(self, next_id=None):
        url = self.api_root
        if next_id:
            url += '?id=' + next_id
        req = requests.get(url)
        self.set_last_time()
        req.raise_for_status()
        data = json.loads(req.text)
        if 'next_change_id' not in data:
            raise KeyError('next_change_id required field not present in response')
        return (data['stashes'], data['next_change_id'])

if __name__ == '__main__':
    # For testing only...
    api = PoeApi()
    stashes = api.get_next()
    print("got first set of stashes")
    stashes = api.get_next()
    print("Next_id is %s" % api.next_id)
    done = False
    for stash in stashes:
        for item in stash.items:
            print("stash contains item: %s %s" % (item.name, item.typeLine))
            done = True
            break
        if done:
            break


# vim: sw=4 sts=4 et ai:

#!/usr/bin/env python3

"""
The core classes used by the PoE API python interface. To jump right in, see
the `PoeApi` class.
"""


import re
import time
import datetime
import requests
import rapidjson as json


__author__ = "Aaron Sherman <ajs@ajs.com>"
__copyright__ = "Copyright 2018, Aaron Sherman"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Aaron Sherman"
__email__ = "ajs@ajs.com"


POE_STASH_API_ENDPOINT = 'http://www.pathofexile.com/api/public-stash-tabs'


# Our abstract base creates its public methods dynamically
# pylint: disable=too-few-public-methods
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
            # Because we don't want to conflict with auto-generate names:
            # pylint: disable=protected-access
            return property(lambda  self: self._data.get(name, None))

        super().__init_subclass__()
        assert cls.fields, "Incorrectly initialized PoeApiData class"
        added = []
        # pylint doesn't know that we just validated that fields
        # has been overridden.
        # pylint: disable=not-an-iterable
        for field in cls.fields:
            if not hasattr(cls, field):
                added += [field]
                setattr(cls, field, data_getter(field))

    def __init__(self, data):
        self._data = data


class ApiItem(PoeApiData):
    """This is the core PoE item structure"""

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
        "y"]

    def _clean_markup(self, value):
        return re.sub(self.name_cleaner_re, '', value)

    # These names are given to us by the API, and are not python-aware.
    # pylint: disable=invalid-name
    @property
    def typeLine(self):
        """The type of the item. Markup is stripped."""

        return self._clean_markup(self._data['typeLine'])

    @property
    def name(self):
        """The basic name of the item. Markup is stripped."""

        return self._clean_markup(self._data['name'])



class ApiStash(PoeApiData):
    """A stash aka "stash tab" is a collection of items in an x/y grid"""

    fields = [
        'accountName', 'lastCharacterName', 'id', 'stash', 'stashType',
        'items', 'public']

    @property
    def items(self):
        """The array of items (as a generator of ApiItem objects)"""

        for item in self._data['items']:
            yield ApiItem(item, self)


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
        """Pause for the rest of the time left in our rate limiting parameter"""

        if self.last_time:
            now = datetime.datetime.now()
            delta = now - self.last_time
            if delta.total_seconds() < self.rate:
                remaining = self.rate - delta.total_seconds()
                time.sleep(remaining)
        self.set_last_time()

    def set_last_time(self):
        """Set the time of the last request for rate limiting"""

        self.last_time = datetime.datetime.now()

    def get_next(self):
        """Return the next stash generator"""

        self.rate_wait()
        data, self.next_id = self._get_data(next_id=self.next_id)
        return self.stash_generator(data)

    @staticmethod
    def stash_generator(data):
        """Turn a data blob from the API into a generator of ApiStash objects"""

        for stash in data:
            yield ApiStash(stash)

    def _get_data(self, next_id=None):
        """Actually read from the API via requests library"""

        url = self.api_root
        if next_id:
            url += '?id=' + next_id
        req = requests.get(url)
        self.set_last_time()
        req.raise_for_status()
        # rapidjson doesn't tell python what its methods are...
        # pylint: disable=c-extension-no-member
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
    for input_stash in stashes:
        for stashitem in input_stash.items:
            print(
                "stash contains item: %s %s" % (stashitem.name, stashitem.typeLine))
            done = True
            break
        if done:
            break


# vim: sw=4 sts=4 et ai:

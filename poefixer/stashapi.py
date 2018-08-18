#!/usr/bin/env python3

"""
The core classes used by the PoE API python interface. To jump right in, see
the `PoeApi` class.
"""


import re
import time
import logging
import datetime
import requests
import requests.packages.urllib3.util.retry as urllib_retry
import requests.adapters as requests_adapters
import rapidjson as json


__author__ = "Aaron Sherman <ajs@ajs.com>"
__copyright__ = "Copyright 2018, Aaron Sherman"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Aaron Sherman"
__email__ = "ajs@ajs.com"


POE_STASH_API_ENDPOINT = 'http://www.pathofexile.com/api/public-stash-tabs'


# TODO: Move this out into something more central
def requests_context():
    session = requests.Session()
    retry = urllib_retry.Retry(
        total=10,
        backoff_factor=1,
        status_forcelist=(500, 502, 503, 504))
    adapter = requests_adapters.HTTPAdapter(max_retries=retry)

    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session

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
    required_fields = None

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
            if field.startswith('_'):
                raise KeyError("Invalid field name: %s" % field)
            if not hasattr(cls, field):
                added += [field]
                setattr(cls, field, data_getter(field))

    def __init__(self, data, logger=logging):
        self._data = data
        self._logger = logger

    def _repr_fields(self):
        def format_fields():
            for field in sorted(self.fields):
                value = getattr(self, field)
                if value is None:
                    # Skip empty values for summary
                    continue
                elif isinstance(value, str) and value.startswith('http'):
                    if len(value) > 10:
                        value = value[0:7] + '...'
                yield "%s=%r" % (field, value)
        return ", ".join(format_fields())

    def __repr__(self):
        if self.fields:
            return "<%s(%s)>" % (self.__class__.__name__, self._repr_fields())
        else:
            return "<%s()>" % self.__class__.__name__

    def validate(self):
        """
        Basic validation based on self.required_fields if present.

        Subclasses should implement their own validate as apporopriate
        and call `super().validate()`
        """

        if self.required_fields:
            for field in self.required_fields:
                value = self._data.get(field, None)
                if value is None:
                    raise ValueError(
                        "%s: %s is a required field" % (
                            self.__class__.__name__, field))


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

    required_fields = [
        "category", "id", "h", "w", "x", "y", "frameType", "icon",
        "identified", "ilvl", "league", "name", "typeLine", "verified"]

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

    required_fields = ['id', 'stashType', 'public']

    @property
    def items(self):
        """The array of items (as a generator of ApiItem objects)"""

        for item in self._data['items']:
            api_item = ApiItem(item)
            try:
                api_item.validate()
            except ValueError as e:
                self._logger.warning("Invalid item: %s", str(e))
                continue
            yield api_item

    @property
    def api_item_count(self):
        return len(self._data['items'])


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
    * `slow` - Be extra careful about issuing requests too fast by updating the
               last request counter AFTER a request completes. Otherwise, the
               counter is only updated BEFORE each request.
    * `api_root` - The PoE stash API root. Generally don't change this unless
                   you have a mock server you use for testing.
    """

    api_root = POE_STASH_API_ENDPOINT
    next_id = None
    rate = 1.1
    slow = False

    def __init__(
            self,
            next_id=None, rate=None, slow=None, api_root=None, logger=logging):
        self.logger = logger
        self.next_id = next_id
        if rate is not None:
            self.rate = datetime.timedelta(seconds=rate)
        if slow is not None:
            self.slow = slow
        if api_root is not None:
            self.api_root = api_root
        self.last_time = None
        self.rq_context = requests_context()

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
        data, self.next_id = self._get_data(next_id=self.next_id, slow=self.slow)
        return self.stash_generator(data)

    @staticmethod
    def stash_generator(data):
        """Turn a data blob from the API into a generator of ApiStash objects"""

        for stash in data:
            api_stash = ApiStash(stash)
            try:
                api_stash.validate()
            except ValueError as e:
                self.logger.warning("Invalid stash: %s", str(e))
                continue
            yield api_stash

    def _get_data(self, next_id=None, slow=False):
        """Actually read from the API via requests library"""

        url = self.api_root
        if next_id:
            self.logger.info("Requesting next stash set: %s" % next_id)
            url += '?id=' + next_id
        else:
            self.logger.info("Requesting first stash set")
        req = self.rq_context.get(url)
        if slow:
            self.set_last_time()
        req.raise_for_status()
        self.logger.debug("Acquired stash data")
        # rapidjson doesn't tell python what its methods are...
        # pylint: disable=c-extension-no-member
        data = json.loads(req.text)
        self.logger.debug("Loaded stash data from JSON")
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

"""
A database module for Python PoE API data.

Where possible the names of the fields in the API are preserved. However,
one major exception is in the "id" field, which is renamed to "api_id"
and a new, auto-incrementing primary key is labeled "id".
"""


import time
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import rapidjson as json

Base = declarative_base()

# We're not doing a full implementation, here...
# pylint: disable=abstract-method
class SemiJSON(sqlalchemy.types.TypeDecorator):
    """A stopgap for using SQLite implementations that do not support JSON"""

    impl = sqlalchemy.UnicodeText

    def load_dialect_impl(self, dialect):
        if dialect.name == 'sqlite':
            return dialect.type_descriptor(self.impl)
        return dialect.type_descriptor(sqlalchemy.JSON())

    # rapidjson doesn't appear to let python know that it has a dumps
    # function, so we have to give pylint a heads-up
    # pylint: disable=c-extension-no-member
    def process_bind_param(self, value, dialect):
        if dialect.name == 'sqlite' and value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if dialect.name == 'sqlite' and value is not None:
            value = json.loads(value)
        return value

# SQLAlchemy table definitions do not need methods.
#
# pylint: disable=too-few-public-methods
class Stash(Base):
    """
    The db-table for API stash data
    """

    __tablename__ = 'stash'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    accountName = sqlalchemy.Column(sqlalchemy.Unicode(255))
    lastCharacterName = sqlalchemy.Column(sqlalchemy.Unicode(255))
    stash = sqlalchemy.Column(sqlalchemy.Unicode(255))
    stashType = sqlalchemy.Column(sqlalchemy.Unicode(32), nullable=False)
    public = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    updated_at = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)


class Item(Base):
    """
    The db-table for API item data
    """

    __tablename__ = 'item'


    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    h = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    w = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    x = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    y = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    abyssJewel = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    artFilename = sqlalchemy.Column(sqlalchemy.String(255))
    # Note: API docs say this cannot be null, but we get null values
    category = sqlalchemy.Column(SemiJSON)
    corrupted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    cosmeticMods = sqlalchemy.Column(SemiJSON)
    craftedMods = sqlalchemy.Column(SemiJSON)
    descrText = sqlalchemy.Column(sqlalchemy.Unicode(255))
    duplicated = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    elder = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    enchantMods = sqlalchemy.Column(SemiJSON)
    explicitMods = sqlalchemy.Column(SemiJSON)
    flavourText = sqlalchemy.Column(SemiJSON)
    frameType = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    icon = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    identified = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    ilvl = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    implicitMods = sqlalchemy.Column(SemiJSON)
    inventoryId = sqlalchemy.Column(sqlalchemy.String(255))
    isRelic = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    league = sqlalchemy.Column(sqlalchemy.Unicode(64), nullable=False)
    lockedToCharacter = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    maxStackSize = sqlalchemy.Column(sqlalchemy.Integer)
    name = sqlalchemy.Column(sqlalchemy.Unicode(255), nullable=False)
    nextLevelRequirements = sqlalchemy.Column(SemiJSON)
    note = sqlalchemy.Column(sqlalchemy.Unicode(255))
    properties = sqlalchemy.Column(SemiJSON)
    prophecyDiffText = sqlalchemy.Column(sqlalchemy.Unicode(255))
    prophecyText = sqlalchemy.Column(sqlalchemy.Unicode(255))
    requirements = sqlalchemy.Column(SemiJSON)
    secDescrText = sqlalchemy.Column(sqlalchemy.Text)
    shaper = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    sockets = sqlalchemy.Column(SemiJSON)
    stackSize = sqlalchemy.Column(sqlalchemy.Integer)
    support = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    talismanTier = sqlalchemy.Column(sqlalchemy.Integer)
    typeLine = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    utilityMods = sqlalchemy.Column(SemiJSON)
    verified = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    updated_at = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)


    def __repr__(self):
        return "<Item(name=%r, id=%s, api_id=%s, typeLine=%r" % (
            self.name, self.id, self.api_id, self.typeLine)


class PoeDb:
    """
    This is the wrapper for the item/stash database. All you need to
    do is instantiate it with an appropriate SQLAlchemy connection
    URI as the `db_connect` parameter (or default it to a sqlite db
    in "poetest.db") and send it stashes you get from the api like so:

        db = PoeDb()
        api = PoeApi()

        while True:
            for stash in api.get_next():
                db.insert_api_stash(stash, with_items=True)

    """

    db_connect = 'sqlite:///poetest.db'
    _session = None
    _engine = None
    _session_maker = None

    def insert_api_stash(self, stash, with_items=False):
        """
        Given a PoeApi.Stash, insert its data into the Item table

        An optional `with_items` boolean may be set to true in order
        to recurse into the items in the given stash and insert/update
        them as well.
        """

        # I really dislike mashing my close-brackets up against my data
        # pylint: disable=bad-whitespace
        simple_fields = [
            "accountName", "lastCharacterName", "stash", "stashType",
            "public" ]

        self._insert_or_update_row(Stash, stash, simple_fields)

        if with_items:
            for item in stash.items:
                self.insert_api_item(item)

    def insert_api_item(self, item):
        """Given a PoeApi.Item, insert its data into the Item table"""

        # pylint: disable=bad-whitespace
        simple_fields = [
            "h", "w", "x", "y", "abyssJewel", "artFilename",
            "category", "corrupted", "cosmeticMods", "craftedMods",
            "descrText", "duplicated", "elder", "enchantMods",
            "explicitMods", "flavourText", "frameType", "icon",
            "identified", "ilvl", "implicitMods", "inventoryId",
            "isRelic", "league", "lockedToCharacter", "maxStackSize",
            "name", "nextLevelRequirements", "note", "properties",
            "prophecyDiffText", "prophecyText", "requirements",
            "secDescrText", "shaper", "sockets",
            "stackSize", "support", "talismanTier", "typeLine",
            "utilityMods", "verified" ]

        # pylint: disable=fixme
        #TODO socketed items...

        self._insert_or_update_row(Item, item, simple_fields)

    def _insert_or_update_row(self, table, thing, simple_fields):
        now = int(time.time())
        query = self.session.query(table)
        existing = query.filter(table.api_id == thing.id).first()
        if existing:
            row = existing
        else:
            row = table()
            row.created_at = now

        row.api_id = thing.id
        row.updated_at = now

        for field in simple_fields:
            setattr(row, field, getattr(thing, field, None))

        self.session.add(row)

    @property
    def session(self):
        """The current database context object"""

        if not self._session:
            self._session = self._session_maker()
        return self._session

    def create_database(self):
        """Write a new database from our schema"""

        Base.metadata.create_all(self._engine)

    def __init__(self, db_connect=None, echo=False):
        if db_connect is not None:
            self.db_connect = db_connect

        self._engine = sqlalchemy.create_engine(self.db_connect, echo=echo)
        self._session_maker = sqlalchemy.orm.sessionmaker(bind=self._engine)


# vim: sw=4 sts=4 et ai:

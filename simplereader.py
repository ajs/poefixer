"""
Trivial API reader/writer for testing
"""


import poefixer


db = poefixer.PoeDb(db_connect='sqlite:///:memory:')
api = poefixer.PoeApi()

db.create_database()

while True:
    for stash in api.get_next():
        print("Inserting stash...")
        db.insert_api_stash(stash, with_items=True)

#vim: et sw=4 sts=4 ai:

# poefixer
A Path of Exile Stash API reader and database manager

This module consits of two major modules:

* `stashapi`
* `db`

The stashapi is the HTTP interface to stash updates published
by GGG.

The db module is what takes the objects created by stashapi and writes them
to your database.

This isn't (yet) a full-featured end-user tool. It's really aimed at
Python developers who wish to begin working with the Path of Exile API,
and don't want to write the API and DB code themselves (I know I didn't!)

-A

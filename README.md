# poefixer
A Path of Exile Stash API reader and database manager

This module consits of two major components, both of which are
accessible from the top-level namespace or can be imported individually:

* `stashapi`
* `db`

The stashapi is the HTTP interface to public stash tab updates published
by GGG. This is how Path of Exile trading sites get their data, though
if you're not whitelisted, you will be rate restricted by defualt.

The db module is what takes the objects created by stashapi and writes them
to your database. This creates a _current_ (not time series) database of all
stashes and items.

This isn't (yet) a full-featured end-user tool. It's really aimed at
Python developers who wish to begin working with the Path of Exile API,
and don't want to write the API and DB code themselves (I know I didn't!)

-A

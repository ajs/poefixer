# poefixer
A Path of Exile Stash API reader and database manager

This module consits of two major components, both of which are
accessible from the top-level namespace or can be imported individually:

* `stashapi`
* `db`

The *stashapi module* is the HTTP interface to public stash tab updates
published by GGG. This is how Path of Exile trading sites get their data,
though if you're not whitelisted, you will be rate restricted by defualt.

The *db module* is what takes the objects created by stashapi and writes them
to your database. This creates a _current_ (not time series) database of all
stashes and items.

To load data:

* Begin by creating a database somewhere. MySQL is the most
  heavily tested by the author, but you can try something else
  if you want. Most of the code relies on sqlachemy, so it should
  generally just work...
* Install the module. If you are running from source code, you
  can `pip install -e .` or you can just set the environment variable
  `PYTHONPATH=.` once or before each command.
* Turn your database credentials into a URL of the form:
  `<db-type>://<user>:<password>@<host>/<db>`
* For MySQL, you will also want to include `?charset=utf8mb4` at
  the end of the URL. Also, mysql has many interface libraries, so
  you need to specify which to use. I recommend `mysql+pymysql` as
  the `db-type` at the front of the URL.
* Run the data loader as a trial run: `scripts/simplereader.py -d <db-url>`
* If that works, kill it and start it up again from the most recent ID.
  You can find that ID at: https://poe.ninja/stats
* Once that is running and pulling down data into your database, you will
  also need a currency processor running. This takes the raw data and
  creates the currency summary and sales tables. Run it like so:
  `scripts/fixer.py -d <db-url> currency --verbose`
* The currency script will exit when it's up-to-date, so you want to
  re-run it either on a schedule or just every time it exits cleanly.

These programs provide a basic database structure and will auto-instantiate
tables that they need. However, they are also too slow to keep up with the
entire output of the community! You would have to create a parallelized
version of the `simplereader.py` script and the currency processor for
that, and that's beyond the scope of this project, mostly because doing
so without being whielisted by GGG would hit their auto-rate-limiting
thresholds, and I'm not yet a big enough fish to get on that list.

That being said, you can accomplish quite a bit, just by regularly updating
your pull to the most recent `next_id` and re-running. If you just wish
to analyze the market, this is more than sufficient, and will quickly give
you gigabytes of market data!

This isn't (yet) a full-featured end-user tool. It's really aimed at
Python developers who wish to begin working with the Path of Exile API,
and don't want to write the API and DB code themselves (I know I didn't!)

-A

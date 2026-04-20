## Performance with a large database

We'll examine how the web app functions with a large amount of testing/dummy data. Ensure the database has been initialized, and run

```$ python seed.py```

Reserve approximately 30 seconds for creating the testing data with the following parameters:

```
USER_COUNT = 10_000
POST_COUNT = 1_000_000
COMMENT_COUNT = 3_000_000
LIKE_COUNT = 50_000_000
TAG_COUNT = 600_000
FRIEND_COUNT = 70_000
```

### Measurements

We'll begin by adding measurement logic to `app.py`:

```
from flask import g
from time import time

@app.before_request
def before_request():
    g.start_time = time()

@app.after_request
def after_request(response):
    t = round(time() - g.start_time, 2)
    print(f">> Request time: {t} seconds")
    return response
```

Every time a user makes an HTML request, the app prints a time measurement to the console.

### Results

Each result is the average value of three (3) measurements, rounded to two decimal places. Each time, the page was loaded with a cache bypass (`CTRL+F5`).

#### No dummy data

We'll begin by creating only one user and post.

| Page | Time |
| -----| --- |
| index page | 0.05 s |
| post | 0.03 s |
| user page | 0.04 s |
| other | 0.02 s |

#### Testing data

With testing data created using `seed.py`, but without pagination or indexing

| Page | Time |
| -----| --- |
| index page | 10.34 s |
| post | 0.07 s |
| user page | 0.23 s |
| other | 0.03 s |

The application is unusably sluggish.

#### With pagination

With test data, no indexing but pagination

| Page | Time |
| -----| --- |
| index page | 0.74 s |
| post | 0.04 s |
| user page | 0.05 s |
| other | 0.03 s |

#### Final optimizations

The same testing data, with both indexing and pagination

| Page | Time |
| -----| --- |
| index page | 0.32 s |
| post | 0.02 s |
| user page | 0.03 s |
| other | 0.02 s |

### Conclusions

The application works relatively well, even with tens of millions of database entries. Indexing and pagination were exceedingly beneficial to the performance of the web app; evidently, these methods constitute necessity for a web app with a large database.

Pages load faster when the user is signed out. This is because the web app does not need to compare the visibility of the post with the session user's access permissions.

In order to further speed up front page loading, it is possible to store the number of likes directly in the database, rather than aggregating on each request. This can, for instance, be accomplished by storing an integer in the `Posts` table, and updating it with the SQL `TRIGGER` command.
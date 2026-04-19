# dream-tracker
A simple social platform for recording and tracking sleep quality and the narratives experienced during rapid eye movement dreaming.

## Functionality
Users can
- create an account and sign in
- create new posts, and edit or delete their own posts
- view their own posts as well as posts by other users
- follow other users, receiving their posts in their feeds
- set visibility rules for each of their posts (e.g. public, private, followers only)
- assign categories to their own posts
- search for posts using search queries, categories or statistics
- view users' profile pages, which display the user's posts and statistics
- reply to, like and react to posts
- add posts to curated lists

# Installation

1. Clone the repo and navigate to its directory with a terminal of your choice
2. Install `flask`:

```
$ pip install flask
```

or as a self-contained virtual environment

```
$ python -m venv venv
$ venv/bin/activate
$ pip install flask
```

3. Start the server and navigate to `localhost:5000` with a browser of your choice

```
$ flask run
```

The app will initialize the database and any configurations automatically.
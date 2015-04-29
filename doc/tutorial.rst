.. _demotutorial:

Demo Webapp Tutorial
====================

Getting started is pretty easy. The first thing to do is create a
configuration somewhere on your filesystem.  You'll need to add the correct
values for your configuration. When you're done the file should look something
like this::

    DEBUG = True                              # show traceback if exception is occurred.
    SOURCE_DIR = '/path/to/rst/sources'       # absolute path is required
    BUILD_DIR = '/path/to/build/directory'    # absolute path is required
    DATABASE_URI = 'sqlite:////path/to/sqlite/db'
    SEARCH = 'xapian'
    NOTIFY = ''                               # email address to notify
    MODERATE_ENABLE = False                   # if set True, all comments will be published after moderation
    LOGIN_REQUIRED = False                    # if set True, users need login to see any documentation

Additionally, if you want to use OAuth2 authenticatoin with Google/Github, you need these
settings as well::

    GOOGLE_CONSUMER_KEY = "<your-google-key>.apps.googleusercontent.com"
    GOOGLE_CONSUMER_SECRET = "<your-google-secret>"

    GITHUB_CONSUMER_KEY = "<your-github-key>"
    GITHUB_CONSUMER_SECRET = "<your-github-secret>"


Then you'll need to set an environment variable pointing to your configurate
file. On Linux you can set the environment variable with this command::

    $ export SPHINXWEB_SETTINGS=/path/to/your/configs/sphinxweb.cfg

Once this is done you're ready to build the documentation. Inside the
sphinx-demo-webapp directory execute this command::

    $ python build.py

This will build the documentation, and copy the static files from the build
directory to the webapp's static directory. You're then ready to start the
development server::

    $ python runserver.py

Now you can open up your browser and go to http://127.0.0.1:5000/
to view the documentation.

Moderation
============

Make user moderator::

   $ make-moderator user1@example.com user2@example.com

Permission
===========

Add permission for user::

   $ make-user-permission user1@example.com read

SphinxWeb supports these permissions:

:read: read the document.


Migration
==========

Migrate your database:

   $ alembic upgrade head


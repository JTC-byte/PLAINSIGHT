"""PLAINSIGHT, the application: the case store and the ingest door.

This package is Class C runtime code. It holds no rule of its own about who may
be a subject, what may be retained, or what may leave: those are rank 1 in
doctrine/, and the PSE validation it applies is tools/validate.py, loaded by
path and never copied (app/store/door.py).

The first slice built here is the store (app/store/) and the ingest door, the
views' models (app/model/), the HTTP server on 127.0.0.1 (app/http/), and the
static front end (app/static/); app/README.md says how to open the web. The
store root is PLAINSIGHT_HOME, default %LOCALAPPDATA%\\plainsight, and a root
inside a git working tree is refused (STORE_PATH_IN_REPOSITORY, RT-15). On
LOCAL the store holds tracked, unmodified synthetic corpus files only (EG-2).

Run python -m app --help for the subcommands.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"

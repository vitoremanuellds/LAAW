"""Error type for the LAAW tasks CLI."""


class TaskError(Exception):
    """A recoverable error: print 'tasks: <msg>' to stderr and exit 1.

    All CLI failures raise this; laaw_tasks.cli.main turns it into the
    documented 'tasks: …' message and exit code.
    """

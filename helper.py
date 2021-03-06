from fabric.api import hide, settings
from fabric.colors import blue
from contextlib import contextmanager


def header(txt):
    """Decorate a string to make it stand out as a header. """
    wrapper = "-" * len(txt)
    return blue("\n" + txt + "\n" + wrapper + "\n", bold=True)


@contextmanager
def mute():
    """Run a fabric command without reporting any responses to the user. """
    with settings(warn_only='true'):
        with hide('running', 'stdout', 'stderr', 'warnings'):
            yield


def check_true(string):
    """ Check if an English string seems to contain truth.

    Return a boolean

    Default to returning a False value unless truth is found.
    """
    string = string.lower()
    if string in ['true', 'yes', 'y', '1', 'yep', 'yeah']:
        return True
    else:
        return False

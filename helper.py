from fabricapi import hide, settings
from fabric.colors import blue
from contextlib import contextmanager


def header(txt):
    """Decorate a string to make it stand out as a header. """
    wrapper = "------------------------------------------------------"
    return blue(wrapper + "\n" + txt + "\n" + wrapper, bold=True)


@contextmanager
def mute():
    """Run a fabric command without reporting any responses to the user. """
    with settings(warn_only='true'):
        with hide('running', 'stdout', 'stderr', 'warnings'):
            yield

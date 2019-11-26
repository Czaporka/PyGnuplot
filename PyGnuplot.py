"""
By Ben Schneider

Simple python wrapper for Gnuplot
Thanks to steview2000 for suggesting to separate processes,
    jrbrearley for help with debugging in python 3.4+

Example:
    import PyGnuplot as gp
    import numpy as np
    X = np.arange(10)
    Y = np.sin(X/(2*np.pi))
    Z = Y**2.0
    gp.s([X,Y,Z])  # saves data into tmp.dat
    gp.c("plot 'tmp.dat' u 1:2 w lp)  # send "plot instructions to Gnuplot"
    gp.c("replot 'tmp.dat' u 1:3" w lp)
    gp.p("myfigure.ps")  # creates postscript file
"""
from subprocess import Popen, PIPE
from tempfile import TemporaryFile


DEFAULT_TERM = "x11"  # change this if you use a different terminal


class _GnuPlot:

    def __init__(self, term=DEFAULT_TERM):
        self.term = term
        self.proc = Popen(
            ["gnuplot", "-p"], stdin=PIPE, universal_newlines=True)


class _FigureList(object):

    def __init__(self):
        instance = _GnuPlot()
        self.instances = {0: instance}
        self.current_idx = 0
        self.current_fig = instance

    def get_figure(self, idx=None):
        """Get a Gnuplot instance.

        If `idx` is `None` (default):
            a new `_Instance` is created at max(self.instances)+1.
        If `idx` is not `None` and corresponding `_Instance` exists:
            the `_Instance` is returned.
        If `idx` is not `None` but corresponding `_Instance` doesn't exist:
            a new `_Instance` is created at `idx` and is returned.
        In all cases, the new instance/figure becomes current.
        """
        if idx is None:  # create new figure if no number was given
            idx = max(self.instances) + 1
        instance = self.instances.setdefault(idx, _GnuPlot())
        self.current_idx = idx
        self.current_fig = instance
        return instance


def figure(number=None):
    """Create a new figure or update an existing one.

    >>> figure(2)  # would create or update figure 2
    >>> figure()  # simply creates a new figure
    returns the new figure number
    """
    fig = fl.get_figure(number)
    c("set term {} {}".format(fig.term, number))
    return number


def c(command):
    """Send a command to Gnuplot.

    >>> c("plot sin(x)")
    >>> c("plot 'tmp.dat' u 1:2 w lp")
    """
    proc = fl.current_fig.proc
    print(command, file=proc.stdin)


def s(data, filename="tmp.dat"):
    """Write data to $filename.

    >>> s(data, filename="tmp.dat")  # overwrites/creates tmp.dat
    """
    with open(filename, "w") as fh:
        for items in zip(*data):
            print(*items, file=fh)


def plot(data):
    """Write data to a file and send plot instruction to Gnuplot."""
    with TemporaryFile() as f:
        s(data, f.name)
        c("plot '{}' w lp".format(f.name))


def p(filename="tmp.ps", width=14, height=9, fontsize=12, term=DEFAULT_TERM):
    """Script to make Gnuplot print into a postscript file
    >>> p(filename="myfigure.ps")  # overwrites/creates myfigure.ps
    """
    c("set term postscript size {width}cm, {height}cm color "
      "solid {fontsize} font 'Calibri';".format(
          height=height, width=width, fontsize=fontsize))
    c("set out '{}';".format(filename))
    c("replot;")
    c("set term {}; replot".format(term))


def pdf(filename="tmp.pdf", width=14,
        height=9, fontsize=12, term=DEFAULT_TERM):
    """Script to make Gnuplot print into a pdf file
    >>> pdf(filename="myfigure.pdf")  # overwrites/creates myfigure.pdf
    """
    c("set term pdf enhanced size {width}cm, {height}cm "
      "color solid fsize {fontsize} fname 'Helvetica';".format(
          width=width, height=height, fontsize=fontsize))
    c("set out '{}';".format(filename))
    c("replot;")
    c("set term {}; replot".format(term))


fl = _FigureList()

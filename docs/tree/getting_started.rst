.. ipython:: python
    :suppress:

    import polars

Getting started
===============

Getting started with pygef is easy done by importing the :code:`pygef` library:

.. ipython:: python

    from pygef import Cpt, Bore

or any equivalent :code:`import` statement.

Load a Cpt/Bore file
---------------------

The classes :code:`Cpt` and :code:`Bore` accept two possible inputs:

- the :code:`path` of the file
- the :code:`content`, a dictionary containing the keys: ["string", "file_type"]

    - string: String version of the file.
    - file_type: One of ["gef", "xml"]

If you want to use the :code:`path` then your code should look like this:

.. ipython:: python

    import os

    path_cpt = os.path.join(os.environ.get("DOC_PATH"), "../pygef/test_files/cpt.gef")
    cpt = Cpt(path_cpt)

If you want to use the :code:`content` method:

.. ipython:: python

    with open(path_cpt, encoding="utf-8", errors="ignore") as f:
        s = f.read()
    gef = Cpt(content=dict(string=s, file_type="gef"))

Access the attributes
---------------------

Accessing the attributes of a pygef object is quite easy.
If for example we want to know the (x, y, z) coordinates of the gef we can simply do:

.. ipython:: python

    coordinates = (gef.x, gef.y, gef.zid)
    print(coordinates)

Check all the available attributes in the reference. Everything(or almost) that is contained in the files it is now
accessible as attribute of the :code:`gef` object.

The classes :code:`Cpt` and :code:`Bore` have different attributes, check the reference to learn more about it.

A common and very useful attribute is :code:`gef.df`, this is a :code:`polars.DataFrame` that contains all the rows and
columns defined in the file.

Cpt
...
If we call :code:`cpt.df` on a :code:`cpt` object we will get something like this:

.. ipython:: python

    cpt.df


The number and type of columns depends on the columns originally present in the cpt.

The columns :code:`penetration_length`, :code:`qc`, :code:`depth` are always present.

Suggestion: Instead of using the column :code:`penetration_length` use the column :code:`depth` since this one is corrected with the inclination (if present).

Borehole
.........
If we call :code:`bore.df` on a :code:`bore` object we will get something like this:

.. ipython:: python

    path_bore = os.path.join(os.environ.get("DOC_PATH"), "../pygef/test_files/example_bore.gef")
    bore = Bore(path_bore)
    bore.df


Plot a gef file
---------------

We can plot a .gef file using the method :code:`.plot()`, check the reference to know which are the arguments of the method.

cpt
...
If we use the method without arguments on a :code:`cpt` object we get:

.. ipython:: python
    :okwarning:

    @savefig cpt_plot.png
    cpt.plot(figsize=(6, 8))


borehole
.........
If we use the method without arguments on a :code:`bore` object we get:

.. ipython:: python
    :okwarning:

    @savefig bore_plot.png
    bore.plot()

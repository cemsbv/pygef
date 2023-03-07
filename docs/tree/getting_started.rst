.. ipython:: python
    :suppress:

    import polars

Installing pygef
==================
To install :code:`pygef`, we strongly recommend using Python Package Index (PyPI).
You can install :code:`pygef` with:

.. code-block:: bash

    pip install pygef[map]

We installed the `map` variant of :code:`pygef` which include additional dependencies,
and thereby enable additional functionality.

How to import pygef
===================

Getting started with pygef is easy done by importing the :code:`pygef` library:

.. ipython:: python

    import pygef

or any equivalent :code:`import` statement.

Load a Cpt/Bore file
---------------------

The classes :code:`read_cpt` and :code:`read_bore` accept two possible inputs:

- the :code:`path` of the file
- the :code:`BytesIO` of the file

If you want to use the :code:`path` then your code should look like this:

.. ipython:: python

    import os

    path_cpt = os.path.join(
        os.environ.get("DOC_PATH"), "../tests/test_files/cpt_xml/example.xml"
    )
    cpt = pygef.read_cpt(path_cpt)

Access the attributes
---------------------

Accessing the attributes of a pygef object is quite easy.
If for example we want to know the (x, y, z) coordinates of the gef we can simply do:

.. ipython:: python

    coordinates = (
        cpt.standardized_location.x,
        cpt.standardized_location.y,
        cpt.delivered_vertical_position_offset
    )
    print(coordinates)

Check all the available attributes in the reference. Everything (or almost) that is contained in the files it is now
accessible as attribute of the :code:`gef` object.

The classes :meth:`pygef.cpt.CPTData` and :meth:`pygef.bore.BoreData` have different attributes, check the reference to learn more about it.

A common and very useful attribute is :code:`CPTData.data`, this is a :code:`polars.DataFrame` that contains all the rows and
columns defined in the file.

CPT
...
If we call :code:`CPTData.data` on a :code:`CPTData` object we will get something like this:

.. ipython:: python

    cpt.data


The number and type of columns depends on the columns originally present in the cpt.

The columns :code:`penetration_length`, :code:`qc`, :code:`depth` are always present.

Suggestion: Instead of using the column :code:`penetration_length` use the column :code:`depth` since this one is corrected with the inclination (if present).

Borehole
.........
If we call :code:`BoreData.data` on a :code:`BoreData` object we will get something like this:

.. ipython:: python

    path_bore = os.path.join(
        os.environ.get("DOC_PATH"), "../tests/test_files/bore_xml/DP14+074_MB_KR.xml"
    )
    bore = pygef.read_bore(path_bore)
    bore.data


Plot a gef file
---------------

We can plot a gef file using the method :code:`.plot()`, check the reference to know which are the arguments of the method.

CPT
...
If we use the method without arguments on a :code:`cpt` object we get:

.. ipython:: python
    :okwarning:

    @savefig cpt_plot.png
    pygef.plotting.plot_cpt(cpt)


Borehole
.........
If we use the method without arguments on a :code:`BoreData` object we get:

.. ipython:: python
    :okwarning:

    @savefig bore_plot.png
    pygef.plotting.plot_bore(bore)


Combine Borehole an CPT
........................

.. ipython:: python
    :okwarning:

    # parse BRO bhrgt XML
    path_bore = os.path.join(
        os.environ.get("DOC_PATH"), "../tests/test_files/bore_xml/BHR000000336600.xml"
    )
    bore = pygef.read_bore(path_bore)

    # parse BRO CPT XML
    path_cpt = os.path.join(
        os.environ.get("DOC_PATH"), "../tests/test_files/cpt_xml/CPT000000155283.xml"
    )
    cpt = pygef.read_cpt(path_cpt)

    @savefig bore_cpt_plot.png
    pygef.plotting.plot_merge(bore, cpt)
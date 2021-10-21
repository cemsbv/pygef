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



Classify a cpt
--------------

We can classify a :code:`cpt` object using the method :code:`.classify()`.
The available classification are:

- Robertson(1990) and Robertson(2016)
- Jefferies&Been: available only if :code:`u2` is in the columns of :code:`cpt.df`.

It is possible to use the old (1990) or new(2006) implementation of Robertson.

Robertson(1990):

.. math::
    \begin{align}
    I_c = \sqrt{(3.47 - \log Q_t )^2 + (\log F_r + 1.22)^2}
    \end{align}

where:

.. math::
    \begin{align}
    Q_t &= \frac{q_t - \sigma_{vo}}{\sigma_{vo}'}, \\
    F_r &= \frac{f_s}{q_t - \sigma_{vo}} \times 100, \\
    \end{align}

.. math::
    \begin{align}
    q_t =
    \begin{cases}
    q_c + u_2 (1 - a), & \text{if} \> u_2 \neq 0 \\
    q_c                & \text{otherwise}
    \end{cases}
    \end{align}


Robertson(2006):

.. math::
    \begin{align}
    I_c = \sqrt{(3.47 - \log Q_t )^2 + (\log F_r + 1.22)^2}
    \end{align}

where:

.. math::
    \begin{align}
    Q_t &= \frac{q_t - \sigma_{vo}}{p_a}(\frac{p_a}{\sigma_{vo}'})^n, \\
    n &= 0.381 \times I_c + 0.05 \frac{\sigma_{vo}'}{p_a} - 0.15, \\
    F_r &= \frac{f_s}{q_t - \sigma_{vo}} \times 100, \\
    \end{align}

.. math::
    \begin{align}
    q_t =
    \begin{cases}
    q_c + u_2 (1 - a), & \text{if} \> u_2 \neq 0 \\
    q_c                & \text{otherwise}
    \end{cases}
    \end{align}

The implementation given by Jefferies&Been is the following:

.. math::
    \begin{align}
    I_c = \sqrt{(3 - \log (Q_t \times(1 - u_2) + 1))^2 + (1.5 +1.3 \times \log F_r)^2}
    \end{align}

where:

.. math::
    \begin{align}
    Q_t &= \frac{q_t - \sigma_{vo}}{\sigma_{vo}'}, \\
    F_r &= \frac{f_s}{q_t - \sigma_{vo}} \times 100, \\
    q_t &= q_c + u_2 (1 - a)
    \end{align}


The classification is done for each row of the cpt, and you can get the result for each row.

However, it is also possible to apply a grouping algorithm on the cpt, if you set :code:`do_grouping` to :code:`True`,
and specify the :code:`min_thickness` for a layer to be considered, you will get back a much shorter :code:`polars.DataFrame` with the grouped layers.


Check the reference to learn about all the arguments of the method.

Robertson classification without grouping
.........................................

To get the classification we need to at least pass the attribute :code:`classification` and the water level.
The water level can be given either as :code:`water_level_NAP` or :code:`water_level_wrt_depth`.

.. ipython:: python
    :okwarning:

    cpt.classify(classification="robertson", water_level_NAP=-1)

The classification is given for each row of the cpt, all the parameters(Qt, qt, Bq, ecc..) used for the classification are also returned with the
:code:`polars.DataFrame`.

If you don't want to have so many columns you can just make a selection of them:

.. ipython:: python
    :okwarning:

    df = cpt.classify(classification="robertson", water_level_NAP=-1)
    df[["depth", "soil_type"]]


Robertson classification with grouping
.........................................
We can also apply the grouping algorithm to get a series of layers.

The grouping is a simple algorithm that merge all the layers with :code:`thickness` < :code:`min_thickness`
with the last layer with :code:`thickness` > :code:`min_thickness`.

In order to not make a big error do not use a value for the :code:`min_thickness` bigger then 0.2 m and check the classification made for each row.
The :code:`.plot()` method can be useful for this. (See example below)

.. ipython:: python
    :okwarning:

    cpt.classify(classification="robertson", do_grouping=True, min_thickness=0.2, water_level_NAP=-10)


Plot a classified cpt
---------------------

Passing the argument :code:`classification` to the :code:`.plot()` method a subplot with a classification is added.

.. ipython:: python
    :okwarning:

    @savefig cpt_plot_classification.png
    cpt.plot(classification="robertson", water_level_NAP=-10)


If we pass also the arguments :code:`do_grouping` and :code:`min_thickness` we can plot next to it a subplot with the grouped classification.

.. ipython:: python
    :okwarning:

    @savefig cpt_plot_classification_grouped.png
    cpt.plot(classification="robertson", do_grouping=True, min_thickness=0.2,  water_level_NAP=-10)


Check the reference to learn about all the arguments of the method, you can for example control the grid and the figure size.


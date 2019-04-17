Dasiphora species classification
================================

.. contents::

.. section-numbering::



PROBLEM STATEMENT
-----------------

* Constructing a decision tree for `df`-species;
* Studying relationships between environmental factors and leaf morphometric features;
* Estimating interspecific variability of some morhpometric featrues


MATERIALS AND METHODS
---------------------

Initially, source data were represented as an array, consisting of mixed type variables, 
quantitative and qualitative types, that describe
the morphological featrues of six `df`-species and environmental conditions where thet were collected. 
The array's shape was 590x46 (totally, 589 items were used in the analysis below and 46 features).

Quantitative features were presented as a set of the following variables: ['L1p1l','L1p2l','W1p1l','W1p2l','L2p3l','L2p4l','W2p3l','W2p4l',
'S2p3l','S2p4l','Lkd','Wkd','OtnWLkd','Dvsh','Dosh','Lp','Dpl','Lns','Wns','Lvs','Wvs']


+----------------------------------------------+--------------------+
| Full description of numerical variables goes | here               |
+----------------------------------------------+--------------------+
| Variable abbreviation                        | Description        |
+----------------------------------------------+--------------------+
| L1p1l                                        | Variable meaning   |
+----------------------------------------------+--------------------+
| etc.                                         |                    |
+----------------------------------------------+--------------------+


A subset of qualitative features consisted of ['Dp','Dvl','Dnl','Dc','Dvns','Dnns','Dvvs','Dnvs','Сp', 'Ef'] variables, their meanings presented in the table below:

+-----------------------------------------------+-------------------+
| Full description of qualitative variables goes| here              |
+----------------------------------------------+--------------------+
| Variable abbreviation                        | Description        |
+----------------------------------------------+--------------------+
| Dp                                           | Variable meaning   |
+----------------------------------------------+--------------------+
| etc.                                         |                    |
+----------------------------------------------+--------------------+

And, finally, a subset of variables representing environmental conditions was following:

+------------------------------------------------------+-------------+
| Table of environmental variables and its descriptions|             |
+------------------------------------------------------+-------------+
| Variable abbreviation                                | Description |
+------------------------------------------------------+-------------+
| ALT                                                  | Var. meaning|
+------------------------------------------------------+-------------+
| IC etc.                                              |             |
+------------------------------------------------------+-------------+


Computational environment
~~~~~~~~~~~~~~~~~~~~~~~~~

As an environment for perforiming all kinds of statistical computations, 
we used built on top of Python programming language computational ecosystem. The latter
included: SciPy/NumPy (ref. to. scipy) packages,
Scikit-Learn package (ref.to.sklearn) as a mordern
machine learning toolset (we used some common data preprocessing features (scaling and qualitative features encoding), 
and implementation of the adaptive CART algorithm for decision tree building), 
Pandas (ref.to.pandas project) for performing I/O operations and data cleaning,
as well Matplotlib (ref.to.matplotlib) and Seaborn (ref.to.seabornifexists) packages for visualization purposes.


Data preparation
~~~~~~~~~~~~~~~~

Data preparation operations included: 1) data cleaning, 2) quantitative features scaling/shifting, 3) qualitative features encoding.
During automatic data cleaning all rows, that included not-a-number or non-existing values were removed from the dataset. The only one
item with a non-exisiting value was removed during this stage.

Scaling and shifting procedures were applied to all quantitative columns in the dataset. It consisted in removing the mean and scaling 
to unity standard deviation.

To encode qulitative features, we used one-hot encoding transformation implemented in  Scikit-Learn package. This, in turn, led to
extending the number of columns of the data frame. 

We didn't use any of dimensinality reduction approaches, because all of these lead to smoothing and hiding original 
meanings of features, that are important when dealing with building taxonomic classifications.


Decision tree building
~~~~~~~~~~~~~~~~~~~~~~


We used an optimized version of the CART algorithm implemented in the Scikit-Learn package to construct 
a binary decision tree. When all of the morphological features were used, this led to a quite simple tree. It was much simpler
than one based on  qualitative features only. 
The algorithm  automatically selected a relatively small subset of morphological parameters,
that yeilded to classification tree of the followign form (see fig.1)

.. class:: no-web

   .. image:: https://raw.githubusercontent.com/vbgi/df/master/images_final/dtree_simple.png
       :alt: Decision tree built with help of the CART algo
       :width: 100%
       :align: center  

'''
Main module used to get random values

'''

import random
from numpy import random as nrandom
import numpy as np


def irand(a, b, size=1):
    '''Returns array of uniformly distributed floats
    in a given interval

    :param a: low bound of an interval
    :param b: high bound of an interval
    :param size: size of array of random values to be generated
    :type a: float
    :type b: float
    :type size: int
    :return: array of uniformly distributed values in a given interval `(a ,b)`
    :rtype: list

    **How it works**

        It just `nrandom.uniform` function from `numpy` package.

    :Example:

    .. code-block:: python

        irand(10, 20, 100)
        # will create array of random values
        # of length 100 from range (10, 20)
    '''
    return nrandom.uniform(a, b, size).tolist()


def place_spatially(bbox=[(0, 1), (0, 1)], probgrid=None, size=1):
    '''
    Returns array of coordinates for randomly distributed points
    in the `bbox` taking into account probabilities defined by `numpy.array`
    `probgrid`. If no `probgrid` is defined, returns coordinates of
    `size` uniformly distributed points in the `bbox`.

    :param bbox: bounding box, i.e. `[(min_x, max_x), (min_y, max_y)]`
    :param probgrid: probability density of point occurence in `bbox`,
                     `probgrid` is 2D `numpy.array`
    :param size: the number of points to be randomly placed
    :type bbox: list
    :type probgrid: `numpy.array`
    :type size: int
    :return: `(X,Y)` -- arrays of x- and y-coordinates of points placed
             according to `probgrid`.

    **How it works**

        Long description

    '''

    m, n = np.shape(probgrid)
    dx = (bbox[0][1] - bbox[0][0]) / float(n)
    dy = (bbox[1][1] - bbox[1][0]) / float(m)
    if probgrid is not None:
        probgrid = probgrid / np.sum(probgrid)  # Normalize in any case!
        xyplaces = nrandom.multinomial(size, probgrid.ravel())
        XB, YB = np.meshgrid(np.arange(bbox[0][0], bbox[0][1], dx),
                             np.arange(bbox[1][0], bbox[1][1], dy))
        XB = XB.ravel()
        YB = YB.ravel()
        inds1 = xyplaces == 1
        if sum(inds1) > 0:
            X = XB[inds1] + nrandom.uniform(0, dx, sum(inds1))
            Y = YB[inds1] + nrandom.uniform(0, dy, sum(inds1))
        else:
            X = np.array([])
            Y = np.array([])
        inds2 = xyplaces > 1
        # TODO: Is it possible to avoid for-loop here?
        for xb, yb, nn in zip(XB[inds2], YB[inds2], xyplaces[inds2]):
            toX = np.array([xb]*nn)
            toY = np.array([yb]*nn)
            toX += nrandom.uniform(0, dx, len(toX))
            toY += nrandom.uniform(0, dy, len(toY))
            X = np.hstack([X, toX])
            Y = np.hstack([Y, toY])
    else:
        X = nrandom.uniform(bbox[0][0], bbox[0][1], size=size)
        Y = nrandom.uniform(bbox[1][0], bbox[1][1], size=size)
    return X, Y

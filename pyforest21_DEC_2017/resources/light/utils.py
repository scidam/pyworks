try:
    from scipy.spatial import ConvexHull
except ImportError:
    pass
    # TODO: scipy is required here!!!

import numpy as np


def point_in_triangle(e1, e2, p):
    '''Checks if point lies within a triangle defined
    by basis vectors :math:`e_1` and :math:`e_2`.
    '''

    # TODO: Some code refactoring needed: optimization
    res = np.dot(np.linalg.pinv(np.vstack([e1, e2]).T), p)
    if (res >= -4.0e-16).all() and res.sum() <= 1:
        return True
    else:
        return False


def poly3d_intersection(points, source, direction):
    '''Finds intersections of a convex hull of points
    by the line started at a given point in a given
    direction.

    # TODO: Docs needed
    '''
    _points = np.array(points)
    _direction = np.array(direction)
    _direction = _direction/(_direction[0]*_direction[0] +
                             _direction[1]*_direction[1] +
                             _direction[2]*_direction[2]) ** 0.5
    _source = np.array(source)
    chull = ConvexHull(_points)
    solvability = np.dot(chull.equations[:, :-1], _direction)
    intersections = []
    for face, eq, solv in zip(chull.simplices, chull.equations, solvability):
        p0 = _points[face[0]]
        p1 = _points[face[1]]
        p2 = _points[face[2]]
        res = -eq[-1] - np.dot(eq[:-1], _source)
        res /= solv
        if res > 0.0:
            p = _source + res * _direction
            if point_in_triangle(p1 - p0, p2 - p0, p - p0):
                intersections.append(p)
    if intersections:
        intersections = np.array(intersections).round(decimals=14)
        # Uniquify rows, there are lots of redundant points might be...
        _aux = np.ascontiguousarray(intersections).view(np.dtype((np.void,
                                                              intersections.dtype.itemsize *
                                                              intersections.shape[1]))
                                                        )
        _, idx = np.unique(_aux, return_index=True)
        return intersections[idx]
    else:
        return []


def poly3d_qhull_intersection(qhull, source, direction):
    '''Finds intersections of a convex hull of points
    by the line started at a given point in a given
    direction.
    # TODO: Docs needed
    '''
    _points = qhull.points[qhull.vertices, :]
    _direction = np.array(direction)
    _direction = _direction/np.linalg.norm(_direction)
    _source = np.array(source)
    solvability = np.dot(qhull.equations[:, :-1], _direction)
    intersections = []
    for face, eq, solv in zip(qhull.simplices, qhull.equations, solvability):
        p0 = _points[face[0]]
        p1 = _points[face[1]]
        p2 = _points[face[2]]
        res = -eq[-1] - np.dot(eq[:-1], _source)
        res /= solv
        if res > 0.0:
            p = _source + res * _direction
            if point_in_triangle(p1 - p0, p2 - p0, p - p0):
                intersections.append(p)
    if intersections:
        intersections = np.array(intersections).round(decimals=14)
        # Uniquify rows, there are lots of redundant points might be...
        _aux = np.ascontiguousarray(intersections).view(np.dtype((np.void,
                                                              intersections.dtype.itemsize *
                                                              intersections.shape[1]))
                                                        )
        _, idx = np.unique(_aux, return_index=True)
        return intersections[idx]
    else:
        return []

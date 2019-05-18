
import numpy as np
import shapely
import os
import re
import pandas as pd


class LeafContour:
    """Quite old class to handle leaf contours
    """

    def __str__(self):
        return 'Contour leaf object: nodes: %s, dpc: %s' %(len(self.points), self.dpc)

    def __init__(self, dpc, points, description=None):
        self.dpc = dpc
        self.points = np.array(points,dtype=np.float64)
        self.description = description
        self.relpoints = None
        self.pcapoints = None
        self.datasource = None

        # Contour properties
        self._length = None
        self._area = None
        self._curvatures = None
        self._inertia = None
        self._maxminxy = None

    @property
    def area(self):
        return self._area

    @area.getter
    def area(self):
        from shapely.geometry import Polygon
        if  self.pcapoints == None:
            self.interpolated(self)
        try:
            polygon = Polygon(self.ppts)
            self._area = polygon.area
        except:
            self._area = None
        return self._area

    @property
    def length(self):
        """Length of the contour"""

    @length.getter
    def length(self):
        from shapely.geometry import Polygon
        if  self.pcapoints == None:
            self.interpolated(self)
        try:
            polygon = Polygon(self.ppts)
            self._length = polygon.length
        except:
            self._length = None
        return self._length

    @property
    def inertia(self):
        pass

    @inertia.getter
    def inertia(self):
        if  self.pcapoints == None:
            self.interpolated(self)
        vals = [np.sum(np.array(self.pcapoints[0]) ** 2), np.sum(np.array(self.pcapoints[1]) ** 2)]
        self._inertia = (max(vals), min(vals))
        return self._inertia

    @property
    def coordinates(self):
        pass

    @coordinates.getter
    def coordinates(self):
        if self.pcapoints == None:
            self.interpolated(self)
        return np.array(self.pcapoints)

    @property
    def maxminxy(self):
        pass

    @maxminxy.getter
    def maxminxy(self):
        if  self.pcapoints == None:
            self.interpolated(self)
        self._maxminxy = (min(self.pcapoints[0]), max(self.pcapoints[0]), \
                          min(self.pcapoints[1]), max(self.pcapoints[1]))
        return self._maxminxy

    @property
    def position(self):
        if  self.pcapoints == None:
            self.interpolated(self)
        indleft = np.argmin(self.pcapoints[1])
        indright = np.argmax(self.pcapoints[1])
        valleft = self.pcapoints[0][indleft]
        valright = self.pcapoints[0][indright]
        return ((valleft + valright) * 0.5 - \
                (self.maxminxy[1] + self.maxminxy[0]) * 0.5) / (self.maxminxy[1] - self.maxminxy[0])

    @property
    def curvatures(self):
        pass

    @curvatures.getter
    def curvatures(self):
        from scipy import interpolate
        if  self.pcapoints == None:
            self.interpolated(self)
        try:
            tck,unew = interpolate.splprep([np.array(self.ppts)[:,0] / max(np.abs(np.array(self.ppts)[:, 0])), np.array(self.ppts)[:, 1] / max(np.abs(np.array(self.ppts)[:, 1]))], s=0.0)
            dr = np.array(interpolate.splev(unew, tck, der=1)).transpose()
            ddr = np.array(interpolate.splev(unew, tck, der=2)).transpose()
            curvature = [np.linalg.norm(np.cross(x, y)) / np.linalg.norm(x) ** 3 for x, y in zip(dr, ddr)]
            self._curvatures = [min(curvature), max(curvature), np.mean(curvature), np.std(curvature),\
                              np.max(curvature[int(len(curvature) / 2.0) -\
                                               int(len(curvature) / 8.0):int(len(curvature) / 2.0) +\
                                               int(len(curvature) / 8.0)]), max(max(curvature[-5:]), max(curvature[:5]))]
        except:
            self._curvatures=list()
        return self._curvatures

    @property
    def rawcurvatures(self):
        from scipy import interpolate
        if  self.pcapoints==None:
            self.interpolated(self)
        try:
            tck,unew = interpolate.splprep([np.array(self.ppts)[:, 0] / max(np.abs(np.array(self.ppts)[:, 0])), np.array(self.ppts)[:, 1] / max(np.abs(np.array(self.ppts)[:, 1]))], s=0.0)
            dr = np.array(interpolate.splev(unew, tck, der=1)).transpose()
            ddr = np.array(interpolate.splev(unew, tck, der=2)).transpose()
            curvature = np.array([np.linalg.norm(np.cross(x, y)) / np.linalg.norm(x) ** 3 for x, y in zip(dr,ddr)])
        except:
            curvature = np.array([])
        return curvature

    @staticmethod
    def centermass(self):
        massx=np.mean(self.points[:, 0])
        massy=np.mean(self.points[:, 1])
        newx=self.points[:, 0] - massx
        newy=self.points[:, 1] - massy
        self.relpoints=np.array([newx, newy])

    @staticmethod
    def interpolated(self, points=200):
        from sklearn.decomposition import PCA
        from scipy import interpolate
        if self.relpoints is None:
            self.centermass(self)
        pca = PCA(n_components=2)
        tofit=[[x, y] for x,y in zip(self.relpoints[0, :] / self.dpc, self.relpoints[1, :] / self.dpc)]
        tofit.append(tofit[0])
        pca.fit(tofit)
        transformed = pca.transform(tofit)
        self.transformed = transformed
        tck, u = interpolate.splprep([transformed[:, 0], transformed[:, 1]], s=0.0)
        unew = np.arange(0, 1.0, 1.0 / float(points))
        out = interpolate.splev(unew,tck)
        self.pcapoints = [out[0], out[1]]
        self.ppts = [(x, y) for x, y in zip(self.pcapoints[0], self.pcapoints[1])]


def parse_file(filename):
    """Read a specific TPS file"""

    data = dict()
    ind = 0
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if s.startswith('LM'):
                ind += 1
                data.setdefault('data', []).append(list())
            elif s.startswith('SCALE'):
                data.setdefault('scale', float(s.split("=")[-1]))
            elif re.match('^\d+', s):
                data.setdefault('data', [])[-1].append(list(map(float, s.split())))
        data.setdefault('filename', filename)
    return data


def walk_throughout_path(path):
    data = list()
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.lower().strip().endswith('tps'):
                data.append(parse_file(os.path.join(root, f)))
                data[-1]['data'] = [LeafContour(1 / data[-1]['scale'], k) for k in data[-1]['data']]
    return data


if __name__ == '__main__':
    data = walk_throughout_path('.')
    result = []
    for d in data:
        ind = 0
        for lc in d.get('data'):
            result.append([d.get('filename') + '_' + str(ind), lc.maxminxy[1]-lc.maxminxy[0], lc.maxminxy[-1]-lc.maxminxy[-2], lc.area, lc.length])
            ind += 1
    df = pd.DataFrame(result, columns=['filename', 'length', 'width', 'area', 'perimiter'])
    df.to_csv('output.csv')



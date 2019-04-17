#
import numpy as np
from scipy import optimize as opt
from scipy import weave
from scipy.spatial import Delaunay, KDTree
import pandas as pd
import random

cyl_threshold=0.04


def scross(a):
    return np.array([[0.0,-a[2],a[1]],[a[2],0.0, -a[0]],[-a[1], a[0],0.0]])


class Cylinder:
    '''
    My favorite cylinder ... to be fitted.

    '''
    def __init__(self):
#         self.u = 0.0 # used for computing n
#         self.v = 0.0 # used for computing n
        self.R2 = 1 # Radius of the cylinder
#         self.n = None #unity vector of the axes of symmetry of the cylinder
        self.origin = np.array([0.0, 0.0, 0.0]) # Coordinates of the cylinder's origin
        self.n = np.array([0.0, 0.0, 0.0]) # Coordinates of the cylinder's origin
        #self.h = 0.0 # Height of the cylinder from origin in 'n' direction.
        self.l1=1
        self.l2=1

    def set_params(self,n,origin,R2,l1,l2):
        self.origin = origin
        self.R2 = R2
        self.n = n
        self.l1 = l1
        self.l2 = l2

#         self.n = np.array([np.cos(v)*np.cos(u), np.cos(v)*np.sin(u), np.sin(v)])

    def fit_cloud(self,cloud):
        '''
        cloud is nx3 array of coordinates to be fitted.

        This function returns mean residual of points departure from cylinder shape.
        '''
        icloud = cloud - self.origin
        return np.linalg.norm(np.cross(icloud, self.n).T,axis=0)**2-self.R2

    def equations(self,cloud):
        result=[]
        icloud = cloud - self.origin
        result.append(np.sum(np.linalg.norm(np.cross(icloud, self.n).T,axis=0)**2-self.R2))
        result.append(np.dot(self.n,self.origin))
        result.append(np.dot(self.n,self.n)-1.0)
        x=np.sum(np.array([np.dot(np.dot(scross(x).T,scross(x)),self.n)*z for x,z in zip(icloud,np.linalg.norm(np.cross(icloud, self.n).T,axis=0)**2-self.R2)]),axis=0)+self.l1*self.origin+self.l2*self.n
        result.extend(x.tolist())
        y=np.sum(np.array([np.dot(np.dot(scross(self.n).T,scross(self.n)),x)*z for x,z in zip(icloud,np.linalg.norm(np.cross(icloud, self.n).T,axis=0)**2-self.R2)]),axis=0)+self.l1*self.n
        result.extend(y.tolist())
        return result

def estimate_cylinder(cloud, maxiter=10):
    mycloud = np.copy(cloud)

    def to_optimize(x,c=None, cloud=None):
        c.set_params(np.array([x[0],x[1],x[2]]),np.array([x[3],x[4],x[5]]), x[6],x[7],x[8])
        return c.equations(cloud)

    myc = Cylinder()
    init_origin=np.mean(mycloud, axis=0)
    x0 = [0,0,1.0,init_origin[0], init_origin[1], init_origin[2], 0.1, 1.0, 1.0]
    done = False
    indx = 0
    res, infores, ier, msg=opt.fsolve(to_optimize, x0, args=(myc,mycloud))
    if ier == 1:
        return res
    else:
        return None;


class Cloud:
    def __init__(self, cloud):
        self.xmax = np.max(cloud[:,0])
        self.xmin = np.min(cloud[:,0])
        self.ymax = np.max(cloud[:,1])
        self.ymin = np.min(cloud[:,1])
        self.zmax = np.max(cloud[:,2])
        self.zmin = np.min(cloud[:,2])
        self.cloud = cloud
        self.kdtree = KDTree(cloud)

    def find_suspecious_point(self, h, dh, R):
        ztrues = (self.cloud[:,2]>=h)*(self.cloud[:,2]<h+dh)
        mycloud = self.cloud[ztrues]
        count = max(int((self.xmax-self.xmin)/R/2.0),int((self.ymax-self.ymin)/R/2.0))
        myhist, xedges, yedges = np.histogram2d(mycloud[:,0],mycloud[:,1],count)
        myhist=np.array(myhist)
        maxs=np.where(myhist[::-1]==myhist.max())
        xinterval =[xedges[maxs[0][0]], xedges[maxs[0][0]+1]]
        yinterval =[yedges[maxs[0][1]], xedges[maxs[0][1]+1]]
        xtrues=(self.cloud[:,0]>=xinterval[0])*(self.cloud[:,0]<xinterval[1])
        ytrues=(self.cloud[:,0]>=yinterval[0])*(self.cloud[:,0]<yinterval[1])
        return (self.cloud[xtrues*ytrues], xtrues*ytrues)


    def find_initial_cylinder(self, Rinit=0.4, maxiter=10000):
        done = False
        indx = 0
        while (~done) or (indx<maxiter):
            pcloud, pindeces=self.find_suspecious_point(1.0,1.0,Rinit)
            nearest=self.kdtree.query_ball_point(random.choice(pcloud),3*Rinit)
            estimate_cylinder(pcloud[nearest])
            pdb.set_trace()

    def __str__(self):
        return 'Point cloud with %s points.'%self.cloud.shape[0]

# def get_normal(cloud,triangular,idx):
#     '''
#     Get point cloud normal at point with index eq to idx.
#     Input cloud assumed to be a nx3 array.
#     '''
#     point=cloud[idx]
#     ontriangles=triangular.simplices[tri.find_simplex(point)]
#     ontriangles.remove(point)
#     vectors=cloud[ontriangles]-point
#
#
#     vectors=
#
#     simpleces=triangular.find_simplex(points)
#
#     import matplotlib.pyplot as plt
#
#     plt.plot(points[:,0], points[:,1], 'o')
#     plt.show()
#     print simpleces








# from sklearn.datasets import make_circles
# # w = np.array(pd.read_table('tree.dat'))
#
# w=make_circles(300, factor=1, noise=0.0001)
# w=4*w[0]+5
# r=np.matrix(20*np.random.rand(300))
# w=np.array(np.hstack([w,r.T]))
#
#
# #Arbitrary vector rotation
# # Rotate inputs on angle 'x' around OZ
# rotmatOZ=lambda x: np.array([[np.cos(x),-np.sin(x),0],[np.sin(x), np.cos(x), 0],[0,0,1]])
#  #Rotate inputs on angle 'x' around OY
# rotmatOY=lambda x: np.array([[np.cos(x),0,-np.sin(x)],[0, 1, 0],[np.sin(x),0,np.cos(x)]])
#  #Rotate inputs on angle 'x' around OX
# rotmatOX=lambda x: np.array([[1,0,0],[0, np.cos(x), -np.sin(x)],[0,np.sin(x),np.cos(x)]])
#
# getrotmat=lambda x,y,z: np.dot(np.dot(rotmatOX(x),rotmatOY(y)),rotmatOZ(z))
# #
# w=np.dot(getrotmat(*np.random.rand(3)),w.T).T
#
# tri=Delaunay(w)







data=np.recfromtxt('tree.dat')
data=np.array(data)
myc=Cloud(data)
myc.find_initial_cylinder()

print myc
sfd


# x0=x
# c.set_params(np.array([x[0],x[1],x[2]]),np.array([x[3],x[4],x[5]]), x[6],x[7],x[8])
# print c.equations(w)
# dfg

# print rress



# print len(x0)
#
# res = opt.minimize(to_optimize, x0, method='BFGS', options={'xtol': 1e-10, 'disp': True}, args=(c,w))
#
# print res, c.n













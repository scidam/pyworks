import pcl
import uuid
import numpy as np
from copy import deepcopy
import pdb
import time
from pylab import *
from mpl_toolkits.mplot3d import axes3d
from scipy import optimize as opt
import scipy.spatial as spat
import vtkex

#--------------------------Initial Search parameters-----------------------------
RMIN_STEM = 0.3
RMAX_STEM = 0.5
DPU = 800
KMEAN = 100
MAXDIST = 0.05
MAXITER = 1000
NORM_DIST_WEIGHT = 0.01
INNER_ITERATIONS = 3
MAIN_SURFACE_NORMAL = np.array([0.0, 0.0, 1.0])  # should be unity vector
STEM_DEV_FORM_NORMAL = 0.9
INITIAL_STEM_HEIGHT = 6 * RMIN_STEM

#---------------------------------------------------------------------------------

#R_PATCH_MAX = 0.01 # 3cm (centimeters)
R_FILTER_MIN = 0.1 # If no points



#---------------------------------------------------------------------------------


#---------------------------Auxilary classes--------------------------------------
class Node:
    def __init__(self, cyl, left=1, right=2):
        self.cyl = cyl
        self.left = left
        self.right = right
    def __str__(self):
        return '(' + str(self.left) + ',' + str(self.right) + ')'
    def __repr__(self):
        return self.__str__()
    @property
    def is_leaf_node(self):
        return True if (self.right - self.left) == 1 else False

class CylinderHierarchy:
    '''Cylinders hierarchy that will describe a tree (real tree in the forest!).'''
    def __init__(self):
        self.nodes = []
    @property
    def rights(self):
        return np.array([x.right for x in self.nodes], dtype=np.int32)
    @property
    def lefts(self):
        return np.array([x.left for x in self.nodes], dtype=np.int32)
    def add_root(self, node):
        newnode = Node(node.cyl)
        if not self.nodes:
            newnode.left = 1
            newnode.right = 2
        else:
            newnode.right = self.rights.max() + 2
            newnode.left = 1
            for item in self.nodes:
                item.left += 1
                item.right += 1
        self.nodes.append(newnode)

    def is_root_node(self, node):
        return True if node.right == self.rights.max() else False

    def get_all_children(self, node, self_include=False):
        children = [n for n in self.nodes if (n.right < node.right) and (n.left > node.left)]
        if self_include:
            children.append(node)
        return children

    def _get_two_nearest_siblings(self, node):
        leftsibling = (node.left - self.rights == 1)
        rightsibling = (self.lefts - node.right == 1)
        if leftsibling.sum() > 1 or rightsibling.sum() > 1:
            raise TypeError, 'Error in construction of cyl-hierarchy'
        res = []
        if leftsibling.any():
            res.append(leftsibling.argmax())
        if rightsibling.any():
            res.append(rightsibling.argmax())
        return res

    def get_siblings(self, node, self_include=False):
        def _check_status(ind):
            ind_trues = [x[0] for x in pool]
            return True if self.nodes[ind] not in ind_trues else False
        def _select_false_node(pool):
            for item in pool:
                if item[1] == False:
                    return item
            return None
        done = False
        pool = []
        nearests = self._get_two_nearest_siblings(node)
        if nearests:
            pool.extend([(self.nodes[x], False) for x in nearests])
        else:
            done = True
        while not done:
            selected = _select_false_node(pool)
            if selected:
                nearests = self._get_two_nearest_siblings(selected[0])
                pending = [(self.nodes[x], False) for x in nearests if _check_status(x)]
                pool.extend(pending)
                newval=(selected[0],True)
                pool.remove(selected)
                pool.append(newval)
            else:
                done = True
        if self_include:
            res = [x[0] for x in pool]
        else:
            res = [x[0] for x in pool if x[0]!=node]
        return res

    def add_child(self, node, child):
        assert node in self.nodes, "Node should be in the main set of nodes."
        if node.is_leaf_node:
            child.left = node.left + 1
            child.right = child.left + 1
            for item in self.nodes:
                if (item.right > node.left):
                    if item.left>node.left:
                        item.left += 1
                        item.right += 2
                    else:
                        item.right += 2
            self.nodes.append(child)
        else:
            raise TypeError, "This function is for leaf nodes only."

    def insert_node(self, node, child, side='left'):
        ''' Side should be left or right'''
        if self.is_root_node(node) and len(self.nodes) == 1:
            raise TypeError, "Could not insert node to the root node. use add_child."
        if side == 'left':
            for item in self.nodes:
                if item.right > node.left:
                    if item.left >= node.left:
                        item.left += 2
                    item.right += 2
                    child.left = node.left - 2
                    child.right = node.right - 2
        elif side == "right":
            for item in self.nodes:
                if item.right > node.right:
                    if item.left > node.left:
                        item.left += 2
                    item.right += 2
                    child.left = node.right + 1
                    child.right = node.right + 2
        self.nodes.append(child)

    def force_insert_node(self, node, child):
        if self.is_root_node(node) and len(self.nodes) == 1:
            self.add_child(node, child)
        elif self.is_root_node(node):
            whatnode = self.nodes[np.argmax(self.lefts==2)]
            self.insert_node(whatnode, child)
        else:
            self.insert_node(node, child)
    @property
    def root_node(self):
        return self.nodes[self.rights.argmax()] or None

    def delete_node(self,node):
        '''
        Deletes node from a tree. All child nodes are deleted too.
        '''
        assert node in self.nodes, 'Node should be included into main node array'
        if node.is_leaf_node:
            for item in self.nodes:
                if item.right>node.right:
                    if item.left>node.left:
                        item.left-=2
                    item.right-=2
            self.nodes.remove(node)
        elif self.is_root_node(node):
            self.nodes=[]
        else:
            children = self.get_all_children(node,self_include=True)
            for item in children:
                self.delete_node(item)

class Cylinder:
    def __init__(self, origin, direction, radius, start, stop):
        '''
      Model of a finite cylinder.
      origin is an array of length 3, lies on the axis of symmetry of the cylinder;
      direction a unity vector of length 3, describes cylinders axis of symmentry;
      radius - no comments;
      start,stop - scalars describe start and end of the cylinder on its' axis;

      pk - automatically assigned primary key of the cylinder
    '''

        self.o = origin
        self.l = direction/np.linalg.norm(direction)
        self.r = radius
        self.a = start
        self.b = stop
        self.pk = uuid.uuid4().hex
        self.n = self._get_n(origin,self.l)
        self.amat = self._a_mat(origin,self.l)
        self.iamat = np.linalg.pinv(self.amat)

    def __str__(self):
        return 'Cylinder: o=(%.5f,%.5f,%.5f), l=(%.5f,%.5f,%.5f), r=%.5f,a=%.5f,b=%.5f'%(self.o[0],self.o[1],self.o[2],self.l[0],self.l[1],self.l[2],self.r,self.a,self.b)

    def _get_n(self,r0,l):
        '''
        Compute orthogonal vector to l vector
        '''
        EPS1 = 1.0e-13
        if abs(np.cross(r0,l).any())>EPS1:
            n = np.cross(r0,l)
            n = n/np.linalg.norm(n)
        elif abs(np.cross(l, [0.0,0.0,1.0]).any())>EPS1:
            n = np.cross(l,[0.0,0.0,1.0])
        elif abs(np.cross(l, [0.0,1.0,0.0]).any())>EPS1:
            n = np.cross(l,[0.0,1.0,0.0])
        elif abs(np.cross(l, [1.0,0.0,0.0]).any())>EPS1:
            n = np.cross(l,[1.0,0.0,0.0])
        return np.array(n)

    def _a_mat(self,r0,l):
        'l,n - assumed to be unit vectors'
        n = self._get_n(r0,l)
        e = np.cross(n,l)
        return np.matrix([e,n,l])

#---------------------------------------------------------------------------------
def cydistance(c1,c2):
    '''
    Computes distance between cylinders
    '''
    assert isinstance(c1,Cylinder) and isinstance(c2,Cylinder),'Inputs should be instances of the Cylinder class'
    def r_mat(phi):
        'rotation matrix'
        return np.matrix([[np.cos(phi), -np.sin(phi), 0.0], [np.sin(phi), np.cos(phi), 0.0], [0.0,0.0,1.0]])

    def distance(x0):
        '''
        0<=t1,t2<=1
        0<=phi1,phi2<=2pi
        '''
        t1,phi1,t2,phi2 = x0[0],x0[1],x0[2],x0[3]
        r1 = np.matrix(c1.o+c1.a*c1.l+c1.l*t1*(c1.b-c1.a)).T+c1.r*c1.iamat*r_mat(phi1)*c1.amat*np.matrix(c1.n).T
        r2 = np.matrix(c2.o+c2.a*c2.l+c2.l*t2*(c2.b-c2.a)).T+c2.r*c2.iamat*r_mat(phi2)*c2.amat*np.matrix(c2.n).T
        return ((r1-r2).T*(r1-r2))[0,0]
    x0 = opt.differential_evolution(distance,[(0.0,1.0), (0,2.0*np.pi),(0.0,1.0),(0.0,2.0*np.pi)])
    print x0.success, 'Result = ',np.sqrt(distance(x0.x))
    return np.sqrt(distance(x0.x))

#     done = False
#     ind = 1
#     INDMAX = 200
#     x0=np.zeros(4)
#     gt1 = lambda t1: distance([t1,x0[1],x0[2],x0[3]])
#     gt2 = lambda t2: distance([x0[0],x0[1],t2,x0[3]])
#     gphi1 = lambda phi1: distance([x0[0],phi1,x0[2],x0[3]])
#     gphi2 = lambda phi2: distance([x0[0],x0[1],x0[2],phi2])
#     distances=[]
#     while ((not done)and(ind<INDMAX)):
#        x0[0] = opt.fminbound(gt1,0.0,1.0)
#        x0[2] = opt.fminbound(gt2,0.0,1.0)
#        x0[1] = opt.fminbound(gphi1,0.0,2.0*np.pi)
#        x0[3] = opt.fminbound(gphi2,0.0,2.0*np.pi)
#        distances.append(distance(x0))
#        ind+=1
#        if ind>3:
#            if abs(distances[-2]-distances[-1])<1.0e-13:
#                done = True
#     return np.sqrt(distances[-1])


def minpoints(r, h, dpu):
    return np.pi * 2 * r * h * dpu

def filter_preliminary(cloud):
    '''
      Returns filtered cloud. Preprocessed to find initial stem
    '''
    projpcl = np.dot(cloud, MAIN_SURFACE_NORMAL)
    print 'projpcl',projpcl.max(), projpcl.min(), RMIN_STEM
    hist, bin_edges = np.histogram(projpcl, bins=int((projpcl.max() - projpcl.min()) / RMIN_STEM))
    org_axe = bin_edges[np.argmax(hist > 2.0 * RMIN_STEM * np.pi * RMIN_STEM * DPU)-1]
    return cloud[(projpcl >= org_axe) * (projpcl <= org_axe + INITIAL_STEM_HEIGHT)]

def find_initial_stem(pointcloud):
    '''It is assumed the stem is unique (no two stems per tree occur:)
      Auxilary cylinders are stored in cylinders array of the following form
        cylinders = [ (num_of_vertices, cylinder model returned by pcl), ..., ...]'''
    MINPOINTS = DPU * 4.0 * RMIN_STEM * (np.pi * RMIN_STEM)
    cylinders = []
    currentcloud = pointcloud
    for ind in xrange(INNER_ITERATIONS):
        print 'Current iteration', ind
        seg = currentcloud.make_segmenter_normals(ksearch=KMEAN)
        seg.set_radius_limits(RMIN_STEM, RMAX_STEM)
        seg.set_optimize_coefficients(True)
        seg.set_model_type(pcl.SACMODEL_CYLINDER)
        seg.set_normal_distance_weight(NORM_DIST_WEIGHT)
        seg.set_method_type(pcl.SAC_RANSAC)
        seg.set_max_iterations(MAXITER)
        seg.set_distance_threshold(MAXDIST)
        try:
            indices, model = seg.segment()
        except:
            break
            print 'Exception during segmentation'
        if len(indices) > MINPOINTS:
            print 'I have found a cylinder with %s vertices, of radius %s' % (len(indices), model[-1])
            cylinders.append((len(indices), model, indices))  # Accumulate cylinders
        else:
            print 'Too low points'
            break
        currentcloud = currentcloud.extract(indices, negative=True)
    #----------------Filtering over found cylinders -------------------------
    print 'Current cylinder candidates: ', len(cylinders)
    fcyl = filter(lambda x: np.abs(np.dot(x[1][3:6], MAIN_SURFACE_NORMAL)) > STEM_DEV_FORM_NORMAL, cylinders)
    print 'Current cylinder candidates after filtering: ', len(fcyl)
    fcyl.sort(lambda x, y:-1 if x[0] >= y[0] else 1)
    return fcyl[0]

def get_cylinder_from_model(model,cloud):
    assert len(model)==7, "Model should be a 7D-vector"
    l = np.array(model[3:6])/np.linalg.norm(model[3:6]) #direction
    r = model[-1] #radius
    o = np.array(model[0:3]) #origin
    #model describe infinite cylinder, This routine make a finite one from it.
    projpcl = np.dot(cloud, l) - np.dot(o,l)
    hist, bin_edges = np.histogram(projpcl, bins=10)
    bin_height = bin_edges[1]-bin_edges[0]
    first = None
    last = None
    print 'Current radiuds is r=', r, bin_height
    for ind,item in enumerate(hist):
        print 'Current state:', ind, item,minpoints(r,bin_height,DPU)
        if (item>=minpoints(r,bin_height,DPU)) and (first is None):
            first =  bin_edges[ind]
        elif first:
            last = bin_edges[ind+1]
    if last is None and first:
        last = first + bin_height
    print 'L&F:', last, first
    if last and first:
        c = Cylinder(o,l,r,first,last)
    else:
        c = None
    return c

def extract_cylinders(pointcloud,rmax):
    cylinders = []
    currentcloud = pointcloud
    for ind in xrange(INNER_ITERATIONS):
        seg = currentcloud.make_segmenter_normals(ksearch=KMEAN)
        seg.set_radius_limits(0.01, rmax)
        seg.set_optimize_coefficients(True)
        seg.set_model_type(pcl.SACMODEL_CYLINDER)
        seg.set_normal_distance_weight(NORM_DIST_WEIGHT)
        seg.set_method_type(pcl.SAC_RANSAC)
        seg.set_max_iterations(MAXITER)
        seg.set_distance_threshold(0.05*rmax)
        try:
            indices, model = seg.segment()
        except:
            break
        try:
            if len(indices) > minpoints(model[-1],model[-1],DPU):
                cylinders.append((len(indices), model, indices))  # Accumulate cylinders
                currentcloud = currentcloud.extract(indices, negative=True)
            else:
                break
        except:
            pass
    return cylinders or None

def get_neighbor_cloud(cyl,pointcloud,cube=None):
    if cube is None:
        cs = cyl.r+2*abs(cyl.b-cyl.a)+0.5
    cc = cyl.o+cyl.l*(cyl.b+cyl.a)/2.0
    xbool = (np.array(pointcloud)[:,0]>(cc[0]-cs/2.0))*(np.array(pointcloud)[:,0]<(cc[0]+cs/2.0))
    ybool = (np.array(pointcloud)[:,1]>(cc[1]-cs/2.0))*(np.array(pointcloud)[:,1]<(cc[1]+cs/2.0))
    zbool = (np.array(pointcloud)[:,2]>(cc[2]-cs/2.0))*(np.array(pointcloud)[:,2]<(cc[2]+cs/2.0))
    return pointcloud.copy()[xbool*ybool*zbool]


def filter_cloud(inds, cloud):
    mask = np.ones(len(cloud),dtype=bool)
    mask[inds] = False
    return cloud[mask]

def cyl_putable(ex_cyl,stack,cloud):
    exc = get_cylinder_from_model(ex_cyl[1],cloud[ex_cyl[2]])
    if exc:
        for item in stack:
            if cydistance(exc,item[0])<=exc.r:
                return exc
    return None

def remove_cylinder_points(cyl,cloud,threshold=None):
    if threshold==None:
        thres = cyl.r*0.2
    else:
        thres = threshold
    scals = np.dot(np.array(cloud)-cyl.o,cyl.l)
    trus = (scals>=cyl.a)*(scals<=cyl.b)
    trusr = np.sqrt(np.linalg.norm(cloud-cyl.o,axis=1)**2.0-scals**2.0)<=cyl.r+thres
    return cloud[~(trus*trusr)]


def computepca(array):
    cv = np.cov(array)
    u,s,v = np.linalg.svd(cv)
    return u,s



def filterpoints(cloud,r=R_FILTER_MIN):
    cld = spat.cKDTree(cloud)
    pairs = cld.query_pairs(r)
    npairs = np.array(list(pairs))
    fltrd = np.setdiff1d(np.arange(cld.n),npairs.ravel())
    res = np.setdiff1d(np.arange(cld.n),fltrd,assume_unique=True)
    filteredcloud = cloud[res]
    return filteredcloud


#def form_the_patches(cloud,r=np.linspace(RMIN_PATCH,RMAX_PATCH,5)):
    #'''
    #patches = [(radius, indicies, svdu,svds), ...]
    #indicies = [0,4,9,...<less(len(cloud))]
    #'''
    #cld = spat.cKDTree(cloud)
    #_patches = []

    #for _r in r:
        #cld.query_ball_point()









#Load cloud here
cloud = np.loadtxt('quercus.csv',dtype=np.float32)


print 'Cloud shape is ', cloud.shape


#Common cloud preprocessing
prelim = filter_preliminary(np.array(cloud))
pointcloud = pcl.PointCloud(prelim)
res = find_initial_stem(pointcloud)


c = get_cylinder_from_model(res[1],np.array(pointcloud)[res[2]])


mainstack=[(c,np.array(pointcloud)[res[2]])]
statuses = [False]
# ================ Main loop for cylinder extraction=======================
rmax = c.r
while not all(statuses):
    cur_ind = np.argmax(~np.array(statuses))
    cur_cyl = mainstack[cur_ind][0]
    cloud = remove_cylinder_points(cur_cyl,cloud)
    npc = get_neighbor_cloud(cur_cyl,cloud)
    ccyls = extract_cylinders(pcl.PointCloud(npc),rmax)
    print "len of neighbor cloud", len(npc)
    if ccyls:
        for item in ccyls:
            newcyl = cyl_putable(item, mainstack, npc)
            if newcyl:
                mainstack.append((newcyl,npc[item[2]]))
                statuses.append(False)
                for item in mainstack:
                     vtkex.plotcylinder(item[0])
                vtkex.addpoints(npc)
                vtkex.render(cur_cyl.o)
                cloud = remove_cylinder_points(newcyl,cloud)
    statuses[cur_ind] = True
    print 'Current length', len(cloud), 'Statuses len', len(statuses)
    if len(statuses)>25:
        break
# ==========================================================================

for item in mainstack:
    vtkex.plotcylinder(item[0])
vtkex.addpoints(cloud)
vtkex.render(c.o)



# fig = figure()
# ax = fig.gca(projection='3d')
# #
# ax.plot(gagg[:,0],gagg[:,1],gagg[:,2],'o')
# show()

#cloud = np.loadtxt('quercus.txt',dtype=np.float32)

# Filter all alone points if the distance to the nearest neighbor is greater than R_FILTER_MIN
#cloud = filterpoints(cloud)






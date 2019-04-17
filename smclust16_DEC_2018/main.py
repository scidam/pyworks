import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial import distance as ssd
from scipy.spatial.distance import pdist, cdist



# copied from haversine.py 
import math
def haversine_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d 
 
 
 
def compute_distance_matrix(X, temp_weight=None, coord_weight=None):
    D = pdist(X[:, :2], lambda x, y: haversine_distance(x, y))  
    T = pdist(X, lambda x, y: abs(x[-1] - y[-1])) # pairwise differences by temperature
    if temp_weight is None or coord_weight is None: # if at least one of the weights isn't defined, use coordinates only
        return D
    return temp_weight * T + coord_weight * D
       
    
 
np.random.seed(30) 
 
 
# Create location data
x = np.random.rand(100, 1)
y = np.random.rand(100, 1)
 
t = np.random.randint(0, 20, size=(100,1))

 

X = np.hstack([x, y, t])

# Compare clustering alternatives
distance_matrix = compute_distance_matrix(X, temp_weight=100, coord_weight=5)
Zd = linkage(distance_matrix, method="complete")
 
 
# Cluster based on distance matrix
cld = fcluster(Zd, 10, criterion='distance').reshape(100,1)
plt.figure(figsize=(10, 8))
plt.scatter(x, y, c=cld)  
plt.show()

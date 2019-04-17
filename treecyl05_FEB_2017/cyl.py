import pcl
import numpy as np
cloud = pcl.PointCloud(np.loadtxt('tree.dat',dtype=np.float32))
print(cloud.size)

seg = cloud.make_segmenter_normals(ksearch=50)
seg.set_optimize_coefficients(True)
seg.set_model_type(pcl.SACMODEL_CYLINDER)
seg.set_normal_distance_weight(0.1)
seg.set_method_type(pcl.SAC_RANSAC)
seg.set_max_iterations(10000)
seg.set_distance_threshold(0.1)
seg.set_radius_limits(0, 1)
indices, model = seg.segment()
print(model)
cloud_cylinder = cloud.extract(indices, negative=False)
print len(indices), model


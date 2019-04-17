from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
import waipy


datasets = (['data1.dat', 'SAR', 1800], 
            ['data2.dat', 'BIK', 1864],
            ['data3.dat', 'VUS', 1609])


dt=1
units='mm'
for d, name, t0 in datasets:
    data = np.loadtxt(d)
    N = data.size
    time = np.arange(0, N) * dt + t0
    label='Precipitation data {}'.format(name)
    data_norm = waipy.normalize(data)
    alpha = abs(np.corrcoef(data_norm[0:-1], data_norm[1:])[0,1])
    result = waipy.cwt(data_norm, 1, 1, 0.25, 2, 7/0.25, alpha, 6, mother='Morlet', name=name)
    waipy.wavelet_plot(label, time, data_norm, 1.0e-6, result); 

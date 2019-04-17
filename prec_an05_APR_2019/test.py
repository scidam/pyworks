from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
import waipy


data = np.array(list(range(32)) *30)
N = data.size
t0=0
dt=1
units='mm'
label='Sample data'
time = np.arange(0, N) * dt + t0

data_norm = waipy.normalize(data)
alpha = abs(np.corrcoef(data_norm[0:-1], data_norm[1:])[0,1])
print(alpha)
result = waipy.cwt(data_norm, 1, 1, 0.25, 2, 7/0.25, alpha, 6, mother='Morlet', name='Simple')
waipy.wavelet_plot(label, time, data_norm, 1.0e-6, result);



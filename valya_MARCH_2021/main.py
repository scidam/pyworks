import pandas as pd
import numpy as np
import glob
from sklearn import decomposition
import os
import matplotlib.pyplot as plt
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
pca = LinearDiscriminantAnalysis(n_components=2)


data = dict()
X = []
y = []
for name in glob.glob('*.xlsx'):
    data[os.path.basename(name)] = pd.read_excel(name)
    dataset= data[os.path.basename(name)].iloc[:99,2:5].values
    X.append(dataset)
    y.append([os.path.basename(name)]*len(dataset))


X = np.vstack(X)
y = np.hstack(y)


pca.fit(X,y)
X_r = pca.transform(X)

colors='bgrcmykw'
target_names = np.unique(y)
ran = range(len(target_names))

for color, i, target_name in zip(colors, ran, target_names):
    plt.scatter(X_r[y == target_name, 0], X_r[y == target_name, 1], c=color,  lw=2,
                label=target_name)
plt.legend()
plt.show()


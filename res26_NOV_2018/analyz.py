
from scipy.stats import ttest_ind, mannwhitneyu
import pandas as pd

data = pd.read_csv('out.csv', header=None)

x = data.loc[:,0].astype(float).values
y = data.loc[~pd.isnull(data.loc[:,1]),1].astype(float).values


print("Column # 1 significantly differs from #2 (t-test)")
print(ttest_ind(x,y))

print("Column # 1 significantly differs from #2 (Mann-Whitney test)")
print(mannwhitneyu(x,y))

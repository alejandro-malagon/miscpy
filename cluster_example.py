import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt

# Variable Declaration
num_clusters = 8
val_k = 3
cust_type = 'ORGANIZATION'
factor_name = 'Remote Deposit / Cash'

df = pd.read_csv("REPLACE")

df_data = df[df['CUSTOMER_TYPE'] == cust_type]
df_data = df_data.set_index(['CUSTOMER_NUMBER', 'CUSTOMER_TYPE'])

val_IQR = np.percentile(df_data['FACTOR_CNT'], 75) - np.percentile(df_data['FACTOR_CNT'], 25)
val_lbound = np.percentile(df_data['FACTOR_CNT'], 25) - (1.5 * val_IQR)
val_ubound = np.percentile(df_data['FACTOR_CNT'], 75) + (1.5 * val_IQR)

df_data_no_out = df_data[(df_data['FACTOR_CNT'] >= val_lbound) & (df_data['FACTOR_CNT'] <= val_ubound)]

df_data_no_out.plot(kind = 'box') # Box Plot

df_data_no_out.describe() # Summary Statistics

wcss = []
for i in range(1, num_clusters + 1):
 kmeans = KMeans(n_clusters = i, init = 'k-means++', max_iter = 300, n_init = 10, random_state = 0)
 kmeans.fit(df_data_no_out['FACTOR_CNT'].reshape(-1, 1))
 wcss.append(kmeans.inertia_)
 
plt.plot(range(1, num_clusters + 1), wcss, 'o-')
plt.title(factor_name + ' ' + str.capitalize(cust_type))
plt.xlabel('Number of Clusters K')
plt.ylabel('Total Within-Clusters Sum of Squares')
plt.axvline(3, linestyle = '--', color = 'black')
plt.show()

# K-Means Clustering
kmeans = KMeans(n_clusters = val_k, random_state = 0).fit(df_data_no_out['FACTOR_CNT'].reshape(-1, 1))

# Identify cluster labels
labels = kmeans.labels_
counts = np.bincount(labels[labels >= 0])

# Append cluster and centroid data to the no outlier dataframe
df_data_no_out['CLUSTER'] = list(labels)
df_data_no_out['CENTROID'] = kmeans.cluster_centers_[df_data_no_out['CLUSTER']]

# Identify cluster info
clusters = {}

for i in range(len(counts)):
    clusters[str(round(kmeans.cluster_centers_[i][0], 5))] = counts[i]
    
clusters # Cluster Info

df_data_no_out.groupby('CLUSTER')['FACTOR_CNT'].agg(['min', 'max']) # U-L bounds for clusters

# Join into w/ outlier dataframe
df_data = df_data.join(df_data_no_out[['CLUSTER', 'CENTROID']])

# Identify the largest centroid cluster and auto-assign to outliers
df_data['CLUSTER'][df_data['CLUSTER'].isnull()] = df_data['CLUSTER'][df_data['CENTROID'] == df_data['CENTROID'].max()].min()

df_data = df_data.reset_index()
df_data.to_csv('REPLACE', index = False)
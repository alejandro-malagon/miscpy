# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 16:23:18 2018

@author: alemal03
"""

import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

# Initial Data Set Read
df = pd.read_csv("REPLACE")

# Variable Declaration
args = [
        ['INDIVIDUAL', 'LOW', 'clusters_ind_low.csv'],
        ['INDIVIDUAL', 'MEDIUM', 'clusters_ind_med.csv'],
        ['INDIVIDUAL', 'HIGH', 'clusters_ind_high.csv'],
        ['ORGANIZATION', 'LOW', 'clusters_org_low.csv'],
        ['ORGANIZATION', 'MEDIUM', 'clusters_org_med.csv'],
        ['ORGANIZATION', 'HIGH', 'clusters_org_high.csv']
       ]

# Number of clusters to fit
val_k = 3

# Initialize Loop
for i in range(0, len(args)):
    # Variable Declaration
    cust_type, risk_lvl, output_name = args[i][0], args[i][1], args[i][2]
    
    # Data Slicing by Customer Type and Risk Level
    df_data = df[(df['CUST_TYPE'] == cust_type) & (df['RISK_LVL'] == str.capitalize(risk_lvl))]

    # Set index for joining purposes at the end of code
    df_data = df_data.set_index(['CUST_NUM', 'CUST_TYPE', 'RISK_LVL'])

    # Outlier identification
    val_IQR = np.percentile(df_data['MONTH_AVG'], 75) - np.percentile(df_data['MONTH_AVG'], 25)
    val_lbound = np.percentile(df_data['MONTH_AVG'], 25) - (1.5 * val_IQR)
    val_ubound = np.percentile(df_data['MONTH_AVG'], 75) + (1.5 * val_IQR)
    
    # Create dataset without outliers
    df_data_no_out = df_data[(df_data['MONTH_AVG'] >= val_lbound) & (df_data['MONTH_AVG'] <= val_ubound)]

    # K-Means Clustering
    kmeans = KMeans(n_clusters = val_k, random_state = 0).fit(df_data_no_out['MONTH_AVG'].reshape(-1, 1))

    # Identify cluster labels
    labels = kmeans.labels_
    counts = np.bincount(labels[labels >= 0])

    # Print break line for readability
    print('-----' + cust_type + ' - ' + risk_lvl + '-----')

    # Identify cluster info
    clusters = {}

    for j in range(len(counts)):
        clusters[str(round(kmeans.cluster_centers_[j][0], 5))] = counts[j]
    
    print(clusters)

    # Append cluster and centroid data to the no outlier dataframe
    df_data_no_out['CLUSTER'] = list(labels)
    df_data_no_out['CENTROID'] = kmeans.cluster_centers_[df_data_no_out['CLUSTER']]

    # Lower and upper bounds for clusters
    print(df_data_no_out.groupby('CLUSTER')['MONTH_AVG'].agg(['min', 'max'])) 

    # Join cluster assignment information into original dataframe
    df_data = df_data.join(df_data_no_out[['CLUSTER', 'CENTROID']])

    # Identify the largest centroid cluster and auto-assign to outliers
    df_data['CLUSTER'][df_data['CLUSTER'].isnull()] = df_data['CLUSTER'][df_data['CENTROID'] == df_data['CENTROID'].max()].min()

    # Remove index to ensure proper alignment of output file
    df_data = df_data.reset_index()
    
    # Output the dataframe to a .csv file
    df_data.to_csv('REPLACE' + output_name, index = False)
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics.pairwise import cosine_similarity

def get_unvisted_item(data_df, u_id):
    visited_items = set(data_df[data_df.u_id == u_id]['p_id'].tolist())
    unvisited_items = [item for item in data_df.p_id.unique() if item not in visited_items]
    return unvisited_items

def get_items(data_df, u_id):
    visited_items = set(data_df[data_df.u_id == u_id]['p_id'].tolist())
    unvisited_items = [item for item in data_df.p_id.unique() if item not in visited_items]
    return unvisited_items, visited_items

def culc_sim():
    item_Table = pd.read_csv('../data/kmeans_item_Table.csv')
    item_Matrix = item_Table.groupby('p_id').mean()
    item_Matrix = item_Matrix.to_numpy()
    sim = cosine_similarity(item_Matrix, item_Matrix)
    return sim

# csv파일 불러오는 함수 but... 실제 platform애서는 DB의 데이터 불러오겠금 수정 필요
def load_data():
    table_df = pd.read_csv('../data/ulsan_rest_table_ver3.csv')
    print(table_df.isnull().sum())
    table_df.drop(columns='comment', inplace=True)
    table_df.dropna(axis=0, how='any', inplace=True)
    data_df = table_df[['u_id', 'p_id', 'score']]
    return data_df

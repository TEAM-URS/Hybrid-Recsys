import numpy as np
import pandas as pd
import tensorflow as tf
from util import get_unvisted_item, get_items

def recom_cf(model, u_id, data_df, top_n):

    p_id_list = get_unvisted_item(data_df, u_id)
    pred_df = pd.DataFrame(columns=['u_id', 'p_id', 'score'])
            
    for p_id in p_id_list:
        pred = model.predict([np.array([u_id]), np.array([p_id])])
        new_data = pd.DataFrame({'u_id': [u_id], 'p_id': [p_id], 'score': [float(pred)]})
        pred_df = pd.concat([pred_df, new_data], axis=0, names=['u_id', 'p_id', 'score'], ignore_index=True)
    
    recom_df = pred_df.sort_values(by=['score'], ascending=False)[:top_n]

    return recom_df


def recom_cbf(p_id, sim):
    sim_scores = list(enumerate(sim[p_id]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:4]

    return sim_scores


def recom_hybrid(model, u_id, data_df, top_n, sim):
    unvisited_items, visited_items = get_items(data_df, u_id)
    visited_items = set(data_df[data_df.u_id == u_id]['p_id'].tolist())
    pred_df = pd.DataFrame(columns=['u_id', 'p_id', 'score'])
    
    recom_cbf_pids = []
    for cbf_p_id in visited_items:
        for item in recom_cbf(cbf_p_id, sim): #컨텐츠기반필터링
            recom_cbf_pids.append(item[0])
    recom_cbf_pids = set(recom_cbf_pids)
    
    for p_id in unvisited_items:
        pred = model.predict([np.array([u_id]), np.array([p_id])]) #협업필터링
        if p_id in recom_cbf_pids: #컨텐츠기반필터링 추천 목록에 포함된다면..
            pred = pred + pred*0.05     # 가중치 연산
        new_data = pd.DataFrame({'u_id': [u_id], 'p_id': [p_id], 'score': [float(pred)]})
        pred_df = pd.concat([pred_df, new_data], axis=0, names=['u_id', 'p_id', 'rating'], ignore_index=True)
    
    recom_df = pred_df.sort_values(by=['score'], ascending=False)[:top_n]    
    return recom_df
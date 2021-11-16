#=== generate labels for the structural probe proposed in 
# Hewitt, J., & Manning, C. D. (2019, June). A structural probe for finding syntax in word representations. 
# In Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, 
# Volume 1 (Long and Short Papers) (pp. 4129-4138).
# 1) pair-wise distance between words; 2) depth of each word (distance between the word and the syntactic root) in the dependency tree
#=== 
# this script generates pair-wise distance matrixs (symmetry matrixs,just because ease of use) and list of word "syntactic" depth
# from parse results of stanza (i.e. output files of to_tokens.py) 

import os
import re
from argparse import ArgumentParser
from collections import defaultdict
import numpy as np
import pandas as pd
import pickle
from tqdm import tqdm
from utils.constant import punct_upos_tags, punct_xpos_tags


def get_pair_wise_words(i1,i2,graph):
    if i1 == i2:
        return 0
    
    assert i1 in graph and i2 in graph, "NOT valid word index in the original sentence."
    
    visited = [i1]
    dist = 1
    to_visit = graph[i1]
    #print(i1,i2)
    #print(to_visit)
    
    while len(to_visit) > 0:
        #print(to_visit)
        tmp_to_visit = set()
        for i in to_visit:
            #print(i, i2)
            if i == i2:
                return dist
            for ii in graph[i]:
                if ii not in visited:
                    tmp_to_visit.add(ii)
        visited += to_visit
        #print(tmp_to_visit)
        to_visit = list(tmp_to_visit)
        dist += 1
    return -1

def build_dist_matrix(graph,ix2id,length):
    mat = [[0] * length for _ in range(length)]
    for i in range(length):
        for j in range(i+1,length):
            tmp = get_pair_wise_words(ix2id[i],ix2id[j],graph)
            assert tmp != -1, f"ERROR: no distance calculated for {(ix2id[i],ix2id[j])} (original word index)."
            mat[i][j] = mat[j][i] = tmp
    return mat

def build_depth_lst(graph,ix2id,length,root_id):
    # attribute the current depth for each word on the current level during BFS
    res = {root_id:0}
    visited = [root_id]
    dist = 1
    to_visit = graph[root_id]
    
    while len(to_visit) > 0:
        tmp_to_visit = set()
        for i in to_visit:
            res[i] = dist
            for ii in graph[i]:
                if ii not in visited:
                    tmp_to_visit.add(ii)
        visited += to_visit
        to_visit = list(tmp_to_visit)
        dist += 1
    return [res[ix2id[i]] for i in range(length)]

def build_mask_no_punct(pos):
    mask = []
    for p1, p2 in pos:
        if p1 == "ENTITY_MARKER":
            continue
        if p1 not in punct_upos_tags and p2 not in punct_xpos_tags:
            mask.append(1)
        else:
            mask.append(0)
    return mask

def build_targets(pos,deps):
    # given the dependency parse of a sentence, return the distance matrix and the sequence of word depths
    graph = defaultdict(list)
    for i,h,_ in deps:
        if h == 0:
            root = i
            continue
        graph[i].append(h)
        graph[h].append(i)
    ix2id = {i:ix for i, ix in enumerate(sorted(graph.keys()))}
    L = len(ix2id)

    mat = build_dist_matrix(graph,ix2id,L)
    depths = build_depth_lst(graph,ix2id,L,root)
    mask = build_mask_no_punct(pos)
    assert len(mat) == len(depths) == len(mask) == L, "length of distance of matrix | depth | mask sequence not equal to the number of syntactic tokens."

    return mat, depths, mask, sorted(graph.keys())

def build_labels(args,ty):
    data = pickle.load(open(os.path.join(args.data_dir,f"{ty}.pkl"),"rb"))
    dist_mats = []
    depths = []
    masks = []
    keys = []

    for d in tqdm(data,desc=ty):
        tmp_dist_mat, tmp_depths, tmp_mask, tmp_keys = build_targets(d["pos"],d["dependencies"])
        dist_mats.append(tmp_dist_mat)
        depths.append(tmp_depths)
        masks.append(tmp_mask)
        keys.append(tmp_keys)

    assert len(dist_mats) == len(depths) == len(masks) == len(keys) == len(data), f"{ty}: length of outputs on train not equal to original files."
    with open(os.path.join(args.output_dir,f"syntactic_probe_labels_{ty}.pkl"),"wb") as f:
        pickle.dump({"distance_matrix":dist_mats,"depths":depths,"mask":masks,"keys":keys},f,pickle.HIGHEST_PROTOCOL)

#========== as this is the final step of data preprocessing, we do a final check here. ==========
#========== we assume that all generated files (results of to_tokens.py, to_wps.py and this script) are saved under the same directory 
# HOW TO obtain tokens from wordpieces and remove entity markers?
# there are three files: token_level data (T), wp_level_data (W), syntactic_label_data (S)
# 1) use map (W["map"]) and wordpieces (W["wps"]) to restore token sequence  --> wordpieces TO tokens
# 2) select by indexing the token sequence obtained in 1) using the key (S["keys"])  --> REMOVE entity markers and [CLS], [SEP]
# 3) "disable" those punctuation tokens by applying masks (S["masks"]) --> MASK punctuations

def main(args):
    build_labels(args,"train")
    build_labels(args,"dev")
    build_labels(args,"test")

if __name__ == "__main__":
    parser = ArgumentParser(description="generate targets (labels) for the structural probe designed for BERT.")

    parser.add_argument("--data_dir", default=None, type=str, required=True,
                         help="path to token-level data files (results of to_tokens.py)")
    parser.add_argument("--output_dir", default=None, type=str, 
                         help="path to save the outputs.")

    args = parser.parse_args()
    main(args)
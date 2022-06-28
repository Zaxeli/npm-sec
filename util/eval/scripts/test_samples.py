import sys
import os

from py import process
os.chdir(os.getcwd()+"/../../../")
sys.path.append(os.getcwd())
import json
import numpy as np
import pandas as pd
from multiprocessing import Pool 
from typo_eval_framework import Typo_Framework as Typo_FW
from evaluator import Evaluator

"""
Purpose of script:
    Get a sample of mainline pkgs and one of their random typo

"""

"""populariteis dataframe"""
path_res = 'util/eval/results/'
pop_filename = "popularities.csv"
ill_filename = 'illegit_typo.csv'
top1000_f = "util/top_1000"
storage_path = "util/eval/results/"

# pop = pd.read_csv(path_res+pop_filename)
# ill = pd.read_csv(path_res+ill_filename)
# pop_np = pop.to_numpy()
# ill_np = ill.to_numpy()

# with open(path_res+"popularities.json") as f:
#     pop_json = json.load(f)

# ill_join = list(zip(ill_np, pop_json))

""" Get top1000 pkgs """
def ff(x): return x[:-1]
with open(top1000_f) as f:
    lines = f.readlines()
    with Pool(processes=12) as pool:
        top1000 = pool.map(ff, lines)


""" Get the list of manually confirmed typos """
# def f_(row):
#     pkg = row[0][0]

#     try:
#         n = 1+int(row[0][1])
#         typo = row[1][n][0]
#     except: return

#     return [pkg,typo]

# with Pool(processes=12) as pool:
#     typos_cnf = pool.map(f_, ill_join)

# # Typos_cnf is a list of tuples of the form [(main pkg, confirmed typo pkg),..]
# typos_cnf = list(filter(lambda x: x!=None, typos_cnf))

""" Get rank 100-200 pkgs after the top100 """
second_top_100 = top1000[100:200]    # Get the next 100, then filter out problematic to get ~63

""" Get mainline pkg and a random typo pkg for each sample """
def f_(p):
    ty_fw = Typo_FW(p)
    t = list(ty_fw.get_pkgs_names())
    # print(t)
    t.remove(p)

    try:
        r = np.random.randint(len(t))
        typo = t[r]
    except:
        return (p,)
    
    return (p,typo)

# print(test_pkgs[0])
# print(f_(test_pkgs[0]))

with Pool(processes=12) as pool:
    test_pkgs = pool.map(f_, second_top_100)


test_pkgs = list(filter(lambda x: len(x)==2 and '@' not in x[0], test_pkgs))    # has at lesat one typo and id not an '@' pkg
test_pkgs = np.array(test_pkgs)
# testing these pkgs: 
# test_pkgs = np.array(
#  [['co','oco'],
#  ['nan', 'an'],
#  ['promise', 'promisie'],
#  ['postcss', 'potscss'],
#  ['morgan', 'organ'],
#  ['less', 'ess'],
#  ['immutable', 'iammutable'],
#  ['qs', 'q'],
#  ['fs', 'fss'],
#  ['marked', 'rmarked'],
#  ['mime', 'mie'],
#  ['meow', 'mew'],
#  ['styled-components', 'style-components']])

np.save(storage_path+"test_pkgs.npy", test_pkgs)    # save to file for ease of access
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
    Use Evaluator object to get the analysis results and tallies of the typos around each of the 100-200 packages

Approach:
    First, try to hard code 'lodash' as the target pkg. Then get list of typos around it.
    Then use Evaluator to evaluate those typo packages.

    The returned value should be the results & tallies for each of those typo pkgs.

    Now that I have the testing samples, rrun the evaluator on all of them. 
    Benign first, then malign next.

"""

"""populariteis dataframe"""
top1000_f = "util/top_1000"
storage_path = "util/eval/results/"

test_pkgs = np.load(storage_path+"test_pkgs.npy")

print("testing these pkgs: \n",test_pkgs)

""" Now perform evaluation """

"on benign"
ev = Evaluator(pkg_list=list(test_pkgs[:,0]), file_source=False)
ev.perform_evaluation()
ev.store_evaluation(do_json_store=False, do_pandas_tallies=False)
ben_res = ev.get_results()
ben_tal = ev.get_tallies()

"on malign"
ev = Evaluator(pkg_list=list(test_pkgs[:,1]), file_source=False)
ev.perform_evaluation()
ev.store_evaluation(do_json_store=False, do_pandas_tallies=False)
mal_res = ev.get_results()
mal_tal = ev.get_tallies()


""" Store results to disk for persistence """
tals = {
    "ben_tal": ben_tal,
    "mal_tal": mal_tal
}

ress = {
    "ben_res": ben_res,
    "mal_res": mal_res
}

with open(storage_path+"test_tallies.json", "w+") as f:
    json.dump(tals,f)
with open(storage_path+"test_results.json", "w+") as f:
    json.dump(ress,f)

ev.get_testnames()
exit()



PKG_NAME = 'lodash'
ty = Typo_FW(PKG_NAME)

typos = list(ty.get_pkgs_names())

print(typos)

typo1 = [typos[0]]

# typo1 = 'loadash'

ev = Evaluator(pkg_list=typo1, file_source=False)
ev.perform_evaluation()
anly_tests, typo_test = ev.get_testnames()
ev.store_evaluation(do_json_store=False, do_pandas_tallies=False)

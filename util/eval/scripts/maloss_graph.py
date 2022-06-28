import sys
import os
os.chdir(os.getcwd()+"/../../../")
sys.path.append(os.getcwd())
import matplotlib.pyplot as plt
import numpy as np
import json

storage_path = "util/eval/results/"

"""
Purpose of script:
    To graph the results from maloss evaluation for easier analysis and interpretation of results

"""

""" Fetch data """
with open(storage_path+"maloss_eval_res.json") as f:
    res = json.load(f)
with open(storage_path+"maloss_eval_tal.json") as f:
    tal = json.load(f)

# hardcode for now
testnames = [['author_changes', 'dist_tag_latest', 'first_version', 'immature_package', 'maintainer_changes', 'malicious_authors_involved',
              'malicious_maintainers_involved', 'package_popularity', 'strictly_inc_versions', 'version_skipping'], ['age_comparison', 'popularity_comparison', 'same_author']]


""" Collate columns and data """


"""
---- Discontinued: Now incorporating the graphing with the typo samples graphs ----
"""
x_axis=[]
bars
for testnum in range(len(testnames)):
    mal_col=[]
    ben_col=[]
    for i in range(len(testnames[testnum])):
        mal_col.append([row[testnum+1][1][i] for row in mal_tal])
        ben_col.append([row[testnum+1][1][i] for row in ben_tal])

    # number of tests using any of the columns
    m_tests = len(mal_col[0])
    b_tests = len(ben_col[0])

    # internal, bars for the tests of current category
    m_bars_=[]
    b_bars_=[]
    for i in range(len(testnames[testnum])):  # for each testname in the category (typo)
        m = sum(mal_col[i])/m_tests
        m_bars_.append(m)

        b = sum(ben_col[i])/b_tests
        b_bars_.append(b)

    # bars for each category, append
    m_bars.append(m_bars_)
    b_bars.append(b_bars_)

    names = testnames[testnum]
    x_axis.append(np.arange(len(names)))


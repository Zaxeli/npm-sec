from stringprep import b3_exceptions
import matplotlib.pyplot as plt
import numpy as np
import json
import sys
import os
os.chdir(os.getcwd()+"/../../../")
sys.path.append(os.getcwd())
"""
Purpose of script:
    Get the results of the eval and graph them as histogram so that it is easier to analyse and make conclusions.

    The graphs and analysis is for the results from evaluation on 
    rank 100-200 pkgs for 
    benign = main pkg, and 
    malign = random typo of main pkg

    Optionally, it also allows for plotting the tally results for maloss evaluation.
    Set the `plot_maloss` to True for this.

"""
# plot_maloss = False
plot_maloss = True

top1000_f = "util/top_1000"
storage_path = "util/eval/results/"
path_figures = "util/eval/figures/"


""" Retrieve the data """
with open(storage_path+"test_tallies.json") as f:
    tals = json.load(f)
    ben_tal = tals['ben_tal']
    mal_tal = tals['mal_tal']

with open(storage_path+"test_results.json") as f:
    ress = json.load(f)
    # ben_res = ress['ben_res']
    # mal_res = ress['mal_res']

# Maloss samples
with open(storage_path+"maloss_eval_res.json") as f:
    maloss_res = json.load(f)
with open(storage_path+"maloss_eval_tal.json") as f:
    maloss_tal = json.load(f)

# hardcode testnames and order for now
testnames = [['author_changes', 'dist_tag_latest', 'first_version', 'immature_package', 'maintainer_changes', 'malicious_authors_involved',
              'malicious_maintainers_involved', 'package_popularity', 'strictly_inc_versions', 'version_skipping'], ['age_comparison', 'popularity_comparison', 'same_author']]

print(testnames)

""" Collate the data for the columns for anly and typo eval` """
"""
mal (or 'm'): refers to the randomly chosen typo which are being assumed malicious (in the typo sense at least)
ben (or 'b'): refers to the benign packages taken from and filtered from the top1000 list with ranks 100-200
maloss (or 'mls'): refers to the maloss samples which were evaluated separately. These are known to be malicious (per Duian et al)    
"""
# number of tests using any of the columns
m_tests = len(mal_tal)
b_tests = len(ben_tal)
mls_tests = len(maloss_tal)
print("samples: ", m_tests, b_tests, mls_tests)

x_axis=[]
m_bars = []
b_bars = []
mls_bars=[]
for testnum in range(len(testnames)):
    mal_col=[]
    ben_col=[]
    maloss_col=[]
    for i in range(len(testnames[testnum])):
        mal_col.append([row[testnum+1][1][i] for row in mal_tal])
        ben_col.append([row[testnum+1][1][i] for row in ben_tal])
        maloss_col.append([row[testnum+1][1][i] for row in maloss_tal])

    # internal, bars for the tests of current category
    m_bars_=[]
    b_bars_=[]
    mls_bars_=[]
    for i in range(len(testnames[testnum])):  # for each testname in the category (typo)
        m = sum(mal_col[i])/m_tests
        m_bars_.append(m)

        b = sum(ben_col[i])/b_tests
        b_bars_.append(b)

        mls = sum(maloss_col[i])/mls_tests
        mls_bars_.append(mls)

    # bars for each category, append
    m_bars.append(m_bars_)
    b_bars.append(b_bars_)
    mls_bars.append(mls_bars_)

    names = testnames[testnum]
    x_axis.append(np.arange(len(names)))


""" Plot the graphs for benign samples and malicious (assumed typo) samples """

# Changes to graph layout depending on 3 or 2 bargraphs
w=0.4
x_adj = [-0.2,+0.2]
if plot_maloss: w=0.2; x_adj=[-0.2,0,0.2]

plt.figure(1)

plt.subplot(2,1,1)
n=0
plt.bar(x_axis[n]+x_adj[0], np.array(m_bars[n])*100, width=w, align='center', label="typo")
plt.bar(x_axis[n]+x_adj[1], np.array(b_bars[n])*100, width=w, align='center', label="ben")
if plot_maloss: plt.bar(x_axis[n]+x_adj[2], np.array(mls_bars[n])*100, width=w, align='center', label="maloss")

plt.xticks(x_axis[n], testnames[n], rotation=30, ha="right")
plt.xlabel("tests")
plt.ylabel("% positives")
plt.title("Anly tests")
plt.legend()


plt.subplot(2,1,2)

n=1
plt.bar(x_axis[n]+x_adj[0], np.array(m_bars[n])*100, width=w, align='center', label="typo")
plt.bar(x_axis[n]+x_adj[1], np.array(b_bars[n])*100, width=w, align='center', label="ben")
if plot_maloss: plt.bar(x_axis[n]+x_adj[2], np.array(mls_bars[n])*100, width=w, align='center', label="maloss")

plt.xticks(x_axis[n], testnames[n])
plt.xlabel("tests")
plt.ylabel("% positives")
plt.title("Typo tests")
plt.legend()



plt.tight_layout()
name = "graph_analysis.png" if not plot_maloss else "graph_analysis_mls.png"
# plt.savefig(path_figures+name)
plt.show()




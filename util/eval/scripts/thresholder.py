import ast
import numpy as np
import pandas as pd
import json
import sys
import os
import matplotlib.pyplot as plt
from multiprocessing import Pool
from this import d
os.chdir(os.getcwd()+"/../../../")
sys.path.append(os.getcwd())
"""
Purpose of script:
To get 2 thresholds
- From stritly the second pkg in typo list
- From illegi typo in typo list

typo list @ popularities(.csv/.json)
illegit list @ illegit_typo(.csv/.json)
"""


"""filenames"""
path_res = 'util/eval/results/'
path_figs = 'util/eval/figures/'
pop_filename = "popularities.csv"
ill_filename = 'illegit_typo.csv'

pop = pd.read_csv(path_res+pop_filename)
ill = pd.read_csv(path_res+ill_filename)
pop_np = pop.to_numpy()
ill_np = ill.to_numpy()

with open(path_res+"popularities.json") as f:
    pop_json = json.load(f)



"""
Now, calculate the difference with second
"""

# pop_json

"""
Get the pop 1
Try to get pop 2 (or n)
if exist:
    return diff, %diff
else:
    ret
"""
n=2 # 1st typo (2nd in the list of pkgs in radius, where 1st is the main pkg) 
def f_diff(pop_row:list, perc=False, ):
    pop1 = pop_row[1][1] # pop 1
    try:
        pop2 = pop_row[n][1]
        if pop2==pop1: return
    except: return
    
    if perc: return pop2/pop1
    return pop1-pop2

"""Percentage variant"""
def f_perc(pop_row): 
    return f_diff(pop_row, perc=True)

def f_down(pop_row):
    try:
        pop2 = pop_row[n][1]
        return pop2
    except: return

with Pool(processes=12) as pool:
    pop_diff = pool.map(f_diff, pop_json)
    pop_perc = pool.map(f_perc, pop_json)
    down_2 = pool.map(f_down, pop_json)


# i = pop_perc.index(0.0)
# print(pop_json[i])
# print(pop_diff[i],pop_perc[i])
""" 53: ['yosay', ['yosay', 211710, False], ['yosa', 0, False]]"""


# filter out None values
pop_diff = list(filter(lambda x: x!=None, pop_diff))
pop_perc = list(filter(lambda x: x!=None, pop_perc))
down_2 = list(filter(lambda x: x!=None, down_2))


pop_diff_stats = {
    "min": np.min(pop_diff),
    "max": np.max(pop_diff),
    "mean": np.mean(pop_diff),
    "std": np.std(pop_diff),
}
"""{'min': 211710, 'max': 189163553, 'mean': 28336419.77631579, 'std': 39302360.290754095}"""

pop_perc_stats = {
    "min": np.min(pop_perc),
    "max": np.max(pop_perc),
    "mean": np.mean(pop_perc),
    "std": np.std(pop_perc),
}
"""{'min': 0.0, 'max': 76.43655751341353, 'mean': 2.5698870761707955, 'std': 12.491426440500634}"""



"""
--------
Now get stats for the n-th typo pkg using the illegit typo list
--------
"""

ill_join = list(zip(ill_np, pop_json))

def f_(join_row, perc=False):
    # print(join_row)
    ill = join_row[0]
    pop = join_row[1]

    pop1 = pop[1][1]

    try:
        n = int(ill[1]) + 1
        popn = pop[n][1]
        if pop1==popn: return   # same package, different name
    except: return

    # print(pop1, popn, n, pop1-popn, pop)
    # raise Exception

    if perc: return popn/pop1
    return pop1-popn

def f_perc(join_row):
    return f_(join_row, perc=True)

def f_down(join_row:list):
    ill = join_row[0]
    pop = join_row[1]

    try:
        n = int(ill[1]) + 1
        popn = pop[n][1]
        return popn
    except: return


with Pool(processes=1) as pool:
    popN_diff = pool.map(f_, ill_join)
    popN_perc = pool.map(f_perc, ill_join)
    down_n = pool.map(f_down, ill_join)


# filter out None values
popN_diff = list(filter(lambda x: x!=None, popN_diff))
popN_perc = list(filter(lambda x: x!=None, popN_perc))
down_n = list(filter(lambda x: x!=None, down_n))


popN_diff_stats = {
    "max": np.max(popN_diff),
    "min": np.min(popN_diff),
    "mean": np.mean(popN_diff),
    "std": np.std(popN_diff),
}
"""{'max': 189163553, 'min': 211710, 'mean': 28336419.77631579, 'std': 39302360.290754095}"""


popN_perc_stats = {
    "max": np.max(popN_perc),
    "min": np.min(popN_perc),
    "mean": np.mean(popN_perc),
    "std": np.std(popN_perc),
}
"""{'max': 0.7643655751341354, 'min': 0.0, 'mean': 0.02569887076170796, 'std': 0.12491426440500634}"""



print("popN_diff_stats", popN_diff_stats)
print("popN_perc_stats", popN_perc_stats)




"""
---------
Plot graphs for the stats
---------
"""


"""
Sort then Truncate the outiers 
get better granualrity for the ~73 or 65 and plt them 
"""

"""----- popN_perc plot ------"""
plt.figure(1)
plt.subplot(2,2,1)
x=popN_perc.copy()
x.sort()
# x = x[:71]
vals,bins = np.histogram(x, bins=100)
cdf_vals=np.cumsum(vals)
cdf_vals=np.insert(cdf_vals,0,0)    # so that the line starts at (0,0)
# cdf_vals = cdf_vals*100 # to scale it to proper %

plt.plot(bins[:]*100,cdf_vals)  # scale the percentage by multiply with 100
# plt.hist(x,bins=100, cumulative=True)
plt.title("(a) pop% (n-th typo)")
plt.axvline(x=0.02, color="red", ls="--")   # x=0.02% (= 0.0002) because of scaling the np.array by 100
plt.xlabel("typo's downloads (in %)")
plt.ylabel("Number of pkgs")
"""Knee-point at (x,y) = (~0.2%,70) for both popN and pop distributins"""

"""----- pop_perc plot ------"""
plt.subplot(2,2,2)
x=pop_perc.copy()
x.sort()
# x = x[:71]
vals,bins = np.histogram(x, bins=100)
cdf_vals=np.cumsum(vals)
cdf_vals=np.insert(cdf_vals,0,0)    # so that the line starts at (0,0)

plt.plot(bins[:]*100,cdf_vals)  # scale the percentage by multiply with 100
plt.title("(b) pop% (2nd typo)")
plt.xlabel("typo's downloads (in %)")
plt.ylabel("Number of pkgs")
"""Knee-point at (x,y) = (~0.2%,70) for both popN and pop distributins"""


"""----- down_n cumulative histogram plot ------"""
plt.subplot(2,2,3)
vals,bins = np.histogram(down_n, bins=100)
cdf_vals=np.cumsum(vals)
cdf_vals=np.insert(cdf_vals,0,0)    # so that the line starts at (0,0)

plt.plot(bins[:],cdf_vals)
plt.title("(c) downloads (n-th)")
# plt.xticks([5000,10000,20000,30000,40000])
plt.axvline(x=5000, color="red", ls='--')
plt.xlabel("typo's downloads (per week)")
plt.ylabel("Number of pkgs")
"""Knee point seems to be at 5000 downloads for nth typo"""



"""----- down_2 cumulative histogram plot ------"""
plt.subplot(2,2,4)
vals,bins = np.histogram(down_2, bins=100)
cdf_vals=np.cumsum(vals)
cdf_vals=np.insert(cdf_vals,0,0)    # so that the line starts at (0,0)

plt.plot(bins[:],cdf_vals)
plt.title("(d) downloads (2nd)")
plt.xlabel("typo's downloads (per week)")
plt.ylabel("Number of pkgs")
"""Knee point seemingly at 5.9e+6 downloads for 2nd typo"""



"""
pop diff plots aren't that useful
and are confusing to read
"""
# """----- popN_diff plot ------"""
# plt.subplot(2,2,3)
# x=popN_diff.copy()
# x.sort()
# # x = x[:71]
# vals,bins = np.histogram(x, bins=100)
# cdf_vals=np.cumsum(vals)
# cdf_vals=np.insert(cdf_vals,0,0)    # so that the line starts at (0,0)

# plt.plot(bins[:],cdf_vals, label="n: manual reviewed")
# plt.title("pop diff (nth typo)")
# plt.xlabel("pop1-popN")
# plt.ylabel("Number of pkgs")
# """Knee-point at (x,y) = (~0.2%,70) for both popN and pop distributins"""

# """----- pop_diff plot ------"""
# plt.subplot(2,2,3)
# x=pop_diff.copy()
# x.sort()
# # x = x[:71]
# vals,bins = np.histogram(x, bins=100)
# cdf_vals=np.cumsum(vals)
# cdf_vals=np.insert(cdf_vals,0,0)    # so that the line starts at (0,0)

# plt.plot(bins[:],cdf_vals, label="n: 2nd typo")
# plt.title("pop diff (nth typo)")
# plt.xlabel("pop1-popN")
# plt.ylabel("Number of pkgs")

# plt.legend()
# """Knee-point at (x,y) = (~0.2%,70) for both popN and pop distributins"""


plt.tight_layout()
plt.savefig(path_figs+"thresholder.png")
plt.show()









# plt.subplot(2,2,2)
# plt.plot(pop_perc)


# plt.subplot(2,2,3)
# plt.plot(popN_diff)


# plt.subplot(2,2,4)
# plt.plot(popN_perc)




# print(np.isnan(pop_np[1,20]))

# for i in range(len(pop_np)):
#     for j in range(i-1):
#         if np.isnan(pop_np[i,j]):
#             pop_np[i,j] = None
#         try:
#             pop_np[i,j] = ast.literal_eval(pop_np[i,j])
#         except: pass
# pop_np.shape


# np.dele
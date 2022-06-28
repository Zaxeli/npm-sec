import sys
import os
os.chdir(os.getcwd()+"/../../../")
sys.path.append(os.getcwd())

import json
import pandas as pd
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import util.fetch_metadata as fetch_metadata
import util.pkg_metadata_util as parse_util
from typo_eval_framework import Typo_Framework as Typo_FW 


results_dir = "util/eval/results/"

def get_top1k(trunc=1000):
    top1000_f = os.getcwd()+"/util/top_1000"

    with open(top1000_f) as f:
        top1000 = f.readlines()

    top1000 = [i[:-1] for i in top1000]

    return top1000[:trunc]


def get_download_num(pkg):
    num = fetch_metadata.fetch_downloads_num(pkg)
    p = parse_util.check_security_holding(pkg)
    return (pkg, num, p)

def get_radius_downloads(pkg):

    radius = Typo_FW(pkg, allow_sec_holds=True)
    radius_pkgs = radius.get_pkgs_names()
    
    with ThreadPool(processes=5) as threadpool:
        radius_downloads = threadpool.map(get_download_num, radius_pkgs)


    radius_downloads.sort(key= lambda x: x[1], reverse=True)

    # add the name in first column
    radius_downloads.insert(0,pkg)

    return radius_downloads


top_n = get_top1k(trunc=100) # top n packages


""" Get the numbers, and sort them """
with Pool(processes=12) as pool:
    typos_pop = pool.map(get_radius_downloads,top_n)


""" Save the results """
filename = "popularities"
with open(results_dir+filename+".json", 'w+') as f:
    json.dump(typos_pop, f)

df = pd.DataFrame(typos_pop)
df.to_csv(results_dir+filename+".csv", index=False)

# for i in typos_pop:
#     # print(i)
#     if i[1] and i[0] != i[1][0]:
#         print(i)


""" Prepare csv for list of first illegit pkg acc to download nums """
# don't need to overwrite,
# manually fill the second column in
if False:
    df_illegit = df[df.columns[0:1]]
    df_illegit.to_csv(results_dir+'illegit_typo_.csv')


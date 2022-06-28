import sys
import os
from this import d
os.chdir(os.getcwd()+"/../../../")
sys.path.append(os.getcwd())
"""
The illegit_typo.csv file has manually filled in second column with the index of the first typo package that is illegitimate.

Indexing:
-None: 
    no illegitimate typo package
    could be because there are no typo packages at all
    or that all typos are legitimate
-int:
    - 0: the first pkg, usually the original pkg
    - 1: the first typo, i.e., second in the list
    - so on

"""


"""
what seems like it would have a fair amount of traffic
from typos instead of intended download
"""

"""
Calculates 2 thresholds

First:
Strictly using the difference between 1st and 2nd typo packages

Second:
Using the manually filled in typo numbers in illegit_typo.csv

"""

import pandas as pd
import numpy as np

results_dir = "util/eval/results/"
filename = "illegit_typo.csv"
# filename = "popularities.csv"

df_illegit = pd.read_csv(results_dir+filename,)

# df_illegit.columns
# print(df_illegit)


"""To remove index cilumn if added"""
# df = df_illegit[df_illegit.columns[1:]]
# df.to_csv(results_dir+filename, index=False)

for i, row in df_illegit.iterrows():
    print(i, row[0], row[1])#index,name,typo @

# as numpy array for easy access
ar = df_illegit.to_numpy()
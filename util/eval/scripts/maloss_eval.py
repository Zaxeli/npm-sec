import sys
import os
os.chdir(os.getcwd()+"/../../../")
sys.path.append(os.getcwd())
import json
import util.fetch_metadata as metadata 
from evaluator import Evaluator

storage_path = "util/eval/results/"

"""
Purpose of script:
    To evaluate (analysis FW) the maloss samples

"""


samples = metadata.get_malicious_pkg_list()

print(samples)
# exit()

""" Perform evaluation on maloss samples """
ev = Evaluator(pkg_list=samples, file_source=False)
ev.perform_evaluation()
ev.store_evaluation(do_json_store=False, do_pandas_tallies=False)
res = ev.get_results()
tal = ev.get_tallies()

""" Store tallies and result for easier use """
with open(storage_path+"maloss_eval_res.json", "w+") as f:
    json.dump(res, f)
with open(storage_path+"maloss_eval_tal.json", "w+") as f:
    json.dump(tal, f)


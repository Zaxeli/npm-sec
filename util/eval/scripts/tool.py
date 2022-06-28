import sys
import os
os.chdir(os.getcwd()+"/../../../")
sys.path.append(os.getcwd())
from evaluator import Evaluator


argv = sys.argv
pkg_arg = argv[1]
print(pkg_arg)

pkg = [pkg_arg]

ev = Evaluator(pkg_list=pkg, file_source=False)
ev.perform_evaluation()
ev.store_evaluation(do_json_store=False, do_pandas_tallies=False)
tal = ev.get_tallies()[0]
res = ev.get_results()[pkg_arg]
testnames = ev.get_testnames()

print("\n----- Anly results: -----\n")
# anly names -- anly tallies
for name, positive in zip(testnames[0], tal[1][1]):
        if positive == 1:
            msg = res[0][name]['msg']
            print("## "+name)
            print(msg)
            print("-----\n")

print("\n----- Typo results: -----\n")
# anly names -- anly tallies
for name, positive in zip(testnames[1], tal[2][1]):
        if positive == 1:
            msg = res[1][name]['msg']
            print("## "+name)
            print(msg)
            print("-----\n")
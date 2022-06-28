from pprint import pprint
from analyse_framework import Analysis_Framework
from typo_eval_framework import Typo_Framework
import sys


class Collective_Analysis:

    def __init__(self, pkg) -> None:
        self.name = pkg

        self.Analysis_FW = Analysis_Framework(pkg)
        self.TypoEval_FW = Typo_Framework(pkg)

        self.analysis_results = {}
        self.typo_eval_results = {}

    def get_name(self):
        return self.name

    def do_analysis(self, analysis_fw = True, typo_fw = True):
        """
        Performs both analyses unless specified in keyword args

        Returns results as tuple:
        - (analysis_results, typo_eval_results)
        """

        self.analysis_results = self.Analysis_FW.do_analyse_framework()     if analysis_fw==True else {}
        self.typo_eval_results = self.TypoEval_FW.do_typo_eval()            if typo_fw==True else {}

        return self.get_results()

    def get_results(self):
        """
        Returns results as tuple:
        - (analysis_results, typo_eval_results)
        """
        return (self.analysis_results, self.typo_eval_results)

    def get_analysis_results(self):
        return self.analysis_results

    def get_typo_results(self):
        return self.typo_eval_results

    def get_tally(self) -> tuple:
        """
        Returns a tally of how many alerts there were in each of the frameworks
        - (self.name, analysis_tally, typo_tally)
        """

        analysis_tally = self.tally_analysis_res()
        typo_tally = self.tally_typo_res()

        return (self.name, analysis_tally, typo_tally)

    def __tally_res(self, results: dict) -> int:
        """
        Tallies the argument results object's number of positives 

        Returns the total number of positives and the layout of positives ordered alphabetically acc to name
        (total tally, [positives layout] )
        """
        tally = 0
        positives = {}
        
        for test,res in results.items():
            
            if res['positive'] == True:
                tally += 1
                positives[test] = 1
            else:
                positives[test] = 0

        pos_layout = [pos for test, pos in sorted(positives.items())]   # sort and extract only the positive flag

        return tally, pos_layout

    def tally_analysis_res(self):
        """
        Tallies the number of alerts that have poisitve=True

        Returns a tuple: (tally, positives)
        - int: number of positives
        - ordered list: how the positives are spread across the test (ordered alphabetically to test name)
        """

        results = self.get_analysis_results()

        tally, positives = self.__tally_res(results)

        return tally, positives
        
        

    def tally_typo_res(self):
        """
        Tallies the number of alerts that have poisitve=True

        Returns an int: number of positives
        """
        
        results = self.get_typo_results()

        tally, positives = self.__tally_res(results)

        return tally, positives






if __name__ == "__main__":
    if len(sys.argv) >= 2:
        PKG_INPUT_NAME = sys.argv[1]
    else: 
        PKG_INPUT_NAME = 'reqeust'


    pkg_Analysis = Collective_Analysis(PKG_INPUT_NAME)
    a_results, typo_results = pkg_Analysis.do_analysis()


    pprint(a_results)

    print("\n ^ a_results \n")

    pprint(typo_results)

    print("\n ^ typo_results \n")

    print(pkg_Analysis.get_tally())

#--Immediate-er
# TODO_done: doing on 'port' has errors and is not invalid package

#--Larger
# TODO_done: implement some kind of tallying functionality of alarm positives to prepare for large-scale evaluaton
# TODO_done: implement storage of tallies and results to allow for analysis
# TODO: dependency graph for evaluating all of them.
    # Maybe only do typo eval on main input, and anaysis on all dependecy graph
    # Doing typo eval would also check if the dependencies fell victim to typosquatting or not.
# TODO: 
# TODO_done: Blacklist of users, how?
    # jus from MALOSS samples


# TODO_done: form lists for: 
# - top 1000, 
# - MALOSS names

# TODO: storage of positive count should also have point-wise bit
# TODO: perform evaluation on all packages
from math import trunc
import os, json
import pandas as pd
from multiprocessing import Pool, TimeoutError
from collective_analysis import Collective_Analysis



class Evaluator():


    def __init__(self, pkg_list='top_1000', file_source=True, start=0, truncate=None) -> None:
        """
        Reads the top 1000 packages names from the files and intiialises the Evaluator
        
        Args:
        - pkg_list: str or list
            the filename from where to get the pkgs; or
            the list to use as the packages
        - file_source: bool 
            specify if using file source or a list
        - start: int
            specify the starting position in the list of packages 
        - truncate: int
            specify if the position at which the list of pkgs should be truncated
        """


        self._dir = os.getcwd()+'/util/results/'
        self.tallies_f_json = self._dir + "eval/tallies.json"
        self.tallies_f_csv = self._dir + "eval/tallies.csv"
        self.res_f = self._dir + "eval/results"
        
        self.top_1000 = []
        self.tallies = []   
        self.results = {}

        # pandas dataframe
        self.tallies_df = None  


        if file_source:
            top_1000_f = self._dir+pkg_list

            with open(top_1000_f, 'r') as f:
                self.top_1000 = f.readlines()

            global _f
            def _f(x): return x[:-1]
            with Pool(processes=4) as pool:
                self.top_1000 = pool.map(_f, self.top_1000)

        else:
            self.top_1000 = pkg_list


        self.top_1000 = self.top_1000[start:truncate] # top 3 for testing
        print(self.top_1000)
        # for i in top_1000: print(i)


    def perform_evaluation(self):
        """
        Performs evaluation on each of the packages in top_1000
        and stores the CollectiveAnalysis object into list self.pkgs_CA
        """


        """
        next step:
        perform analysis on them

        foreach:
            CA obj
            do_analyse() -> results
            
            res[] := get_res() -> res

            tallies[] := get_tally() -> tallies

        """

        # Func: return CollectiveAnalysis object with analysis done
        global _h
        def _h(pkg):
            pkg_CA = Collective_Analysis(pkg)
            pkg_CA.do_analysis()
            return pkg_CA
        with Pool(processes=12) as pool:
            self.pkgs_CA = pool.map(_h, self.top_1000)


    def store_evaluation(self, do_json_store=True, do_pandas_tallies=True):
        """
        Saves the evaluation results to disk in util/eval/
        """

        """
        Now to store results on disk

            can use zip() to make list/dict

        tallies:
            needs:
            - pkg name 
            - tally

            format:-
            list? CHOSEN
            - redable with json
            - easily sortable
            - 

            dict?
            - readble with josn
            - easily indexable


        results:
            - name
            - a res
            - t res

            format:
            dict:
            name => (a res, t res)


        """

        pkgs_tallies = []
        pkgs_res = []

        global _i, _g
        def _i(pkg_CA: Collective_Analysis): 
            return pkg_CA.get_tally()
        def _g(pkg_CA: Collective_Analysis):
            return pkg_CA.get_results()

        with Pool(processes=12) as pool:
            pkgs_tallies = pool.map(_i, self.pkgs_CA)
            pkgs_res = pool.map(_g, self.pkgs_CA)




        self.tallies = list(pkgs_tallies)
        self.results = dict(zip(self.top_1000, pkgs_res))

        if do_json_store:
            with open(self.tallies_f_json, "w+") as f:
                json.dump(self.tallies, f, indent=4)

            with open(self.res_f, "w+") as f:
                json.dump(self.results, f, indent=4)

        if do_pandas_tallies:
            self.pandas_tallies()


    def pandas_tallies(self) -> pd.DataFrame:
        """
        Takes the json formatted tallies and forms a pandas.DataFrame out of it,
        assigning the dataframe to `self.tallies_df`s
        
        Also stores the dataframe as a CSV in 'tallies.csv' file

        Returns the full DataFrame also
        """

        testnames = self.get_testnames()
        d = self.tallies.copy()

        # Flatten rows of data
        data = []
        for i in d:
            x = [i[0], i[1][0]]
            x.extend(i[1][1])

            x.append(i[2][0])
            x.extend(i[2][1])

            data.append(x)

        # Flattened list of column names
        cols = ['name', 'anly.total']
        anlys = ["anly."+name for name in testnames[0]]
        cols.extend(anlys)
        cols.append("typo.total")
        typos = ["typo."+name for name in testnames[1]]
        cols.extend(typos)

        # Generate the list of tuples for each column
        tpl = []
        tpl.append(('name',))   # first column
        for i,fw in enumerate(['anly','typo']): # two sets of columns: anly and typo
            tpl.append((fw,'total'))    # first is 'total'
            for j in testnames[i]:
                tpl.append((fw,j))      # rest are the testname

        # MultiIndex column heading
        cols = pd.MultiIndex.from_tuples(tpl)

        # make DataFrame and then store as csv
        df = pd.DataFrame(data, columns=cols)
        self.tallies_df = df
        df.to_csv('util/eval/tallies.csv', index=False)

        return df


    def get_testnames(self):
        """
        Returns 2d list of testnames ordered alphabetically

        Returns:
        - [anly_testnames, typo_testnames]
        """

        pkg_CA = self.pkgs_CA[0]
        anly_testnames = pkg_CA.analysis_results.keys()
        typo_testnames = pkg_CA.typo_eval_results.keys()

        _testnames = [anly_testnames, typo_testnames]
        testnames = []
        for t in _testnames:
            t = list(t)
            t.sort()
            testnames.append(t)

        return testnames
        
    def get_tallies(self):
        """
        Returns the tallies as a list of format:

        [
            (pkg name, 
                (
                    a tally, (tally layout)
                    t tally, (tally layout)
                )
            )
            ...
        ]
        """
        return self.tallies
    
    def get_results(self):
        """
        Return the  evaluation results as a dict

        pkg name => (a res, t res)
        """
        return self.results



# ev = Evaluator(start=0, truncate=1000)
# ev.perform_evaluation()
# ev.store_evaluation()
# tallies = ev.get_tallies()
# result = ev.get_results()

# print(tallies)


# print(top_1000[0], json.dumps(pkgs_CA[0].get_results()[1], indent=4))





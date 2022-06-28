#! /usr/bin/python3

import dateutil.parser
import json
import threading
from util.typo_radius import TypoRadius
import util.fetch_metadata as metadata
import util.pkg_metadata_util as parse_util


"""

Building typo eval framework
"""
# PKG_INPUT_NAME = 'request'


class Typo_Framework:


    npm_registry = "https://registry.npmjs.org/"

    def __init__(self, pkg, allow_sec_holds=False) -> None:
        
        self.PKG_INPUT_NAME = pkg

        radius_obj = TypoRadius()
        self.typos = radius_obj.generate_typos(self.PKG_INPUT_NAME)

        # metadata for all the valid packages in radius 
        self.packages = {}

        # Results of the anlyses
        self.results = {}

        """
        generate typo candidates

        #spawn threads
            get published metadata
            if not live pkg,
                dont add
            else:
                add to packages
        #end threads

        """


        # Further optimisiation: use module multiprocessing.Pool(processes=n) ...
        def thread_cull_typos(pkg):
            """
            get metadata
            if not live, 
                return
            else,
                add packages[typo] = result
            """

            if pkg == 'requests':
                print(pkg)
            res = metadata.fetch_live_metadata(pkg)

            # do nothing if no metadata
            if res == False:
                return

            # do nothing if is security holding
            is_sec_holding = parse_util.check_security_holding(res)
            if is_sec_holding and not allow_sec_holds:
                return

            # TODO: check if deprecated holding. See: https://www.npmjs.com/package/loadash
            # This packages used to be malcious in version 0.0.1, ostensibly.

            self.packages[pkg] = res


        threads = []
        for i,typo in enumerate(self.typos):
            t = threading.Thread(target=thread_cull_typos, args=(typo,), name="thread-"+str(i))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        threads=[] # empty thread list


    def get_pkgs(self):
        """Returns full metadata of packages"""
        return self.packages
    def get_pkgs_names(self):
        """Returns just the names of the packages"""
        return self.packages.keys()


    """
    -----------------------------------------------------------------
    ----------------------------------------------------------------------
    Criterias Implementation
    ----------------------------------------------------------------------
    -----------------------------------------------------------------
    """


    def popularity_comparison(self):
        """
        -----popularity comparison-----

        If input package is the only popular pkg in radius, then all good.
        Else, mark positive and give message about other popular packages

        In other words, there must be only one popular package---the input package---for negative result.
        Because if there are other comparable popularity packages, then it is ambiguous

        TODO: make use of popularity results from analysis_framework?

        """

        POSITIVE = False
        MSG = ''



        """
        Get the downloads count for each package
        """

        packages_downloads = {}

        """ Multithreading download numbers retrieval """
        def thread_download_num(pkg):
            downloads = metadata.fetch_downloads(pkg)
            try:
                packages_downloads[pkg] = downloads["downloads"]
            except: packages_downloads[pkg]=0
                # print("\t\t\t\tDownla except @ ", pkg, downloads)
                # packages_downloads[pkg] = downloads["downloads"]

        threads = []
        for pkg in self.packages.keys():
            t = threading.Thread(target=thread_download_num, args=(pkg,), name="thread-"+pkg)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()


        """ TODO: caching of download numbers?"""
        # packages_downloads = {'reqeust': 56, 'urequest': 1, 'rquest': 4, 'reuqest': 7, 'request': 20259265}


        """
        Classify popular and not popular based on threshold
        """

        # TODO: make these thresholds more robust
        # percent_threshold = 0.4 # 40% 
        percent_threshold = 0.0002 # 0.02% based on the graph knee-point from analysing both pop (strict 2nd typo) and popN (manual reviewed typo) datasets
        min_threshold = 5000 # 5k seems to be a knee-point for n-th typo's downloads

        download_numbers = packages_downloads.values()
        max_downloads = max(download_numbers)
        cutoff = percent_threshold * max_downloads

        not_popular = []
        popular = []

        for pkg in packages_downloads.keys():
            if packages_downloads[pkg] >= cutoff and packages_downloads[pkg] >= min_threshold:
                popular.append(pkg)
            else:
                not_popular.append(pkg)


        # If the requested is not the only popular package within radius, raise alert
        if popular != [self.PKG_INPUT_NAME]:
            POSITIVE = True
            MSG += "The requested package seems to be obscure. Perhaps you meant to install another package?\n"

            popular_str = ''
            nonpopular_str = ''

            for pkg in packages_downloads.keys():
                info_str = "\t\t{}, weekly downloads: {}\n".format(pkg, packages_downloads[pkg])
                if pkg in popular:
                    popular_str += info_str
                else:
                    nonpopular_str += info_str

            MSG += "\tPopular packages:\n"
            MSG += popular_str

            MSG += "\tNon-Popular packages:\n"
            MSG += nonpopular_str


        # print("popularity")
        # print(POSITIVE)
        # print(MSG)

        return {"positive": POSITIVE, "msg": MSG}


 

    def age_comparison(self):

        """
        -----Initial release comparison (age comparison)-----


        check if older packages exit
        """

        POSITIVE = False
        MSG = ''


        package_init_release = {}

        for pkg in self.packages.keys():
            if pkg is '': continue
            init_release =  parse_util.init_release(self.packages[pkg]) # Get as ISO formatted string 
            init_release = dateutil.parser.isoparse(init_release) # parse into datetime.datetime object
            package_init_release[pkg] = init_release

        # print(package_init_release)

        # now to see if the input pkg is oldest
        ages = package_init_release.values()

        oldest_age = min(ages)
        oldest_name = [ k for k, v in package_init_release.items() if v == oldest_age][0]

        pkg_age = package_init_release[self.PKG_INPUT_NAME]

        if oldest_age != pkg_age:
            POSITIVE = True

            MSG += "There are typo packages older than your input. This might be indicative of typosquatting\n"
            MSG += "\tYour input: {} \tcreated: {}\n".format(self.PKG_INPUT_NAME, pkg_age)
            MSG += "\tOlder package: {} \tcreated: {}".format(oldest_name,  oldest_age)

        # print("age compare")
        # print(POSITIVE)
        # print(MSG)
    
        return {"positive": POSITIVE, "msg": MSG}


    def same_author_check(self):
        """
        -----same author check-----

        Is positive if there are more than one package in radius with same author,
        else is negative

        TODO: resolve this:-
        if the multi authors are same as requested package, then it might not be typosquatting,
        just that the author is reserving those names.
        But if user's rqueste is for illegitimate package, then it might be already in the typosqautters' region 
        and so the legitimate pkg is consideted wrong.

        """
        POSITIVE = False
        MSG = ''


        # authors = {} # dict of <package name> => <author>

        # authors = {} # <email> => < <name>, [<package>] >
            # email is not required key in `human` object

        authors = {} # author_str => [package]
        multi = False
        for pkg in self.packages.keys():
            if pkg is '': continue

            try:
                author = parse_util.get_latest_author(self.packages[pkg])
            except: continue
                # print("\t\t\tExcepton @ ", pkg, self.packages.keys())
                # author = parse_util.get_latest_author(self.packages[pkg])
            author_str = json.dumps(author, sort_keys=True)

            # print(pkg, author_str)

            if authors.get(author_str) == None:
                authors[author_str] = [pkg]
            else:
                multi = True
                authors[author_str].append(pkg)

        if multi:
            POSITIVE = True
            # display users and publishd pkgs
            MSG += "There are multuple packages in typo vicinity by same author. \
This might be indicativeof typosquatting or the orginal author reserving names. \
\nYou should review whether you are trying to install a typo package.\n"

            for author_str in authors.keys():
                pkgs = authors[author_str]
                author = json.loads(author_str)
                MSG += "\tAuthor: {}\n\t\t{}\n".format(author, pkgs)

        # print("same author")
        # print(POSITIVE)
        # print(MSG)

        return {"positive": POSITIVE, "msg": MSG}


    def do_typo_eval(self):
        """
        Perform the criteria anlyses

        Keys:
        - "popularity_comparison"
        - "age_comparison"
        - "same_author"
        """

        print("Typo Evaluating package: {}".format(self.PKG_INPUT_NAME))

        results = {
            "popularity_comparison": self.popularity_comparison(),
            "age_comparison": self.age_comparison(),
            "same_author": self.same_author_check()
        }

        self.results = results

        return results

    def get_results(self):
        return self.results



if __name__ == "__main__":
    PKG_uport = Typo_Framework('port')
    PKG_uport.do_typo_eval()
    print(json.dumps(PKG_uport.get_results(),indent=4))
#! /usr/bin/python3

import json
import util.fetch_metadata as metadata
import util.pkg_metadata_util as parse_util


"""
Building analysis framework
"""

class Analysis_Framework:

    """
    Each test criteria function returns a dict: 
    {
        "positive": bool,
        "msg: string
    }

    - positive indicates whether the test was positive
    - msg is the warning message to print, is empty if test was negative

    """

    npm_registry = "https://registry.npmjs.org/"


    def __init__(self, pkg) -> None:

        """
        Consolidate all useful varables in one place, and all the analyses with them separately. For vars reused across analyses 
        """

        self.PKG_INPUT_NAME = pkg

        self.pkg_metadata = metadata.fetch_live_metadata(self.PKG_INPUT_NAME)

        self.versions_raw_unsorted = parse_util.get_all_versions(self.pkg_metadata)
        self.versions_raw = parse_util.sort_raw_versions(self.versions_raw_unsorted)

        self.timestamps = parse_util.get_all_version_timestamps(self.pkg_metadata)
        self.versions_time_ordered = parse_util.get_versions_time_ordered(self.versions_raw, self.timestamps)

        self.latest_ver = parse_util.get_latest_version(self.pkg_metadata)
        self.latest_ver = parse_util.PkgVersion(self.latest_ver)

        self.authors = parse_util.get_authors(self.versions_raw, self.pkg_metadata)

        self.maintainers = parse_util.get_maintainers(self.versions_raw, self.pkg_metadata)

        self.blacklist_users = metadata.get_malicious_user_list()

        self.analysis_results = {}


    """
    ---------------------------------------------------------------------
    analyse version inconsistencies in package
    ---------------------------------------------------------------------
    """

    """
    Get the package metadata

    Get all versions

    get the version string usng util as list

    get version object (uitl) for each item in list

    compare 3-ver for each 1.2-or version
        see if any skip
        make use of skip detect util (TODO: implement this util)

    for now, just do skip_check() on all major versions (1-or ver)



    """



    def version_skipping(self):
        """
        -----version skipping-----
        """
        POSITIVE = False
        MSG = ''

        pkg_metadata = metadata.fetch_live_metadata(self.PKG_INPUT_NAME) 

        versions_raw_unsorted = parse_util.get_all_versions(pkg_metadata)
        versions_raw = parse_util.sort_raw_versions(versions_raw_unsorted) # by version num, not by time

        versions = [parse_util.PkgVersion(version) for version in versions_raw]

        # form set from all 1-ord versions in above list, to prevent repeats

        ver_ord_1_set = [ver.ver_ord_1 for ver in versions]
        ver_ord_1_set = set(ver_ord_1_set)

        skips = parse_util.skip_check(ver_ord_1_set)

        if skips:
            POSITIVE = True

            print_frndly = [str(i)+".x.x" for i in skips]
            
            MSG = "There are skips in version num (1st order patch num). Versions skipped: {}".format(print_frndly)
            # print(MSG)

        # print("skipped versions: ", skips)
        return {"positive": POSITIVE, "msg": MSG}


    def immature_package(self):
        """
        -----latest version < 1.0.0 => immature pkg-----
        """

        POSITIVE = False
        MSG = ''

        # pkg_metadata = metadata.fetch_live_metadata(self.PKG_INPUT_NAME)


        latest_ver = parse_util.get_latest_version(self.pkg_metadata)
        latest_ver = parse_util.PkgVersion(latest_ver)

        if latest_ver.ver_ord_1 < 1:
            POSITIVE = True
            MSG = "The latest version is {} It might not be a mature package and have bugs and vulnerabilities.".format(latest_ver.raw_version)

        return {"positive": POSITIVE, "msg": MSG}


    def strictly_inc_versions(self):
        """
        -----all versions are strictly increasing over time-----
        """

        POSITIVE = False
        MSG = ''

        # `versions_raw`` is patchnum-ordered

        timestamps = parse_util.get_all_version_timestamps(self.pkg_metadata)

        versions_time_ordered = parse_util.get_versions_time_ordered(self.versions_raw, timestamps)

        ### Testing detection of time-wise disordered version numbers 
        # x=6
        # temp = versions_time_ordered[x]
        # versions_time_ordered[x-1] = versions_time_ordered[x]
        # versions_time_ordered[x] = temp


        # x=10
        # temp = versions_time_ordered[x]
        # versions_time_ordered[x-1] = versions_time_ordered[x]
        # versions_time_ordered[x] = temp

        # check mismatch indices comparing versions_time_ordered and versions_raw (vernum ordered)
        mismatch = []
        for i, (ver_r, ver_t) in enumerate(zip(self.versions_raw, versions_time_ordered)):
            if ver_r != ver_t:
                mismatch.append(i)

        if len(mismatch) > 0:

            POSITIVE = True

            MSG += "There is some discrepancy in the time ordering of the package versions. It seems that a lesser versions number was published at a later time.\n"
            MSG += "Mismatches: \n"

            for i in mismatch:
                ver_r = self.versions_raw[i]
                ver_r_time = timestamps[ver_r]

                ver_t = versions_time_ordered[i]
                ver_t_time = timestamps[ver_t]

                MSG += '''\t{} at time {} \n\t{} at time {}\n\n'''.format(ver_r, ver_r_time, ver_t, ver_t_time)

        return {"positive": POSITIVE, "msg": MSG}



    def dist_tag_latest(self):
        """
        -----dist-tag latest is not same as timestamp latest-----
        """

        POSITIVE = False
        MSG = ''

        if self.versions_time_ordered[-1] != self.latest_ver.raw_version:
            POSITIVE = True

            MSG += "The latest dist-tag published version is not most recent\n"
            MSG += "\t'latest' version: {} \n\tmost recent version {}\n".format(self.latest_ver.raw_version, self.versions_time_ordered[-1])

        return {"positive": POSITIVE, "msg": MSG}



    def first_version(self):
        """
        -----first version > 1.0.0-----
        """

        POSITIVE = False
        MSG = ''

        v1_0_0 = "1.0.0"
        first_ver = self.versions_time_ordered[0]
        comparison = parse_util.compare_versions_raw(first_ver, v1_0_0)

        if comparison == 1:
            POSITIVE = True
            MSG += "The first version {} is greater than 1.0.0. This is inconsistent versioning and may mean malicious activity.".format(first_ver)

        return {"positive": POSITIVE, "msg": MSG}



    """
    ---------------------------------------------------------------------
    maintainer/owner inconsistencies 
    ---------------------------------------------------------------------
    """


    def maintainer_changes(self):
        """
        -----change/add/delete maintainer across versions-----

        first step, just check which versions mutates list of maintainers
        need to also check for ordering

        """

        POSITIVE = False
        MSG = ''

        # versions_raw # sorted raw strings
        # versions_time_ordered # time sorted
        maintainers = parse_util.get_maintainers(self.versions_raw, self.pkg_metadata)

        for i in range(1,len(self.versions_raw)):
            ver_prev = self.versions_raw[i-1]
            ver_next = self.versions_raw[i]

            m_prev = maintainers[ver_prev]
            m_next = maintainers[ver_next]

            if m_prev != m_next:
                POSITIVE = True

                MSG += "version {}: \t maintainers: {} \nversion {}: \t maintainers: {}\n\n".format(ver_prev, m_prev, ver_next, m_next)
                # print("version {}: \t maintainers: {} \nversion {}: \t maintainers: {}\n".format(ver_prev, parse_util.sort_maintainers(m_prev), ver_next, parse_util.sort_maintainers(m_next)))

            # print(ver, maintainers[ver])


            """
            TODO: use sets and disjunction to see changes
        
            """

        return {"positive": POSITIVE, "msg": MSG}



    def author_changes(self):
        """
        -----changes in owner/author-----
        """

        POSITIVE = False
        MSG = ''

        authors = parse_util.get_authors(self.versions_raw, self.pkg_metadata)


        first_ver = self.versions_raw[0]
        author_prev =  authors[first_ver] # initialise author_prev with the author of first version
        # author_prev = None

        for ver in self.versions_raw:
            author = authors[ver]

            if author != author_prev:

                POSITIVE = True
                MSG += "Authorship change at version {} :\n\tPrev author: {}\n\tNew author: {}\n".format(ver, author_prev, author)
                # (ver, author, author_prev, sep='\t')
                author_prev = author

        """
        TODO: Testing: Use npm_pkg_1093 to see if it detects change in ownership. Need to make another account on npm.
        """

        return {"positive": POSITIVE, "msg": MSG}



    """
    ---------------------------------------------------------------------
    Package popularity 
    ---------------------------------------------------------------------
    """


    def package_popularity(self):
        """
        -----popularity of package----- 
        """

        POSITIVE = False
        MSG = ''

        downloads = metadata.fetch_downloads(self.PKG_INPUT_NAME)
        downloads = downloads['downloads']

        # TODO: run experiment on npm ecosytem get download count distribution
        threshold = 5000 # hard-coded threshold for what is considered popular

        if downloads < threshold:
            POSITIVE = True

            MSG += "\nThis package does not seem to be popular and may be an obscure package with bugs or malicious code.\n"
            MSG += "\tlast week downloads: {}".format(downloads)

        # print(downloads)

        return {"positive": POSITIVE, "msg": MSG}


    """
    ---------------------------------------------------------------------
    malicious users 
    ---------------------------------------------------------------------
    """


    def malicious_authors_involved(self):
        """
        -----malicious authors involved-----
        """

        POSITIVE = False
        MSG = ''

        blacklist_users = metadata.get_malicious_user_list()

        # check is authors has a blacklisted user
        # using set operations

        blacklisted_author = False

        authors_all = self.authors.values()
        
        for user in blacklist_users:    
            if user in authors_all:
                POSITIVE = True

                blacklisted_author = user

                MSG += "\nThis package has an author who has been blacklisted for involvement with malicious packages.\n\tblacklisted author: {}\n".format(blacklisted_author)

                break

        return {"positive": POSITIVE, "msg": MSG}


    def malicious_maintainers_involved(self):
        """
        -----malicious maintainers involved-----
        """

        POSITIVE = False
        MSG = ''
        
        # check if maintainers has a blacklisted user

        maintainers_all = []
        for m in self.maintainers.values(): 
            try:
                maintainers_all.extend(m)
            except:
                pass
        
        # print(maintainers_all)

        blacklisted_m = []
        for user in self.blacklist_users:
            if user in maintainers_all:
                blacklisted_m.append(user)

        if blacklisted_m:
            POSITIVE = True
            
            MSG += "This package has maintainers who have been blacklisted for involvement with malicious packages:\n"
            for m in blacklisted_m:
                MSG += "\t" + json.dumps(m) + "\n"

        return {"positive": POSITIVE, "msg": MSG}


    def do_analyse_framework(self):
        
        print("Analysing package: ", parse_util.get_pkg_name(self.pkg_metadata))


        results = {
            "version_skipping": self.version_skipping(),
            "immature_package": self.immature_package(),
            "strictly_inc_versions": self.strictly_inc_versions(),
            "dist_tag_latest": self.dist_tag_latest(),
            "first_version": self.first_version(),

            "maintainer_changes": self.maintainer_changes(),
            "author_changes": self.author_changes(),

            "package_popularity": self.package_popularity(),

            "malicious_authors_involved": self.malicious_authors_involved(),
            "malicious_maintainers_involved": self.malicious_maintainers_involved(),
        }

        self.analysis_results = results

        return results

    def get_results(self):
        return self.analysis_results


# PKG_uport = Analysis_Framework("uport")
# PKG_uport.do_analyse_framework()
# print(PKG_uport.get_results())


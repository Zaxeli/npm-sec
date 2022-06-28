import re
import json
from pip import main
import pkg_resources
import requests
import dateutil.parser

class PkgVersion:

    raw_version = ''

    # Patch version: a.b.c
    ver_ord_1 = ''  # a
    ver_ord_2 = ''  # b
    ver_ord_3 = ''  # c

    ver_prefix=''
    ver_suffix=''

    def __init__(self, version_str: str):
        self.raw_version = version_str

        sectioned_ver = re.split("(\d+\.\d+\.\d+)", version_str)
        
        if len(sectioned_ver) < 3:
            raise Exception("Improper version string format: " + version_str)
        
        self.ver_prefix = sectioned_ver[0]
        self.ver_suffix = sectioned_ver[2]

        # patch_str is the numeric version num formatted as: x.x.x
        patch_str = sectioned_ver[1]
        
        split_patch = patch_str.split(".")

        if len(split_patch) < 3:
            raise Exception("Improper patch format. Expected fromat: x.x.x; given: " + patch_str)
        
        self.ver_ord_1 = int(split_patch[0])
        self.ver_ord_2 = int(split_patch[1])
        self.ver_ord_3 = int(split_patch[2])


def get_latest_version(pkg_metadata):
    """ Return raw version string of latest version"""
    return pkg_metadata["dist-tags"]["latest"]

def get_all_versions(pkg_metadata):
    """
    Returns list of all raw version strings
    """
    versions = pkg_metadata["versions"].keys()
    versions = list(versions)
    return versions

def get_version_metadata(pkg_metadata, version):
    return pkg_metadata["versions"][version]

def is_version_deprecated(pkg_metadata, version):
    version_info = get_version_metadata(pkg_metadata, version)
    
    if "deprecated" in version_info:
        return True
    else:
        return False

def is_unpublished():
    pass

def init_release(pkg_metadata):
    # try:
    #     return pkg_metadata["time"]["created"]
    # except:
    #     print( "\t\t\t\tException: @ ", pkg_metadata)
    #     print(get_pkg_name(pkg_metadata))
    #     return pkg_metadata["time"]["created"]
    return pkg_metadata["time"]["created"]

def skip_check(ver_num_set: set) -> list:
    """
    Takes a set of iterable version numbers (int) and checks if there are any version numbers skipped.
    Does not consider numbers larger than max value present in input as skipped, e.g., is list is [1,2,3] then 
    versions 5-9 are not considered skipped.

    args:
    - ver_num_set: set of type int, the versions numbers to perform check upon

    returns:
    - iterable list of versions numbers that were skipped


    TODO: Should I ignore '0' patch num? 
    One of the analysis criteria might be to say that if first version > 1.0.0, 
    then raise flag. In that case, path num '0' is not necessary.

    """
    ver_num_list = list(ver_num_set)
    ver_num_list.sort()

    max_ver = ver_num_list[-1]

    skipped_vers = []

    for i in range(max_ver):
        if i not in ver_num_list:
            skipped_vers.append(i)


    return skipped_vers

def sort_obj_versions(versions: list):
    """
    Sorts the versions (PkgVersion object), based on the version numbers and not the timestamps
    """
    versions.sort(key= lambda x: (x.ver_ord_1, x.ver_ord_2, x.ver_ord_3))
    return versions


def sort_raw_versions(versions: list):
    """
    Sorts the raw version strings on the version number and not the timestamps
    """
    versions = [PkgVersion(ver) for ver in versions]
    versions = sort_obj_versions(versions)
    versions = [ver.raw_version for ver in versions]
    return versions

def get_versions_time_ordered(raw_versions: list, timestamps: dict):
    """
    Returns a list of the given versions ordered on the timestamp of version release. It is subordered by the version number.

    args:
    ---
    - raw_versions: a list of raw version strings which the function orders on their timestamps
    - timestamps: a dict of timestamps to use for ordering the versions
    """

    sorted_versions = raw_versions.copy() # unsorted copy

    # Parses the timestamp of the version to a datetime, to be used for sorting
    # ordering priority: timestamp, version num 
    def ordering_func(ver):
        t = dateutil.parser.isoparse(timestamps[ver])
        ver_obj = PkgVersion(ver)
        v1 = ver_obj.ver_ord_1
        v2 = ver_obj.ver_ord_2        
        v3 = ver_obj.ver_ord_3        
        return(t, v1, v2, v3)

    sorted_versions.sort(key=ordering_func)

    return sorted_versions


def get_all_version_timestamps(pkg_metadata):
    """
    Returns a dict containing all versions' timestamps. The keys are ordered only on version numbers and not the timestamp
    """
    versions = get_all_versions(pkg_metadata)
    versions = sort_raw_versions(versions)

    version_timestamps = {}

    for ver in versions:
        version_timestamps[ver] = pkg_metadata["time"][ver]

    return version_timestamps

def get_all_versions_time_ordered(pkg_metadata):
    """
    Uses package metadata to get list of all versions. Then gets all the timestamps for versions releases.
    Then uses these to order all versions according to (timestamp, (v1,v2,v3))
    """

    versions = get_all_versions(pkg_metadata)
    timestamps = get_all_version_timestamps(pkg_metadata)

    versions_time_ordered = get_versions_time_ordered(versions, timestamps)

    return versions_time_ordered

def compare_versions(ver1: PkgVersion, ver2: PkgVersion):
    """
    Compares two PkgVersion objects for greater, lesser or equal

    returns (int):
    -  1: ver1 > ver2
    -  0: ver1 == ver2
    - -1: ver1 < ver2
    """
    ver1_num = (ver1.ver_ord_1, ver1.ver_ord_2, ver1.ver_ord_3)
    ver2_num = (ver2.ver_ord_1, ver2.ver_ord_2, ver2.ver_ord_3)

    return (ver1_num > ver2_num) - (ver1_num < ver2_num)


def compare_versions_raw(ver1, ver2):
    """
    Wrapper around compare_versions() to allow for raw version strings
    """
    ver1_obj = PkgVersion(ver1)
    ver2_obj = PkgVersion(ver2)
    res = compare_versions(ver1_obj, ver2_obj)
    return res


def sort_maintainers(maintainers: list, key='email'):
    """
    Sorts a list of maintainers based on email.
    Key can be optionally specified in param
    """
    if maintainers == None:
        return None

    maintainers.sort(key=lambda m: m[key])
    return maintainers


def get_maintainers(versions: list, pkg_metadata, ):
    """
    Fetches the list of maintainers for each of the versions passed to it

    TODO: can modify to support not adding keys for empty values?

    args:
    - versions: list of raw version strings
    - pkg_metadata: json pf package metadata
    
    returns:
    - dict of maintainers for each of the versions given in input 
    """

    maintainers = {}
    

    pkg_metadata_ver = dict(pkg_metadata["versions"])

    for ver in versions:
        m = pkg_metadata_ver[ver].get("maintainers")
        m = sort_maintainers(m)
        maintainers[ver] = m

    return maintainers

def get_all_maintainers(pkg_metadata):
    """
    Fetches maintainers for all versions in pkg metadata. 
    Returns info as dict: (str) versions => (list) maintainers
    """

    versions = get_all_versions_time_ordered(pkg_metadata)
    maintainers = get_maintainers(versions, pkg_metadata)

    return maintainers

def get_all_maintainers_set(pkg_metadata):
    """
    Gets all the maintainers across all versions and removes duplicates
    Returns the users as a set
    """

    maintainers_dict = get_all_maintainers(pkg_metadata)

    maintainers = set()

    for ver,mtrs in maintainers_dict.items():
        for m in mtrs:
            m_str = json.dumps(m, sort_keys=True)
            maintainers.add(m_str)
    
    return maintainers
    

def get_authors(versions: list, pkg_metadata: dict):
    """
    Fetches the author for the versions given in input

    args:
    - versions: list of version strings
    - pkg_metadata: package metadata json  

    returns:
    - dict of author for given versions <version> => <author>

    """

    authors = {}

    for ver in versions:
        try:
            # author = pkg_metadata["versions"][ver]["_npmUser"]
            author = pkg_metadata["versions"][ver]["author"]
        except:            
            try:
                author = pkg_metadata["versions"][ver]["_npmUser"]
            except:
                # continue
                author = None
        
        authors[ver] = author
    
    return authors

def get_all_authors_set(pkg_metadata: dict):
    """
    Gets all authors for the package metadata and eliminates duplicates
    """

    vers = get_all_versions(pkg_metadata)

    authors = set()

    for ver in vers:
        athr = get_authors([ver], pkg_metadata) # get a dict type of ver => author
        athr = athr[ver]    # get just the author 
        athr = json.dumps(athr, sort_keys=True)
        authors.add(athr)

    return authors


def get_latest_author(pkg_metadata: dict):
    """
    Gets the latest author from the package metadata json object provided

    returns:
    - `human` object, per npm standard 
    """

    latest_ver = get_latest_version(pkg_metadata)
    author = get_authors([latest_ver], pkg_metadata)
    try:
        author = author[latest_ver]
    except:
        print("problem: ",get_pkg_name(pkg_metadata))
        raise Exception()

    return author

def check_security_holding(pkg_metadata):
    """
    Checks if the package is a security holding by looking for 3 things:
    - git repo = secuirty holding git repo
    - maintainer is npm
    - version is "0.0.1-security"
    - description = ""
    """

    # hardcoding the security holding attributes
    security_repo = {'type': 'git', 'url': 'git+https://github.com/npm/security-holder.git'}
    npm_maintainer = [{'email': 'npm@npmjs.com', 'name': 'npm'}] 
    sec_version = "0.0.1-security"
    sec_description = 'security holding package'


    try:
        if not pkg_metadata['repository'] == security_repo:
            return False
        if not pkg_metadata['maintainers'] == npm_maintainer:
            return False
        if not get_latest_version(pkg_metadata) == sec_version:
            return False
        if not pkg_metadata['description'] == sec_description:
            return False
    except:
        return False

    return True

def get_pkg_name(pkg_metadata):
    """
    Fetch the package name from the package metadata given in input
    """

    return pkg_metadata["_id"]
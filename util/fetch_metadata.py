import readline
import sys
import os
import json
import requests

npm_registry = "https://registry.npmjs.org/"
npm_downloads = "https://api.npmjs.org/downloads/"

metadata_dir = os.getcwd()+'/'
if metadata_dir.split('/')[-2] != 'util':
    metadata_dir += "util/"

data_dir = metadata_dir+"data/"
# not_exists = data_dir+"not_exists"
not_exists = metadata_dir+"not_exists"

blacklist_dir = metadata_dir+"blacklist/"
users_blacklist = blacklist_dir+"users"
pkgs_blacklist = blacklist_dir+"samples"


def get_stored(pkg):
    """
    description:
    checks if the pkg metadata is already stored

    args:
    - pkg: name of package
    returns:
    - data if it exists
    - False, if no file or file empty 

    TODO: check for stale cache, if the file was made more than 7 days ago (because npm uses *weekly* downloads)
    """
    filename = data_dir+pkg
    f = None

    try:
        f = open(filename)
        metadata = json.load(f)
        f.close()
        return metadata
    except:
        # print("File does not exist or is empty", file=sys.stderr)
        return False
    
def get_network(pkg):
    """
    description:
    gets the package metadata from network by querying npm registry and return the json
    format response, or Flase if status code not 200

    args:
    - pkg (string): name of pkg
    returns:
    - metadata as json, or False
    """

    resp = requests.get(npm_registry+pkg)

    if resp.status_code != 200: 
        return False

    return resp.json()
    

def fetch_metadata_(pkg):
    """
    args:
    - pkg_name: the package for which to fetch the metadata
    returns:
    - json object with metadata of the requested pkg
    - False, if invalid

    description:
    Checks in data/not_exists for whether the pkg was tried before and see if it is valid.
    Then, if valid, it should check whether the pkg metadata already exists in data/ and if it does,
    then it parses and returns it. Otherwise, it will make a network call to fetch detailed metadata
    from npm registry, store it for reuse later, and then return a json object
    """
    
    # check data/not_exists for validity
    with open(not_exists, "r") as f:
        invalid_pkgs = f.readlines()
        if pkg+"\n" in invalid_pkgs:
            return False

    # if metadata already stored, return 
    metadata = get_stored(pkg)
    if metadata:
        # print("returning stored")
        return metadata

    # fetch from npm registry if not
    metadata = get_network(pkg)
    if metadata:
        # print("writing now")
        fname = data_dir+pkg
        try:
            os.makedirs(os.path.dirname(fname), exist_ok=True)
            with open(fname, "w+") as f:
                json.dump(metadata, f)
        except: pass
        return metadata

    # if network didn't get, then update into data/not_exists and return False
    with open(not_exists, "a") as f:
        f.write(pkg+"\n")
        
    return False

def fetch_live_metadata(pkg):
    """
    Fetches the metadata only if currently live (published) and has not been unpublished
    
    """
    
    metadata = fetch_metadata_(pkg)

    metadata_str = json.dumps(metadata)

    if "unpublished" in metadata_str:
        return False
    else:
        return metadata


def downloads_link(duration, pkg):
    """
    See npm API documentation for getting downloads count for building better links
    https://github.com/npm/registry/blob/master/docs/download-counts.md
    """

    link = npm_downloads
    link += "point" + "/"   # for point data
    link += duration + "/"  # for this duration, "last-week" by default
    link += pkg             # for this pkg

    return link


def fetch_downloads(pkg):
    """
    Fetches the number of downloads over the last week
    and returns the json response
    """

    url = downloads_link("last-week", pkg)

    res = requests.get(url)
    # print(url, res, res.json())
    if res.status_code != 200:
        return False

    return res.json()

def fetch_downloads_num(pkg) -> int:
    """
    Fetches just the download number for last week
    Returns: int
    """
    res = fetch_downloads(pkg)
    return res['downloads']



def get_malicious_user_list(stringly=False):
    """
    Fetches the users added in the blacklist.
    Each of the users is a 'human' type per npm specs

    Returns a list of 'human' variables (dicts)

    Args:
    - stringly: if the elements in result list should be stringified  
    """
    
    users = []

    with open(users_blacklist) as f:
        line = f.readline()
        while line:
            users.append(json.loads(line))
            line = f.readline()

    if stringly:
        users = [json.dumps(user) for user in users]

    return users

def get_malicious_pkg_list():
    """
    Fetches the list of blacklist packages
    
    Returns a list of those pkgs
    """
    
    pkgs = []

    with open(pkgs_blacklist) as f:
        pkgs=f.readlines()

    pkgs = [p[:-1] for p in pkgs]


    return pkgs
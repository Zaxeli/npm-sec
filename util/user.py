"""
# Form a blacklist:

Enumerate all packages and subpakcages which is then used to get from npm
the metadata for each one. This metadata is then parsed to get the list of maintainers 
and the list of authors. These users are then added to the blacklist


TODO:
Alternative approach (not implemented atm):
Go through all the packages folders and find package.json files. When it is found, get all the users 
and form them into `human` types which is then json-strigified before writing to blacklist.
    See:
    - `ls -R ../../../npm`
    - if .tgz file then decompress

"""
import sys

sys.path.append("..")

import os
import fetch_metadata as fetcher
import pkg_metadata_util as parseutil

# path = "../../../npm/"
path = "../../npm/" # path to folder containings maloss samples
path_blklist = "blacklist/"

def get_all_pkgs():
    pkgs = os.listdir(path)
    pkgs.sort()

    pkgs_plain = [] # without "@"
    pkgs_sub = []   # with "@"

    for p in pkgs:
        if "@" in p:
            pkgs_sub.append(p)
        else:
            pkgs_plain.append(p)

    # print(pkgs_plain)
    # print("users")
    # print(pkgs_sub)


    pkgs_sub_enlist = []
    for i in range(len(pkgs_sub)):
        p = pkgs_sub[i]
        sub_pkgs = os.listdir(path+p)
        sub_pkgs = [p+"/"+_p for _p in sub_pkgs]
        pkgs_sub_enlist.extend(sub_pkgs)

    # print(pkgs_sub_enlist)

    pkgs = pkgs_plain + pkgs_sub_enlist
    pkgs.sort()

    # print(pkgs)
    return pkgs


pkgs = get_all_pkgs()


pkgs_metadata = {}
for p in pkgs:
    metadata = fetcher.fetch_live_metadata(p)

    # if metadata == False:
    #     print(p)

    pkgs_metadata[p] = metadata


pkgs_users = {}     # dict of sets

all_users = set()

for p in pkgs:
    # print(p)
    # print(json.dumps(pkgs_metadata[p], indent=4))

    maintainers = parseutil.get_all_maintainers_set(pkgs_metadata[p])
    authors = parseutil.get_all_authors_set(pkgs_metadata[p])

    users = maintainers.union(authors)

    pkgs_users[p] = users
    all_users = all_users.union(users)


all_users = list(all_users)

print(all_users)


with open(path_blklist+"users", 'w+') as f:
    for u in all_users:
        f.write(u+'\n')

with open(path_blklist+"samples", "w+") as f:
    for p in pkgs:
        f.write(p + "\n")
# print(pkgs_metadata)
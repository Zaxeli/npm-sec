# Utilities

This folder contains utilities, cached data, and various lists that are used in this project.

## Blacklists

The `blacklist/` folder contains blacklists of users and packages. More info in the folder's `README.md`.

## Cached Data

The `data/` folder contains the cached metadata for all the packages that any of the scripts or classes download as part of any analysis. This speeds up the processing considerably since retirieving the metadata for a package freshly every time is not efficient. Each package has its metadata stored in the a file of its own name. There is also metadata stored for scoped packages (e.g. `@angular/http`), which are in a folder for their own scope. This metadata is automatically restored if it has been deleted, otherwise the stored metadata is used for any of the analysis. As such, these must be deleted manually to refresh the cached metadata.

It also contains the `not_exists` file which has the names of packages which do not exist.
Edit: moved to be under `util/` from `util/data/`

## Eval

The `eval/` folder has various things relating to the evaluation of the tool, as well as scripts for various things.

> `eval/scripts/npm-sec.sh` or `eval/scripts/tool.py`: The script to make use of this tool for a standalone package.

More info in the folder's `README.md`

## Top 1000 packages list

Sourced from:
- https://github.com/anvaka/npmrank
- https://gist.github.com/anvaka/8e8fa57c7ee1350e3491

The file `top_1000` contains the top 1000 npm packages based on the number of dependents in the npm registry ecosystem. This list is used for things like analysing downloads to get threshold values and performing evaluation.


## Util python files

### `user.py`
This is a utility script used to generate the blacklists.

## `typo_radius.py`

This is a script for generating typos around a given input name. Before using the output from this, it is further filtered to check if the packages exist or are invalid names.

## `fetch_metadata.py`

This file contains utility functions relating to fetchin metadata for use, getting the download numbers for a package, getting blacklisted users, getting blacklisted packages, etc.

## `pkg_metadata_util.py`

This file contains utility functions and classes relating to parsing of metadata and processing it to get various different things such as getting all the version numbers, authors, latest version, dist-tag, checking if packages is deprecated, if it's a security gholding, comparing versions, etc.

More info in the file itself.
# Scripts

Mainly contains one-time-use python code for evaluation purposes such as collecting data, processing, graphing, etc.

# Purpose of scripts

The purpose of each script is given below:

## Tool

### `tool.py`

This script makes use of the main classes and uses them to analyse a single package given as input at a command-line argument instead of a bulk of many packages.

It performs all the implemented tests for the package and prints the results.

### `npm-sec.sh`

This is a bash script which makes use of `tool.py` and adds the functionality of asking for the user's confirmation to continue with installation. If the user confirms, it runs an `npm install` command for the requested package.

## Evaluation scripts:

### `eval.py`

This scripts fetches the list of the top 100-200 packages and also a randomly chose typo for each of them. These packages are retrieved from `results/test_pkgs.npy`.

It then uses the original 100-200 packages as the set of benign samples, and the random typos as the set of typo samples. It performs the bulk evaluation with the implemented metadata test on both of these sets. Once the evaluation is done, it stores the results as well as the tallies as json files.

The tallies hold only whether the packages raised a positive for the tests and also the total number of positives for each set of tests (Anly or Typo test sets). It stores it in the `results/test_tallies.json` file.

The results holds the full metadata test results that are obtained after the evaluation. This includes the package name, the test name, whether the test was positive, and, if the test was positive, it also has the warning message for that test and package. It is stored under `results/test_results.json`.


### `maloss_eval.py`

This script complements the `eval.py` and has similar purpose, but it performs the evaluation for the malicious sample set, which was obtained from Prof Brendan from the work in MALOSS.

It performs the evaluation for all the implemented metadata tests for these malicious samples. It saves the tallies and results in the same way as `eval.py`. The tallies are stored in `results/maloss_eval_tal.json` and the results are stored in `results/maloss_eval/res.json`.

### `test_samples.py`

The purpose of this script is to prepare the benign and typo sample sets for the evaluation in `eval.py`.

This script uses the top1000 packages file and then parses it to get a python list from it containing all the top 1000 packages. It then selects the packages of rank 100-200. After that, it chooses a random typo for each of them. The script then filters out those packages which did not have any valid typos and also those which had a '@' in it. It omits '@'-packages because it denotes a scoped package and was problematic to produce typos for. It works because the purpose here is to get a sample for evaluation, which doesn't strictly have to be the top 100 or ranks 100-200. Once the samples are obtained, it stores them in `results/test_pkgs.npy`.


## Graphing scripts

### `graph_analysis.py`

This script retrieves the tallies and results from the evaluation of all three sample sets: benign, typos and maloss. It then uses these tallies to plot the number of positives as percentages of the sample size. It can do this for both the Anly and Typo tests. It makes use of matplotlib to plot the figures.

It saves the figures in `result/graph_analysis_mls.png`. This script was also used to create figures separately for the Anly tests and the Typo tests. This can be done by simple disabling the code which graphs either one.

Thi script was used to produce the figures in `results/`:
- `graph_analysis.png`
- `graph_analysis_mls.png`
- `graph_anly_mls.png`
- `graph_typo_mls.png`

### `maloss_graph.py`

This script was originally intended to separately graph the maloss tallies and results, but was discontinued and was not used. It was kept as an artifact to help with writing the `graph_analysis.py` script.

## Thresholding script

These scripts are used for the purpose of the analysing packages to see what is a good value to use as a popularity threshold.

### `illegit_typo.py`

A script to parse the `illegit_typo.csv` file. Serves just to see the data.

### `thresholder.py`

This script is used for getting two thresholds: percentage threshold and absolute download numbers threshold. It does this by aalysing the top 100 packages from the top1000 list, and all of their typos. 

It analyses the first typo (2nd in the list of packages, if including the main pkg), and the n-th typo. The n-th typo is manually reviewed from the typo list to identify which package (ordered by number of downloads) has its downloads most likely to be coming from typos that devs make while installing. The first pkg to be identified as such is the n-th typo.


First, it analyses the first typo:

It uses the data from `results/popularities.json` which holds info on weekly download numbers for packages and their typos. It uses a pool of processes to get three things:
1. The difference in download numbers between the main package (from the top 100 list) and the first typo (the typo with most downloads after the main pkg).
2. The fraction of downloads (used later as percentage) the first typo has relative to the main pkg.
3. The download numbers for the first typo.

It then filters out empty values which may have been entered for reasons such as there not being a valid typo for a package. It also calculates various statistics for these: min, max, mean, standard deviation.

Next, it analyses the n-th typo:

It uses the `illegit_typo.csv` file for information on the n-th typo for each main package. The value of `n` was idenitfied manually by looking at various things like the npm package webpage, github repo, download numbers, versions, authors, activity, utility, etc. After looking at these things, an informed decision was made about whether the package got it downloads from typos or not.

It calculates the same 3 things for these n-th typos as it did before. It then caluclates the same statistical properties as well.

After this is done, it plots the graphs for these 4 things:
1. A cumulative graph showing the number of packages where the n-th typo has a % of the main package's downloads. 
2. A cumulative graph showing the number of packages where the first typo has a % of the main package's downloads.
3. A cumulative graph of the download number of the n-th typo.
4. A cumulative graph of the download number of the first typo.

The figure is in `figures/thresholder.png`

The knee points are also highlighted.

## Popularities

### `pop_trend.py`

This script prepares the list of top 100 pacakges and does the following for each package:
1. It generates a list of typos
2. Gets the download numbers for the main package and the typos.
3. Sorts the typos by number of downloads

It then saves the data into `results/popularities.csv`.


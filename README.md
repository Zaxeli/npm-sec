# Npm package manager security for developers using metadata analysis

This project was done as my final practicum for completing MS in Cybersecurit @ Georgia Tech. I worked on it during January-May 2022, and completed it in May 2022.

The paper for this project is available here: [Npm package manager security for developers using metadata analysis](https://github.com/Zaxeli/Zaxeli.github.io/blob/main/files/npm_sec.pdf).

It takes much inspiration from the work of [Maloss](https://github.com/osssanitizer/maloss). Their paper is available at [Towards Measuring Supply Chain Attacks on Package Managers for Interpreted Languages](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_1B-1_23055_paper.pdf).

This is the code which I have made publicly available for my project. The project is described in the paper in much more detail.

 <!-- It main package radius analyser for npm metadata analysis.  -->

## How to use

You can use the tool in order to perform a standalon analysis using the following methods:

1. `./npm-sec.sh`: You can use the script present in the base folder by giving it a package name as an argument. This makes use of the `npm-sec.sh` located in the `util/eval/scripts/` folder. It will perform the tests and then ask for confirmation to continue with installation of the npm package.
2. `util/eval/scripts/npm-sec.sh`: You can navigate to this script and then run it with an argument package name.
3. `util/eval/scripts/tool.py`: This will perform the analysis for the package name but it will not ask for confirmation to continue with install. It will do nothing more than perform the metadata tests and print the results.


The tool performs various metadata tests in order to give the user an idea about whether the requested package could be malicious or not. It will print out information for the tests if they raise a positive. This info can be used to make a decision about continuing the installation.

## Structure

The project is structered into two modules of metadata tests that it performs: 
1. Typo tests: Tests which look at attributes across all the packages in the typo radius. These are implemented in `typo_eval_framework.py` under the `Typo_Framework` class.
2. Anly tests: Tests which look at attributes of a package without the context of other packages in the typo radius. These are implemented in `analyse_framework.py` under the `Analysis_Framework` class. (Anly is short for 'self-analysis')

The `collective_analysis.py` file contains the `Collective_Analysis` class. It makes use of both the above classes to perform the full range of metadata tests for the packages. It also stores state and results for the packages that are testes, once their tests are completed.

The `evaluator.py` contains the `Evaluator` class. It is used to perform the metadata tests for a bulk of packages. This is mainly useful for the evaluation of the tool developed in this project.  


## Metadata tests

The tests performed for each module are listed below. A more in-depth desciprtion and discussion of these tests is given in the paper linked at the beginning. It also describes and discusses the evaluation results and the effectiveness of each of these tests.

### Anly

1. Version Skipping
2. Immature Package
3. Strictly Increasing Version Numbers
4. Dist-tag is the latest version
5. First Version
6. Maintainer Changes
7. Author Changes
8. Package Popularity
9. Malicious Authors Involved (blacklist)
10. Malicious Maintainers Involved (blacklist)

### Typo

1. Popularity Comparison
2. Age Comparison
3. Same Author Check


## Contact

Feel free to contact me for any information that might be missing in the documentation of this project. I would be more than happy to provide any help.


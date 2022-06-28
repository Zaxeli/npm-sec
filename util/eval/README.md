# Evaluation results

This folder hold the various things that were produced from the evaluation and were used in doing the evaluation of the tool.

## Figures

The figures are produced by the scripts in `scripts/` folder, used in the analysis. The data which these fugures graph are also available in the `results` folder. Some of the figures are copies made to preserve them from beng overwritten, as a precaution when using the scripts. (kinda hacky, i know) 

## Results

This folder contains the data which was used thourghout the analysis. It contains both csv and json formatted data for most of them, to assist with parsing it using both json or pandas as convenient. These are also mostly generated from the scripts in `scripts/`. The explanation is also given in the description of the scripts, as relevant.

## Scripts

This folder contains scripts that were used for various purposes. These are mostly one-time-use codefor the purpose of collecting data, graphing it, processing it, etc.

This folder also constains the scripts `npm-sec.sh` and `tool.py` which can be used to perform the main analyses of this tool for a single package. The classes in the python files in the base folder are mainly for bulk analysis of packages, used in the evaluation of this tool.





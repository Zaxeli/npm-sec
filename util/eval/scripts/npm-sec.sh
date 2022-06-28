#! /bin/bash

echo "Usage: ./npm-sec.sh <package_name>"

python3 tool.py $1

echo "Please review the alerts and indicate if you wish to continue with \`npm install $1\`. (y/n)?"
# exit
read cont
echo $cont

# read input
if [[ $cont == "Y" || $cont == "y" ]]; then
        npm install $1
else
        echo "don't do that"
        echo 1
fi
# Blacklists

This folder contains the blacklists used in the analysis of the tools as well as some of the metadata tests.

## Package blacklist

File `samples` contains the blacklisted packages. 

These are known malicious samples as provided by Prof. Brendan from the work done in MALOSS.

## User Blacklist

File `users` hold the blacklist of users in the form of an npm 'human' JSON object.

These were compiled by going through the list of package samples and then collecting all users, whether they were maintainers, authors or owners for the package. 





# Chaoss Microtasks for GSoC
This repository contains microtasks for GSoC project "Reporting of CHAOSS Metrics"
Each microtask is contained in seperate folders and has its own README, which states installation guides for that microtask.

# Descriptions
**Microtask 1**: Produce a listing of the number of new committers per month, and the number of commits made by each of them. Present the listing as a table and as a CSV file. Analyse the GrimoireLab enriched index for git.

**Microtask 3**: Produce a listing of repositories, as a table and as CSV file, with the number of commits authored, issues opened, and pull requests opened, during the last three months, ordered by the total number (commits plus issues plus pull requests).

# Other files
**report.pdf**: It is a report produced using Manuscripts based on an index `git_voc` with `Git` as data source. It has Grimoirelab logo and not the previous Bitergia logo.
**sample_code**: This folder contains two jupyter notebooks which contain sample, crude implementaion of what I propose to do in Manuscript. I tackled three metrics from https://github.com/chaoss/metrics/blob/master/1_Diversity-Inclusion.md. They are : `New Contributors vs Maintainers`, `Contributor`, and `Change in maintainer number`. The data for these metrics need to be obtained manually and is more difficult, so I tackled these first, and provided sample implementation.

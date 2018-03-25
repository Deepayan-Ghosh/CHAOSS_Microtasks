# CHAOSS-MICROTASK 1
The goal of this project is to analyse a git repository to obtain the number of new committers per month, and also to obtain the number of commits made by each one of the new committers. Then finally we present the results as a `table` and a `csv` file. The result is obtained by querying Elasticsearch indices for relevant data, and manipulating obtained data.



## Getting started
Follow the below instructions to get the code running on your local system. For this project, we mainly need `python3` and `elasticsearch`, `grimoirelab`,`pandas`,`json` packages installed.

### Pre-requisites
Install all the support systems needed, by following:
https://grimoirelab.gitbooks.io/tutorial/before-you-start/supporting-systems.html
Follow this link to install `grimoirelab`:
https://grimoirelab.gitbooks.io/tutorial/before-you-start/installing-grimoirelab.html

### Installing
Get a copy of the code:
``` git clone https://github.com/Deepayan-Ghosh/CHAOSS_Microtasks.git```

Change directory using:
```cd microtasks/microtask1```

Make the python script `microtask1.py` executable by running the command:
```chmod a+x microtask1.py ```

Then run the script as:
```./microtask1.py -h```

You can also run the script by calling `python3` every time like:
```python3 microtask1.py -h ```



## Options
Command line arguments allow users to input the name of indices, `csv` files, etc. You can get a list of all command line options using `-h` as:
```
$ ./microtask1.py -h 
OR
$ python3 microtask1.py -h
usage: microtask1.py [-h] -u URL [-R REPO] [-r RAW] -e ENRICH [-c] -o1 OUTPUT1 -o2
                OUTPUT2
optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     URL of elasticsearch instance
  -R REPO, --repo REPO  Name of git repo
  -r RAW, --raw RAW     Name of raw index to be used or created
  -e ENRICH, --enrich ENRICH
                        Name of enirched index to be used or created
  -c, --create          Flag, used to create indices, else only analysis is
                        done
  -o1 OUTPUT1, --output1 OUTPUT1
                        Output filename for commiter number details
  -o2 OUTPUT2, --output2 OUTPUT2
                        Output filename for commit details

```
where `-u`,`-e`,`-o1` and `-o2` are mandatory as they represent URL, enrich index name to be analysed, and name of `csv` files, that the user wants. If the user wants to both create and analyse the indices, then `-R`,`-r` options are necessary along with `-c` flag. Here everything is user-input, the index names, the `repo` for which indices are to be created and output filenames.



## Detailed Explanation
The script takes as input the `url` of a elasticsearch instance. It also take as input the name of  a `girmorelab` enriched index, which it then queries to obtain the relevant information, that is, the `author_name` and `commit_date` fields. Here, we assume that the enriched index already exists. However the user can also create an index and then analyse it using the `-c` option. If the user uses `-c` option, then he must also provide an url of the repository whose index is to be created, and also the names of raw and enriched indices that the user wants. If `-c` option is used, then the `create_index()` function is called with appropriate arguments, which uses `p2o.py` to create the indices. Then, analysis begins by calling `get_info_from_index()` function which queries the elasticsearch index to obtain the `author_name` and `commit_date` fields, and returns the query result. The query result is consumed by `find_commiter_per_month()` which produces a mapping (dict) of `months` to number of committers, their names and the commits made by each. Then `create_tables_from_report()`uses the dict to create `csv` files and `pandas` dataframes.



## Examples
```
python3 microtask1.py -c -u http://localhost:9200 -R https://github.com/pybee/voc.git -r idx_voc_raw -e idx_voc -o1 commiter_details_voc -o2 commit_details_voc
```
Here we first create `(-c)` indices for the repo https://github.com/pybee/comb, where `idx_comb_raw` is the name of raw_index and `idx_comb` is the name of the enriched index, and then analyse the enriched index, that is, `idx_comb`. `commiter_details_comb` is the `csv` file which stores the number of new committers per month, while `commit_details_comb` stores the number of commits made by each of the new committers. The elasticsearch instance is running on `localhost` on port `9200`

In the next example we analyse an already existing enriched index `git_voc`, an index made by ana;sing https://github.com/pybee/voc:
```
python3 microtask1.py -u http://localhost:9200 -e git_voc -o1 commiter_details_voc -o2 commit_details_voc
```

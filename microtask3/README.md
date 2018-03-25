# CHAOSS-MICROTASK 3
The goal of this project is to produce a listing of a couple of GitHub repositories as table and `csv`, having number of commits, number of issues and number of pull requests, ordered by the total number, that is, number of commits + issues + pull requests.

## Getting started
Follow the below instructions to get the code running on your local system. For this project, we mainly need `python3` and `elasticsearch`, `json`, `grimoirelab`,`pandas` packages installed.

### Pre-requisites
Install all the support systems needed, by following:
https://grimoirelab.gitbooks.io/tutorial/before-you-start/supporting-systems.html
Follow this link to install `grimoirelab`:
https://grimoirelab.gitbooks.io/tutorial/before-you-start/installing-grimoirelab.html
### Installing
Get a copy of the code:
``` git clone https://github.com/Deepayan-Ghosh/CHAOSS_Microtasks.git```

Change directory using:
```cd microtasks/microtask3```

Make the python script `microtask3.py` executable by running the command:
```chmod a+x microtask3.py ```

Then run the script as:
```./microtask3.py -h```

You can also run the script by calling `python3` every time like:
```python3 microtask3.py -h```

## Detailed Explanation
The script takes as input the `url` of a elasticsearch instance, GitHub token of the user using the `-t` argument and the name of output file (`-o`) where the listing is to be written. These arguments are compulsory.

Apart from these, there are two other options `-c` and `-i`. `-c` enables create mode and the user provides the repo-names, their urls and corresponding index names which are to be analysed to get the final listing. The indices with their names obtained from the user, are first created and then analysed. In `-i` mode the user provides the repo-names and already existing index names which he or she wants to analyse.

In both cases the repository names and index information are provided in the form of JSON files which the python script parses.

### Format of JSON file for `-c` option
```
{ 
	"<owner_org_name>": {
			"<repo-name1>": {
					"url":"<repo1-url>",
					#OPTIONAL FIELDS
					"git_raw":"<raw-git-index-name>",
					"github_raw": "<raw-github-index-name>",
					"git_enrich": "<enrich-git-index-name>",
					"github_enrich": "<enrich-github-index-name>"
				},
			"<repo-name2>": {
					"url":"<repo2-url>",
					
				},				
	},
	...........................
}
```
The `owner-org-name`,`repo-name`s and `url` are compulsory fields while the rest are optional. Optional in the sense that if they are not provided the program produces the names by itself in the following formats:
For raw indices:
```
"git_raw" index name for a repo: "git_" + repo_name + "_raw"
"github_raw" index name for a repo: "github_" + repo_name + "_raw"
```
For enrich indices:
```
"git_enrich" index name for a repo: "git_" + repo_name
"github_enrich" index name for a repo: "github_" + repo_name
```

### Format of JSON file for `-i` option
```
{
	"<repo-name>": {
					"git_raw":"<raw-git-index-name>",
					"github_raw": "<raw-github-index-name>",
					"git_enrich": "<enrich-git-index-name>",
					"github_enrich": "<enrich-github-index-name>"
				},
 ................................................
}
```
Here providing the index names are mandatory.
## Options
Command line arguments allow users to input the name of indices, `csv` file, etc. You can get a list of all command line options using `-h` as:
```
$ ./microtask3.py -h 
OR
$ python3 microtask3.py -h
usage: microtask3.py [-h] -u URL -t TOKEN -o OUT_FILE
                     [-c CREATE_FILE | -i INDEX_FILE]

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     URL of elasticsearch instance
  -t TOKEN, --token TOKEN
                        User-token of github user
  -o OUT_FILE, --out_file OUT_FILE
                        Output filename
  -c CREATE_FILE, --create_file CREATE_FILE
                        JSON file containing repo details
  -i INDEX_FILE, --index_file INDEX_FILE
                        JSON file containing names of indices to query
```
where `-u`,`-t` and `-o` are mandatory as they represent URL, GitHub token of user, and name of `csv` file, that the user wants. If the user wants to both create and analyse the indices, then `-c`option with JSON filename containing repo details is needed, while for `-i` option JSON filename containing index-name details is needed.

## Examples
Here there are two examples: how to run, content of json file and output.
### Example1
```
./query3.py -c repos.json -u http://localhost:9200 -t XXX -o out.csv
```
Here we first create `(-c)` indices for the repo's contained in `repos.json` file, and analyse them to create the listing. User must replace `XXX` with his/her valid token. `-o` specifies the filename of output csv file. Here it is `out`.
### Content of `repos.json`
```
{ 
	"pybee": {
			"voc": {
					"url":"https://github.com/pybee/voc.git"
				},
			"cricket": {
					"url":"https://github.com/pybee/cricket.git"
				},
			"toga": {
					"url":"https://github.com/pybee/toga.git"
				}
	},
	"chaoss": {
			"grimoirelab-elk": {
					"url":"https://github.com/chaoss/grimoirelab-elk.git"
				},
			"grimoirelab-manuscripts": {
					"url":"https://github.com/chaoss/grimoirelab-manuscripts.git"
				},
			"grimoirelab-perceval": {
					"url":"https://github.com/chaoss/grimoirelab-perceval.git"
				}
	},
	"xbmc": {
			"repo-plugins": {
					"url": "https://github.com/xbmc/repo-plugins.git",
					"git_raw":"git_raw_repo-plugins",
					"github_raw": "github_raw_repo-plugins",
					"git_enrich": "git_en_repo-plugins",
					"github_enrich": "github_en_repo-plugins"
				}
	}
}
```
### Tabular output
```
                      Name  Commits  Pull Requests  Issues  Total
0             repo-plugins      214            176       6    396
1                     toga      278             71      34    383
2     grimoirelab-perceval      272             79      21    372
3          grimoirelab-elk      218             89      18    325
4                      voc       86             43      12    141
5  grimoirelab-manuscripts        6             11      10     27
6                  cricket        6              1       2      9
```

### Example2
In the next example we analyse already existing indexes mentioned in `index.json` file and the corresponding repository names:
```
./query3.py -i index.json -u http://localhost:9200 -t XXX -o file.csv
```

### Content of `index.json`
```
{ 
	"voc": {
			"git_enrich":"git_voc",
			"github_enrich":"github_voc"
	},
	"toga": {
			"git_enrich":"git_toga",
			"github_enrich":"github_toga"
	},
	"cricket": {
			"git_enrich":"git_cricket",
			"github_enrich":"github_cricket"
	},
	"grimoirelab-elk": {
			"git_enrich":"git_grimoirelab-elk",
			"github_enrich":"github_grimoirelab-elk"
	},
	"grimoirelab-manuscripts": {
			"git_enrich":"git_grimoirelab-manuscripts",
			"github_enrich":"github_grimoirelab-manuscripts"
	},
	"xbmc": {
			"git_enrich": "git_en_repo-plugins",
			"github_enrich": "github_en_repo-plugins"
	}
}
```
### Tabular output
In table format:
```
                      Name  Commits  Pull Requests  Issues  Total
0                     xbmc      214            176       6    396
1                     toga      278             71      34    383
2          grimoirelab-elk      218             89      18    325
3                      voc       86             43      12    141
4  grimoirelab-manuscripts        6             11      10     27
5                  cricket        6              1       2      9

```

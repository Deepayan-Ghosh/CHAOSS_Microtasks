#!/usr/bin/env python3
import elasticsearch as ES
from elasticsearch_dsl import Search
from dateutil.relativedelta import relativedelta
import datetime
import subprocess
import pandas as pd
import json
import argparse


# utility function: parses JSON dict REPOS to produce
# a list of tuples of the form (repo name, git index name, github index name)
def get_index_names(REPOS):
    repos, git_names, github_names = [], [], []
    for name in REPOS.keys():
        repos += [name]
        git_names += [get_git_index_name(REPOS, name)[1]]
        github_names += [get_github_index_name(REPOS, name)[1]]
    return zip(repos, git_names, github_names)


# if git index name is not provided by user
# this func produces git index names from repo names
# return raw index name, enrich index name for git
def get_git_index_name(REPOS, name):
    if 'git_raw' not in REPOS[name]:
        REPOS[name].update({'git_raw': ' git_' + name + '_raw'})
    if 'git_enrich' not in REPOS[name]:
        REPOS[name].update({'git_enrich': 'git_' + name})
    return REPOS[name]['git_raw'], REPOS[name]['git_enrich']


# if github index name is not provided by user
# this func produces github index names from repo names
# return raw index name, enrich index name for github
def get_github_index_name(REPOS, name):
    if 'github_raw' not in REPOS[name]:
        REPOS[name].update({'github_raw': ' github_' + name + '_raw'})
    if 'github_enrich' not in REPOS[name]:
        REPOS[name].update({'github_enrich': 'github_' + name})
    return REPOS[name]['github_raw'], REPOS[name]['github_enrich']


# parses the input JSON file with repo details
def read_input(filename):
    OWNERS, REPOS, data = [], {}, {}
    try:
        data = json.load(open(filename))
    except ValueError as e:
        print("Error: Decoding failed\n\t\
               JSON is expected, but got ."+filename.split('.')[-1])
        print(e)

    for each in data.keys():
        OWNERS += ([each] * len(data[each]))
        REPOS.update(data[each])
    return OWNERS, REPOS


# parses the input JSON file with details about
# which enriched indices to analyse
def read_index_json(filename):
    repos, git_names, github_names = [], [], []
    data = {}
    try:
        data = json.load(open(filename))
    except ValueError as e:
        print("Error: Decoding failed\n\t\
               JSON is expected, but got ."+filename.split('.')[-1])
        print(e)

    # foreach repo name in the json file
    for each in data.keys():
        repos += [each]
        git_names += [data[each]['git_enrich']]
        github_names += [data[each]['github_enrich']]
    return zip(repos, git_names, github_names)


# function to create indices for all repos in JSON dict
def create_index(OWNERS, REPOS, URL, user_token):
    for name, owner in zip(REPOS.keys(), OWNERS):
        raw_name, rich_name = get_git_index_name(REPOS, name)
        subprocess.run(['p2o.py --enrich --index ' + raw_name +
                        ' --index-enrich ' + rich_name +
                        ' -e ' + URL + ' --no_inc --debug git ' +
                        REPOS[name]['url']], shell=True)

        raw_name, rich_name = get_github_index_name(REPOS, name)
        subprocess.run(['p2o.py --enrich --index ' + raw_name +
                        ' --index-enrich ' + rich_name + ' -e ' + URL +
                        ' --no_inc --debug github ' + owner + ' ' +
                        name + ' -t ' + user_token], shell=True)


# queries elasticsearch using elasticsearch_dsl for filtering results
# git indices are queried for commit count while github for PRs, issues
def get_info_from_index(URL, repo_index_names):
    commit_count, issue_count, pr_count = 0, 0, 0
    result = []
    TODAY = datetime.date.today()
    # DATE_THRESHOLD is the date three months ago from today
    DATE_THRESHOLD = TODAY - relativedelta(months=3)

    for name, i, j in repo_index_names:
        commit_count, issue_count, pr_count = 0, 0, 0
        rich_name_git = i
        rich_name_github = j

        es = ES.Elasticsearch([URL])
        # querying git index for commit count
        # filtering by DATE_THRESHOLD: all activities in last three months
        query_request = Search(using=es, index=rich_name_github)
        query_request = query_request.filter(
                            'range',
                            author_date={'gt': DATE_THRESHOLD}
                        )
        commit_count += query_request.count()

        # querying github index for PRs, issues
        query_request = Search(using=es, index=rich_name_github)
        query_request = query_request.filter(
                            'range',
                            created_at={'gt': DATE_THRESHOLD}
                        )
        query_response = query_request.scan()
        for item in query_response:
            if item.pull_request:
                pr_count += 1
            else:
                issue_count += 1
        total = commit_count + pr_count + issue_count
        result.append([name, commit_count, pr_count, issue_count, total])

    # sort descending by total count
    result.sort(key=lambda x: x[4], reverse=True)
    return result


def table_to_csv(query_result, filename):
    df = pd.DataFrame(query_result, columns=['Name', 'Commits',
                                       'Pull Requests', 'Issues', 'Total'])
    print(df)
    df.to_csv(filename, index=False)


# parses the arguments passed
def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url',
                        help='URL of elasticsearch instance', required=True)
    parser.add_argument('-t', '--token',
                        help='User-token of github user', required=True)
    parser.add_argument('-o', '--out_file',
                        help='Output filename', required=True)

    # mutually exclusive arguments:
    # either both create and analyse indices in JSON format [-c,--create_file]
    # or, only analyse indices in JSON format [-i, --index_file]
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--create_file',
                       help='JSON file containing repo details')
    group.add_argument('-i', '--index_file',
                       help='JSON file containing names of indices to query')

    args = parser.parse_args()

    URL, user_token, out_file = args.url, args.token, args.out_file
    repo_index_names = []

    # perform specific functions based on create mode or analyse mode
    if args.create_file:
        filename = args.create_file
        OWNERS, REPOS = read_input(filename)
        create_index(OWNERS, REPOS, URL, user_token)
        repo_index_names = get_index_names(REPOS)
    elif args.index_file:
        filename = args.index_file
        repo_index_names = read_index_json(filename)
    else:
        print("Error: [-c/--create | -i/--index] \
               at least one argument expected")
        exit(0)

    query_result = get_info_from_index(URL, repo_index_names)
    table_to_csv(query_result, out_file)

if __name__ == "__main__":
    Main()

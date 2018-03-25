#!/usr/bin/env python3
import elasticsearch as ES
import datetime
import subprocess
import argparse
from collections import OrderedDict
import pandas as pd


# function to create the enriched index using p2o.py
def create_index(URL, REPO, raw_index_name, enrich_index_name):
    subprocess.run(['p2o.py --enrich --index ' + raw_index_name +
                    ' --index-enrich ' + enrich_index_name + ' -e ' + URL +
                    ' --no_inc --debug git ' + REPO], shell=True)


# query the enriched index in elasticsearch for relevant information
def get_info_from_index(URL, enrich_index_name):
    es = ES.Elasticsearch([URL])
    query_result = es.search(index=enrich_index_name)
    # query to obtain only commiter name and date from all docs.
    # Also sort the retrieved values according to date
    # (this facilitates maintaining order in OrderedDict)
    query = {
                    "size": query_result['hits']['total'],
                    "_source": ["commit_date", "author_name"],
                    "sort": ["commit_date"]
        }
    query_result = es.search(index=enrich_index_name, body=query)
    return query_result


# Given the query results,
# here, we consume those results to find the new committers per month
#       and, the commits made by them
def find_commiter_per_month(query_result):
    # set to maintain names of all commiters
    # used to check whether committer is new or old
    all_commiters = set()
    final_report_dict = OrderedDict()

    for each in query_result['hits']['hits']:
        commiter = each['_source']['author_name']
        date = each['_source']['commit_date']

        # extract month from date-info of format "%Y-%m-%dT%H:%M:%S"
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        month_entry = date.strftime("%B") + "-" + str(date.year)

        # final dict is of form:
        #    {
        #        <month1>: {
        #                    new_commiter_count: <count>,
        #                    <commiter_name>:    <number of commits>
        #                },
        #        <month2>: {.......}
        #        ...................................................
        #    }
        if month_entry in final_report_dict:
            if commiter not in all_commiters:
                final_report_dict[month_entry]['new_committer_count'] += 1
                final_report_dict[month_entry][commiter] = 1
            else:
                if commiter in final_report_dict[month_entry]:
                    final_report_dict[month_entry][commiter] += 1
        else:
            final_report_dict[month_entry] = {'new_committer_count': 0}
            if commiter not in all_commiters:
                final_report_dict[month_entry][commiter] = 1
                final_report_dict[month_entry]['new_committer_count'] += 1
        all_commiters.add(commiter)

    return final_report_dict


# convert the data in final dictionary into panda dataframes
def create_tables_from_report(report, filename1, filename2):
    # items1 is a dict representing the first table
    # showing number of committers per month
    # items2 represents second table as a list of lists(rows)
    items1, items2 = {}, []

    for month in report.keys():
        if report[month]['new_committer_count'] != 0:
            items1[month] = report[month]['new_committer_count']
            for k in report[month].keys():
                # hold stores each row
                hold = []
                if k != 'new_committer_count':
                    hold.extend([month, k, report[month][k]])
                    items2.append(hold)

    table1 = pd.DataFrame(list(items1.items()),
                          columns=['Month', 'Number of new commiters'])
    table2 = pd.DataFrame(items2,
                          columns=['Month', 'Author', 'Number of commits'])

    # print the tables
    print(table1)
    print(table2)

    # write the tables to csv files
    table1.to_csv(filename1 + '.csv', index=False)
    table2.to_csv(filename2 + '.csv', index=False)


# parses the arguments passed
def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url',
                        help='URL of elasticsearch instance', required=True)
    parser.add_argument('-R', '--repo',
                        help='Name of git repo')
    parser.add_argument('-r', '--raw',
                        help='Name of raw index to be used or created')
    parser.add_argument('-e', '--enrich',
                        help='Name of enirched index to be used or created',
                        required=True)
    parser.add_argument('-c', '--create', help='Flag, used to create indices, \
                        else only analysis is done', action='store_true')
    parser.add_argument('-o1', '--output1', help='Output filename \
                        for commiter number details', required=True)
    parser.add_argument('-o2', '--output2', help='Output filename \
                        for commit details', required=True)
    args = parser.parse_args()

    URL, REPO = args.url, ''
    enrich_index_name, raw_index_name = args.enrich, ''

    # if in --create mode, obtain raw index name, repo name
    # which are otherwise optional
    if args.create:
        if args.raw:
            raw_index_name = args.raw
        else:
            print("Error: [-r RAW, --raw RAW] \
                   raw index name is mandatory in -c mode")
            exit(0)

        if args.repo:
            REPO = args.repo
        else:
            print("Error: [-R REPO, --repo REPO] \
                   repository name is mandatory in creation(-c) mode")
            exit(0)

        create_index(URL, REPO, raw_index_name, enrich_index_name)

    # in create mode or not, query the index, do the analysis
    # and, produce the reports as csv files
    res = get_info_from_index(URL, enrich_index_name)
    report = find_commiter_per_month(res)
    create_tables_from_report(report, args.output1, args.output2)


if __name__ == "__main__":
    Main()

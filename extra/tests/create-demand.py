#!/home/mkapel/gitrepo/noosDrift/venv//bin/python

# !/..../gitrepo/noosDrift/venv//bin/python
# !/usr/bin/python3
# The Python above may not be adequate for you but make sur you are using a python3 environment
# with the coreapi library available

import argparse
import coreapi
import json
import os
import sys
import re

from datetime import datetime as dt

# PARAMETERS
# hostname = "https://odnature.naturalsciences.be/noosdrift/api/schema/core.json"
hostname = "http://localhost:8000/schema/core.json"
result = None

# GET SCHEMA
client = coreapi.Client()
# print("Getting schema from : {}".format(hostname))
schema = client.get(url=hostname)

# print(schema)

# GET TOKEN
# print("Getting token")
action = ['api-token-auth', 'create']

usage_txt = "%(prog)s -u, --user username -p, --password password -f jsonfile | -d filesdir | -F fileslist "
description_txt = 'Create a Simulation demand on the NOOSDRIFT system'
my_parser = argparse.ArgumentParser(prog="create-demand.py", usage=usage_txt, description=description_txt)

userarg = 'user'
passwordarg = 'password'
filearg = 'jsonfile'
dirarg = 'dirfiles'
filelistarg = 'files'
my_parser.add_argument('-u', '--{}'.format(userarg), help='NOOSDRIFT User')
my_parser.add_argument('-p', '--{}'.format(passwordarg), help='NOOSDRIFT User password')
my_parser.add_argument('-f', '--{}'.format(filearg), action='store', help='Path to JSON file used for the demand')
my_parser.add_argument('-F', '--{}'.format(filelistarg), action='store',
                       help='Path to a file containing a list of jsonfiles to process')
my_parser.add_argument('-d', '--{}'.format(dirarg), action='store',
                       help='Path to a directory containing a list of jsonfiles to process')

args = my_parser.parse_args()

vargs = vars(args)
# print("vargs : {}".format(vargs))

env_user = vargs[userarg]
env_pwd = vargs[passwordarg]

if not env_user:
    try:
        env_user = os.environ["NOOS_USER"]
    except KeyError as kerr:
        print("Error, User must either be passed with -u, --user or exist as NOOS_USER")
        sys.exit(-1)

if not env_pwd:
    try:
        env_pwd = os.environ["NOOS_PWD"]
    except KeyError as kerr:
        print("Error, User password must either be passed with -p, --password or exist as NOOS_PWD")
        sys.exit(-1)

if filearg not in vargs and filelistarg not in vargs and dirarg not in vargs:
    print("Error One of the options -f, -F, -d is required")
    sys.exit(-1)

count_options = 0
if filearg in vargs and vargs[filearg] is not None:
    count_options = count_options + 1

if filelistarg in vargs and vargs[filelistarg] is not None:
    count_options = count_options + 1

if dirarg in vargs and vargs[dirarg] is not None:
    count_options = count_options + 1

if count_options > 1:
    print("Error, ONLY One of the options -f, -F, -d is allowed")
    sys.exit(-1)

list_of_files = []

if filearg in vargs and vargs[filearg] is not None:
    json_file = vargs[filearg]
    # print('Found option for one file : {}'.format(json_file))
    list_of_files.append(json_file)
elif filelistarg in vargs and vargs[filelistarg] is not None:
    given_list_of_files = vargs[filelistarg]
    if not os.path.exists(given_list_of_files) or not os.path.isfile(given_list_of_files):
        print('PathError, |{}|, does not exist or is not a file'.format(given_list_of_files))
        sys.exit(-1)
    else:
        file_path_pat = re.compile('\\.json$')
        with open(given_list_of_files) as file:
            for a_file_path in file:
                if a_file_path is not '\n':
                    the_file_path = a_file_path[:-1]
                    if re.match(file_path_pat, the_file_path) and os.path.exists(the_file_path) and \
                            os.path.isfile(the_file_path):
                        list_of_files.append(a_file_path[:-1])

        # print('List of files : {}'.format(list_of_files))
elif dirarg in vargs and vargs[dirarg] is not None:
    files_dir = vargs[dirarg]
    file_path_pat = re.compile('\\.json$')
    for r, d, f in os.walk(files_dir):
        for file in f:
            for a_file_path in file:
                if a_file_path is not '\n':
                    the_file_path = a_file_path[:-1]
                    if re.match(file_path_pat, the_file_path) and os.path.exists(the_file_path) and \
                            os.path.isfile(the_file_path):
                        list_of_files.append(a_file_path[:-1])

params = {'username': env_user, 'password': env_pwd}
try:
    result = client.action(schema, action, params)
    # print('Got Token')
except coreapi.exceptions.CoreAPIException as error:
    print(error)
del action
del params

auth = coreapi.auth.TokenAuthentication(scheme='JWT', token=result['token'])
client = coreapi.Client(auth=auth)
# print("Authenticated token {}".format(result))
del auth

schema = client.get(url=hostname)
# print("Updating schema")
# print(schema)

# SEND REQUEST TO NODE
action = ['simulationdemands', 'create']
# Note : In python, booleans MUST use a first uppercase letter (True, False)
#        To be a valid JSON, booleans MUST be 100% lowercase (true, false)

for a_file in list_of_files:
    if not os.path.exists(a_file) or not os.path.isfile(a_file):
        print('PathError, |{}|, does not exist or is not a file'.format(a_file))
    else:
        try:
            params = {'json_txt': json.load(open(a_file))}
            result = client.action(schema, action, params)
            print('Successfully Send Request')
            # print('{}'.format(result))
            a_time = dt.strptime(result['created_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
            f_time = a_time.strftime("%Y%m%d-%H%M")
            # print("New Demand id is : {}".format(result['id']))
            archive_url = "https://odnature.naturalsciences.be/noosdrift/api/media/simulation-{}-{}.zip".format(
                result['id'], f_time)
            print("DDATAURL={}".format(archive_url))
            w_msg = "!!!!!DATA IS NOT READY YET.!!!!!\nWAIT UNTIL YOU GET A MAIL OR YOU CAN SEE IT ON THE WEB PAGES"
            print("{}".format(w_msg))
        except coreapi.exceptions.CoreAPIException as error:
            print('COREAPIError, for file {}'.format(a_file))
            print(error)
        except json.decoder.JSONDecodeError as jserror:
            print('JSONError, for file {}'.format(a_file))
            print(jserror)

del schema
del result
del client

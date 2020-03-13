#!/home/mkapel/gitrepo/noosDrift/venv/bin/python3

## !/usr/bin/python3
# The Python above may not be adequate for you but make sur you are using a python3 environment
# with the coreapi library available
# #!/somePythonVirtualEnvironment/bin/python3

import argparse
import os
import re
import shutil
import sys
from urllib import request

usage_txt = "%(prog)s ziplist"
description_txt = 'Download results from NOOSDRIFT system'
my_parser = argparse.ArgumentParser(prog="check-demands.py", usage=usage_txt, description=description_txt)

my_parser.add_argument('zip_list',
                       metavar='zip_list',
                       type=str,
                       help='the path zip list')

args = my_parser.parse_args()

zip_list = args.zip_list

if not os.path.isdir(zip_list) or not os.path.isfile(zip_list):
    print('File {} does not exist'.format(zip_list))
    sys.exit(-1)

url_line_pat = re.compile("^DDATAURL=(.*)")
zip_file_pat = re.compile("^.*(simulation-.*\\.zip)$")

with open(zip_list) as create_answer:
    for line in create_answer.readlines():
        the_line = line[:-1]
        url_line_match = re.match(url_line_pat, the_line)
        if url_line_match is not None:
            the_url = url_line_match.group(1)
            zip_file_match = re.match(zip_file_pat, the_url)
            zip_name = zip_file_match.group(1)
            new_zip = open(zip_name, 'wb')
            with request.urlopen(the_url) as response:
                shutil.copyfileobj(response, new_zip)

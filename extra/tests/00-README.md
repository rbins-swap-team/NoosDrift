# Create demands using a python script

## Intro
Files to submit demands automatically using the REST API.
Demands are described with files that use a specific JSON structure.
If the structure is not followed or the data is garbled the REST services will respond with an error.   

## Prerequisites
A proper python virtual environement.
Make sure you change the first line of the script to call for the python executable linked to your environment  

## The script and the options

The command to use is 
 * create-demand.py

It has a number of options

Option
 * -u allows you to specify the user name
 * -p allows you to specify the user password
 * -f specifies one unique json file to process
 * -F specifies a txt file containing a list of json file paths to process. Each path is on a separate line.
 * -d specifies a directory where all the json files to process are kept

Instead of using -u,-p you can store the user and password values in environment variables 
 * NOOS_USER 
 * NOOS_PWD
 
This code does take for granted python will be able to find both json AND coreapi 
modules in it's environment

The result of calling create_demand.py is better stored in a file like so
```
./create-demand.py -f ./WhateverRequestFile.json >> TheAnswer.txt
```

This will allow automatic download of processed demands data by the check-demands.py script like so

```
./check-demands.py zip_list ./TheAnswer.txt
```

Where ./TheAnswer.txt is the file just created with the preceding command 
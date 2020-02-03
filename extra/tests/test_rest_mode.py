import coreapi
import json

# PARAMETERS
user = {"username": "theUserName", "pwd": "thePwd"}
datafile = './extra/tests/request-144.json'
# hostname = 'http://pagurus.rbins.be/noosdrift/api/schema/core.json'
hostname = "https://odnature.naturalsciences.be/noosdrift/api/schema/core.json"
result = None

# GET SCHEMA
client = coreapi.Client()
print("Getting schema from : {}".format(hostname))
# generator = schemas.SchemaGenerator(url=hostname)
# aschema = generator.get_schema()
schema = client.get(url=hostname)

print(schema)

# GET TOKEN
print("Getting token")
action = ['api-token-auth', 'create']
params = {'username': user['username'], 'password': user['pwd']}
try:
    result = client.action(schema, action, params)
    print('Successfully Get Token')
except coreapi.exceptions.CoreAPIException as error:
    print(error)
del action
del params

# UPDATE CLIENT WITH TOKEN
auth = coreapi.auth.TokenAuthentication(scheme='JWT', token=result['token'])
# client = coreapi.Client(auth=auth, decoders=decoders)
client = coreapi.Client(auth=auth)
print("New token {}".format(result))
del auth

# UPDATE SCHEMA WITH TOKEN
schema = client.get(url=hostname)
print("Upadating schema")
print(schema)

# SEND REQUEST TO NODE
# action = ['requests', 'create']
action = ['simulationdemands', 'create']
# Note : In python, booleans MUST use a first uppercase letter (True, False)
#        To be a valid JSON, booleans MUST be 100% lowercase (true, false)
params = {'json_txt': json.load(open(datafile))}
try:
    result = client.action(schema, action, params)
    print('Successfully Send Request')
except coreapi.exceptions.CoreAPIException as error:
    print('SEND REQUEST - coreapi error')
    print(error)
del action
del params

del schema
del result
del client
del user

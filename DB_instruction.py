import os
import bson
from pprint import pprint
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Import the `pprint` function to print nested data:


uri = os.environ['uri']
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Get Character_1 database:
db = client['Character_1']
# Get Long_term_memo collection:
long_memo = db['Long_term_memo']
# Get the document with the DOB '8.20':
pprint(long_memo.find_one({'DOB': '8.20'}))

# Creat a document for the movie 'Parasite':
insert_result = long_memo.insert_one({
      "DOB": "01.01",
      "Name": "person_1",
   })
# Save the id of the document you just created:
id = insert_result.inserted_id
print("_id of inserted document: {id}".format(id=id))
print(long_memo.find_one({'_id': bson.ObjectId(id)}))

# Update the document with the correct year:
update_result = long_memo.update_one({ '_id': id }, {
   '$set': {"DOB": "02.02"}
})
# Print out the updated record to make sure it's correct:
pprint(long_memo.find_one({'_id': bson.ObjectId(id)}))

long_memo.delete_many(
   {"Name": "person_1",}
)

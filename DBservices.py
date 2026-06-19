
from pymongo import MongoClient
from structure import mem
#from bson.objectid import ObjectId

client = MongoClient("mongodb://localhost:27017")##making connection
db = client["echatbot"]
msgs_collection = db["messages"]##like SQl table
msgs_collection.create_index("Cid")
### memory checkpoints storing in DB
## functions to store in DBs called by API endpoints
def store_msg(ci:str,r:str,c:str):
    res = msgs_collection.insert_one({"Cid":ci, "role": r, "content": c})
    return{
       "new msg added for chat id: ": str(res.inserted_id)
    } 

def get_convoHistory(cid):
    msg_list = []
    for m in msgs_collection.find({"Cid":cid}):
        msg_list.append({
            "role": m["role"],
            "content": m["content"]
        })
        
    return  msg_list

def delete_convo(cid):
    res = msgs_collection.delete_one(
        {"_id":cid},
    )
    
    return{
        "chat deleted successfully "
    }
    
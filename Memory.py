import os
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from datetime import datetime

#Initialize embedding model
api_key= os.environ['api_key']
base_url= "https://api.ai.it.cornell.edu"
embedding_client = openai.OpenAI(
    api_key=api_key,
    base_url=base_url
)

def save_conversation_to_mongodb(db, user_name, character_name, messages):
    Short_term = db['Short_term_memo']
    
    # Only get the newest message
    latest_message = messages[-1] if messages else None
    
    if latest_message:
        # 使用 user_name 和 character_name 作为唯一标识
        filter_query = {
            "user_name": user_name,
            "character_name": character_name
        }
        
        # 更新数据，使用 $push 追加新消息，同时更新时间戳
        update_data = {
            "$push": {"messages": latest_message},
            "$set": {"last_updated": datetime.now()},
            "$setOnInsert": {
                "user_name": user_name,
                "character_name": character_name
            }
        }
        
        # 更新或插入对话记录
        Short_term.update_one(
            filter_query,
            update_data,
            upsert=True
        )

#Generates vector embeddings for the given data.
def get_embedding(data):
    response = embedding_client.embeddings.create(
        model="openai.text-embedding-3-small",
        input=data
    )    
    return response.data[0].embedding

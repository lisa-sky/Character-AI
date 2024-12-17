from datetime import datetime
from typing import Dict

def extract_personal_info(message: str, chat_client) -> bool:
    """
    Use a simple prompt-based approach to determine if a message contains important personal information.
    """
    
    relevance_check = f"""
    Is the following message sharing any personal information or significant details about the speaker? 
    Consider things like:
    - Personal details (name, age, location, etc.)
    - Recent plans or events
    - Life experiences or events
    - Preferences, likes, or dislikes
    - Relationships or family
    - Work or education
    - Goals or aspirations
    - Feelings or emotions
    - Health information
    - Any other meaningful personal sharing
    Make sure to include relevant information only.

    Message: "{message}"

    Answer with just 'yes' or 'no'.
    """
    
    try:
        response = chat_client.chat.completions.create(
            model="openai.gpt-4o",
            messages=[{"role": "user", "content": relevance_check}],
            temperature=0,
            max_tokens=5
        )
        
        answer = response.choices[0].message.content.strip().lower()
        return answer == 'yes'
        
    except Exception as e:
        print(f"Error in relevance check: {str(e)}")
        # If there's an error, we'll be conservative and store the message
        return True

def save_to_long_term_memory(db, user_name: str, character_name: str, message: Dict, chat_client):
    """
    Store important information in long-term memory.
    """
    try: 
        Long_term = db['Long_term_memo']
    
        # Check if the message contains important information
        is_important = extract_personal_info(message['content'], chat_client)
        print(f"Is message important? {is_important}")
        
        if not is_important:
            print("❌ Skipping: not important information")
            return
        
        print("✓ Message contains important information")
        
        filter_query = {
            "user_name": user_name,
            "character_name": character_name
        }
            
        update_data = {
            "$push": {"messages": message['content']},
            "$set": {"last_updated": datetime.now()},
            "$setOnInsert": {
                "user_name": user_name,
                "character_name": character_name
            }
        }
            
        Long_term.update_one(
            filter_query,
            update_data,
            upsert=True
        )
        
    except Exception as e:
        raise

def get_relevant_memories(db, user_name: str, character_name: str) -> str:
    """
    Retrieve all memories for a user-character pair.
    """
    try:
        Long_term = db['Long_term_memo']
        
        # Get all memories for this user and character
        filter_query = {
            "user_name": user_name,
            "character_name": character_name
        }
        
        memories = list(Long_term.find(filter_query).sort("timestamp", -1))
        
        # Format memories as a string
        memory_text = []
        for memory in memories:
            if isinstance(memory.get('messages'), list):
                for msg in memory['messages']:
                    # Only process user messages or messages without a role (direct content)
                    if isinstance(msg, dict):
                        if msg.get('role') == 'user':
                            content = msg['content'].strip()
                            memory_text.append(f"User mentioned: {content}")
                    elif isinstance(msg, str) and not msg.startswith('[') and '*[Emotion:' not in msg:
                        # This catches direct string messages that aren't emotion tags or action brackets
                        content = msg.strip()
                        memory_text.append(f"User mentioned: {content}")
            
            elif isinstance(memory.get('content'), str):
                content = memory['content'].strip()
                if not content.startswith('[') and '*[Emotion:' not in content:
                    memory_text.append(f"User mentioned: {content}")
        
        if not memory_text:
            return "No previous information available."
        
        # Take up to 5 most recent memories (if available)
        relevant_memories = memory_text[:5] if len(memory_text) > 5 else memory_text
        print(f"Number of relevant memories found: {len(relevant_memories)}")
        
        result = "\n".join(relevant_memories)
        print(f"Cleaned and formatted memories:\n{result}")
        return result
        
    except Exception as e:
        print(f"Error retrieving memories: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return "Error retrieving previous information."

def save_conversation_to_mongodb(db, user_name, character_name, messages, chat_client):
    """
    Save conversation to both short-term and long-term memory.
    """
    try:
        Short_term = db['Short_term_memo']
        
        # Only get the user message
        latest_message = messages[-2] if messages else None
        
        if latest_message:            
            # Store in short-term memory
            filter_query = {
                "user_name": user_name,
                "character_name": character_name
            }
            
            update_data = {
                "$push": {"messages": latest_message},
                "$set": {"last_updated": datetime.now()},
                "$setOnInsert": {
                    "user_name": user_name,
                    "character_name": character_name
                }
            }
            
            Short_term.update_one(
                filter_query,
                update_data,
                upsert=True
            )
            
            # Check and store in long-term memory if important
            save_to_long_term_memory(db, user_name, character_name, latest_message, chat_client)
            
    except Exception as e:
        print(f"Error saving conversation: {str(e)}")
        raise

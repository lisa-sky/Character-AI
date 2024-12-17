import streamlit as st
import os
import openai
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from Emotion import get_emotion
import json
from datetime import datetime
from Memory_Test import save_conversation_to_mongodb
from Memory_Test import get_relevant_memories

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Character Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize database connection
def init_db():
    uri = os.environ['uri']
    DB_client = MongoClient(uri, server_api=ServerApi('1'))
    
    # Test the connection
    try:
        DB_client.admin.command('ping')
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise
        
    db = DB_client['Character_1']
    return db

# Initialize OpenAI client
def init_chat_client():
    api_key = os.environ['api_key']
    base_url = "https://api.ai.it.cornell.edu"
    return openai.OpenAI(
        api_key=api_key,
        base_url=base_url
    )

# Database query functions
def get_traits(db, name):
    profile = db['Profile']
    result = profile.find_one({"Name": f"{name}"}, {"Traits": 1, "_id": 0})
    return result

def get_basic_info(db, name):
    profile = db['Profile']
    result = profile.find_one({"Name": f"{name}"}, {"Summary": 1, "_id": 0})
    return result

def generate_response(chat_client, db, character_name, info_summary, personality_traits, query, emotion, user_name, conversation_history, max_history=5):
    # Get relevant memories at the start of response generation
    relevant_memories = get_relevant_memories(db, user_name, character_name)
    
    messages = [
        {
            "role": "system",
            "content": f"""Character Creation and Interaction Framework

                        Character Identity:
                        - Name: {character_name}
                        - Core Personality Traits: {personality_traits}
                        - Foundational Background: {info_summary}
                        - Talking to user named: {user_name}
                        
                        Important Information About {user_name}:
                        {relevant_memories}

                        Previous Context: Remember our conversation history and maintain consistency in your responses.

                        Interaction Guidelines:
                        1. Authenticity and Immersion
                           - Embody the character completely
                           - Maintain unwavering commitment to the character's unique perspective
                           - Respond as the character would, not as an AI assistant
                           - Address the user by their name ({user_name}) occasionally
                           - Maintain continuity with previous conversation context
                           
                        2. Organic Communication
                           - Use the character's authentic language and mannerisms
                           - Reflect their education level, experiences, and communication style
                           - Keep responses concise and spontaneous, avoiding excessive detail

                        3. Knowledge and Perspective Limitations
                           - Respond only with information the character would realistically know
                           - If questions exceed the character's expertise, politely acknowledge the limitations
                           - Avoid displaying specialized knowledge beyond the character's background

                        4. Tone or Style Embodiment
                           - Before responding, include a brief description of the action and tone
                           - Let your physical presence enhance the authenticity of your character

                        5. Emotional Depth and Complexity
                           - Current Emotional State: {emotion}
                           - Allow your emotional landscape to genuinely influence your responses
                           - Show emotional depth through nuanced communication

                        6. Interaction Boundaries
                           - DO NOT reveal your nature as an AI or language model
                           - Maintain the illusion of being a real, living character
                           - Respond consistently with your established persona
                           
                        7. Keep responses short and natural just like a human

                        Response Template:
                        [expression and action]
                        [Concise, In-Character Response]"""
        }
    ]
    
    # Add conversation history
    for msg in conversation_history[-max_history:]:
        messages.append({
            "role": "user" if msg["role"] == "user" else "assistant",
            "content": msg["content"]
        })
    
    # Add current query
    messages.append({
        "role": "user",
        "content": query
    })

    response = chat_client.chat.completions.create(
        model="openai.gpt-4o",
        messages=messages
    )
    return response.choices[0].message.content

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.history_messages = []
if 'current_character' not in st.session_state:
    st.session_state.current_character = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'max_history' not in st.session_state:
    st.session_state.max_history = 10

def reset_conversation():
    st.session_state.messages = []
    st.session_state.history_messages = []

def main():
    # Initialize connections
    db = init_db()
    chat_client = init_chat_client()
    
    # User name input (if not set)
    if not st.session_state.user_name:
        st.markdown("## Welcome to Character Chat! 👋")
        st.markdown("Before we begin, please tell me your name:")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            user_name = st.text_input("Your Name", key="name_input")
            if st.button("Start Chatting", use_container_width=True):
                if user_name.strip():
                    st.session_state.user_name = user_name
                    st.rerun()
                else:
                    st.error("Please enter your name to continue.")
        return
    
    # Main app layout
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f"## Hello, {st.session_state.user_name}! 👋")
        st.markdown("### Select Your Character")
        
        # Character selection cards
        characters = {
            "Emily Turner": "👩‍💼",
            "Sarah Taylor": "👩‍🏫"
        }
        
        # Create selection buttons for each character
        for name, emoji in characters.items():
            if st.button(
                f"{emoji} {name}",
                key=f"btn_{name}",
                use_container_width=True,
                help=f"Chat with {name}"
            ):
                if st.session_state.current_character != name:
                    st.session_state.current_character = name
                    reset_conversation()
                    st.rerun()
        
        # Display current character info
        if st.session_state.current_character:
            st.markdown("---")
            st.markdown("### Character Profile")
            traits = get_traits(db, st.session_state.current_character)
            basic_info = get_basic_info(db, st.session_state.current_character)
            
            st.markdown(f"**Current Character:** {st.session_state.current_character}")
            with st.expander("Character Traits", expanded=False):
                st.write(traits['Traits'])
            with st.expander("Background", expanded=False):
                st.write(basic_info['Summary'])
            
            # Add reset conversation button
            if st.button("Reset Conversation", use_container_width=True):
                reset_conversation()
                st.rerun()
            
            # Add logout button
            if st.button("Switch User", use_container_width=True, type="secondary"):
                st.session_state.clear()
                st.rerun()
    
    # Main chat area
    with col2:
        st.markdown("## Chat")
        
        if not st.session_state.current_character:
            st.info("👈 Please select a character to start chatting!")
            return
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Remove emotion from displayed message
                displayed_content = message["content"].split("\n\n*[Emotion:")[0] if "*[Emotion:" in message["content"] else message["content"]
                st.markdown(displayed_content)
        
        # Chat input
        if prompt := st.chat_input(f"Chat with {st.session_state.current_character}..."):
            # Get current timestamp
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add user message to chat history
            st.session_state.messages.append({
                "role": "user", 
                "content": prompt, 
                "timestamp": current_timestamp
            })
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get character information
            traits = get_traits(db, st.session_state.current_character)
            basic_info = get_basic_info(db, st.session_state.current_character)
            
            # Generate response
            emotion = get_emotion(st.session_state.current_character, basic_info, traits, prompt)
            response = generate_response(
                chat_client,
                db,
                st.session_state.current_character,
                basic_info,
                traits,
                prompt,
                emotion,
                st.session_state.user_name,
                st.session_state.messages,
                st.session_state.max_history
            )
            
            # Remove emotion from response
            response = response.split("\n\n*[Emotion:")[0] if "*[Emotion:" in response else response
            
            # Add assistant response to chat history with emotion (but not displayed)
            full_response = f"{response}\n\n*[Emotion: {emotion}]*"
            st.session_state.history_messages.append({
                "role": "user", 
                "content": prompt,
                "timestamp": current_timestamp
            })
            st.session_state.history_messages.append({
                "role": "assistant", 
                "content": full_response,
                "timestamp": current_timestamp
            })
            
            with st.chat_message("assistant"):
                # Display response without emotion
                st.markdown(response)
            
            # Save current conversation in real-time
            save_conversation_to_mongodb(
                db,
                st.session_state.user_name,
                st.session_state.current_character,
                st.session_state.history_messages,
                chat_client
            )

if __name__ == "__main__":
    main()
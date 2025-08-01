from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
import os
from dotenv import load_dotenv
import uuid
import markdown
import random
import time
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure OpenAI client
try:
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY')
    )
except TypeError as e:
    if 'proxies' in str(e):
        # Handle proxy configuration issue
        import httpx
        client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            http_client=httpx.Client()
        )
    else:
        raise e

def load_avatar_config():
    """Load avatar configuration from markdown file"""
    try:
        with open('avatar_config.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        avatars = {}
        
        # Find the Avatar Settings section and only parse that
        avatar_settings_start = content.find('## Avatar Settings')
        config_notes_start = content.find('## Configuration Notes')
        
        if avatar_settings_start == -1:
            return {}
        
        # Extract only the Avatar Settings section
        if config_notes_start != -1:
            avatar_section = content[avatar_settings_start:config_notes_start]
        else:
            # If no config notes section, look for examples section
            examples_start = content.find('## Examples')
            if examples_start != -1:
                avatar_section = content[avatar_settings_start:examples_start]
            else:
                avatar_section = content[avatar_settings_start:]
        
        # Split avatar section by ### headers
        sections = re.split(r'\n### ', avatar_section)
        
        for section in sections[1:]:  # Skip the first section (title)
            lines = section.strip().split('\n')
            if not lines:
                continue
                
            # Get avatar key from header
            avatar_key = lines[0].lower().strip()
            
            # Parse configuration
            config = {
                'active': True,
                'name': avatar_key.title(),
                'prompt_file': f'prompts/{avatar_key}_prompt.md',
                'color': 'from-gray-500 to-gray-600',
                'text_color': 'text-gray-300',
                'icon': 'fas fa-robot',
                'allow_followups': True,
                'speaker_order': 999  # Default to high number for unspecified order
            }
            
            # Parse markdown list items
            for line in lines[1:]:
                line = line.strip()
                if line.startswith('- **') and '**:' in line:
                    # Extract key and value from markdown
                    match = re.match(r'- \*\*(.*?)\*\*:\s*(.*)', line)
                    if match:
                        key, value = match.groups()
                        key = key.lower().replace(' ', '_').replace('-', '_')
                        
                        # Parse boolean values
                        if value.lower() in ['true', 'false']:
                            value = value.lower() == 'true'
                        # Parse numeric values for speaker_order
                        elif key == 'speaker_order':
                            try:
                                value = int(value)
                            except ValueError:
                                # If not a valid number, keep default
                                continue
                        
                        config[key] = value
            
            # Only include active avatars
            if config.get('active', True):
                avatars[avatar_key] = config
        
        return avatars
        
    except FileNotFoundError:
        # Fallback to default configuration
        print("Warning: avatar_config.md not found, using defaults")
        return {
            'kora': {
                'active': True,
                'name': 'Kora',
                'prompt_file': 'prompts/kora_prompt.md',
                'color': 'from-purple-500 to-blue-500',
                'text_color': 'text-purple-300',
                'icon': 'fas fa-leaf',
                'allow_followups': True,
                'speaker_order': 1
            },
            'sassi': {
                'active': True,
                'name': 'Sassi', 
                'prompt_file': 'prompts/sassi_prompt.md',
                'color': 'from-pink-500 to-rose-500',
                'text_color': 'text-pink-300',
                'icon': 'fas fa-palette',
                'allow_followups': True,
                'speaker_order': 2
            },
            'riku': {
                'active': True,
                'name': 'Riku',
                'prompt_file': 'prompts/riku_prompt.md', 
                'color': 'from-green-500 to-emerald-500',
                'text_color': 'text-green-300',
                'icon': 'fas fa-brain',
                'allow_followups': True,
                'speaker_order': 3
            }
        }
    except Exception as e:
        print(f"Error loading avatar config: {e}")
        return {}

# Load AI Characters configuration from markdown file
AI_CHARACTERS = load_avatar_config()

def load_ai_prompt(character):
    """Load the system prompt for a specific AI character"""
    try:
        prompt_file = AI_CHARACTERS[character]['prompt_file']
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"You are {AI_CHARACTERS[character]['name']}, a helpful AI assistant."

def detect_mentions(text):
    """Detect @mentions in text and return list of mentioned characters"""
    import re
    mention_pattern = r'@(kora|sassi|riku|boss)'
    mentions = re.findall(mention_pattern, text.lower())
    return list(set(mentions))  # Remove duplicates

def generate_follow_up_prompt(mentioned_character, mentioning_character, mentioning_message, full_conversation):
    """Generate a prompt for follow-up response"""
    character_name = AI_CHARACTERS[mentioned_character]['name']
    mentioning_name = AI_CHARACTERS[mentioning_character]['name']
    
    return f"""You ({character_name}) have been @mentioned by {mentioning_name} in their recent message: "{mentioning_message}"

You should provide a brief, natural follow-up response that acknowledges their mention and adds to the conversation. Keep it conversational and in character. Start your response with @{mentioning_name} to show you're responding to them specifically.

This is a follow-up response, so keep it concise but meaningful."""

def generate_thought_injection(character, ai_order, current_position, user_message):
    """Generate thought injection for sequential awareness"""
    character_name = AI_CHARACTERS[character]['name']
    
    if current_position == 0:
        # First AI - only sees user message
        return f"""[THOUGHT INJECTION] You ({character_name}) are responding FIRST in this turn. 
The user said: "{user_message}"
You should give a fresh, authentic response in your unique style. The other AIs will build upon what you say."""
    
    else:
        # Subsequent AIs - see previous responses
        previous_ais = ai_order[:current_position]
        previous_names = [AI_CHARACTERS[ai]['name'] for ai in previous_ais]
        
        if current_position == 1:
            return f"""[THOUGHT INJECTION] You ({character_name}) are responding SECOND in this turn.
The user said: "{user_message}"
{previous_names[0]} has already responded - you can see their response above.
You should acknowledge and build upon what {previous_names[0]} said while adding your unique {character} perspective."""
        
        elif current_position == 2:
            return f"""[THOUGHT INJECTION] You ({character_name}) are responding LAST in this turn.
The user said: "{user_message}"
Both {previous_names[0]} and {previous_names[1]} have already responded - you can see their responses above.
You should synthesize and build upon what both {previous_names[0]} and {previous_names[1]} said while adding your unique {character} perspective."""
    
    return ""

def get_ai_follow_up_response(character, mentioning_character, mentioning_message, conversation_history):
    """Get a follow-up response from a mentioned AI"""
    # Prepare messages for OpenAI API
    base_prompt = load_ai_prompt(character)
    follow_up_prompt = generate_follow_up_prompt(character, mentioning_character, mentioning_message, conversation_history)
    
    # Combine base prompt with follow-up context
    system_message = f"{base_prompt}\n\n{follow_up_prompt}"
    
    messages = [{"role": "system", "content": system_message}]
    messages.extend(conversation_history)
    
    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=400,  # Shorter for follow-ups
        temperature=0.7
    )
    
    return response.choices[0].message.content

def get_ai_order():
    """Get AI response order based on speaker_order configuration"""
    # Sort active characters by their speaker_order
    active_characters = [(key, config) for key, config in AI_CHARACTERS.items() 
                        if config.get('active', True)]
    
    # Sort by speaker_order, then by key name as fallback
    active_characters.sort(key=lambda x: (x[1].get('speaker_order', 999), x[0]))
    
    return [char[0] for char in active_characters]

def get_conversation_history():
    """Get conversation history from session"""
    if 'conversation' not in session:
        session['conversation'] = []
    return session['conversation']

def add_to_conversation(role, content, character=None):
    """Add message to conversation history"""
    conversation = get_conversation_history()
    message = {"role": role, "content": content}
    if character:
        message["character"] = character
    conversation.append(message)
    session['conversation'] = conversation
    session.modified = True

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with multi-AI responses and @mention follow-ups"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Add user message to conversation (as Boss)
        add_to_conversation("user", user_message, "boss")
        
        # Get AI responses in configured speaker order
        ai_order = get_ai_order()
        
        # Store all AI responses for this turn
        ai_responses = []
        mention_follow_ups = []
        
        # Get AI responses in SEQUENTIAL order (one at a time)
        for i, character in enumerate(ai_order):
            # Get current conversation history including ALL previous responses
            conversation = get_conversation_history()
            
            # Generate thought injection for this AI's position
            thought_injection = generate_thought_injection(character, ai_order, i, user_message)
            
            # Combine base prompt with thought injection
            base_prompt = load_ai_prompt(character)
            enhanced_prompt = f"{base_prompt}\n\n{thought_injection}"
            
            # Prepare messages for OpenAI API
            messages = [{"role": "system", "content": enhanced_prompt}]
            messages.extend(conversation)
            
            # Call OpenAI API for this specific AI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message.content
            
            # Check for @mentions in this response
            mentions = detect_mentions(assistant_message)
            ai_mentions = [m for m in mentions if m in AI_CHARACTERS.keys()]
            
            # Create AI response object
            ai_response = {
                "role": "assistant",
                "content": assistant_message,
                "character": character,
                "character_name": AI_CHARACTERS[character]['name'],
                "order": i + 1,
                "mentions": mentions,
                "is_follow_up": False
            }
            
            ai_responses.append(ai_response)
            
            # IMMEDIATELY add this AI's response to conversation history
            # so the next AI can see it
            add_to_conversation("assistant", assistant_message, character)
            
            # Store mentioned AIs for follow-up responses
            for mentioned_ai in ai_mentions:
                if mentioned_ai != character:  # Don't mention yourself
                    mention_follow_ups.append({
                        'mentioned_character': mentioned_ai,
                        'mentioning_character': character,
                        'mentioning_message': assistant_message
                    })
        
        # Note: AI responses are already added to conversation history above
        # No need to add them again here
        
        # Handle @mention follow-ups
        follow_up_responses = []
        if mention_follow_ups:
            # Get updated conversation history including main responses
            updated_conversation = get_conversation_history()
            
            # Process follow-ups for each mentioned AI
            processed_mentions = set()  # Avoid duplicate follow-ups
            
            for follow_up in mention_follow_ups:
                mentioned_char = follow_up['mentioned_character']
                mentioning_char = follow_up['mentioning_character']
                mentioning_msg = follow_up['mentioning_message']
                
                # Skip if we already processed this character's follow-up
                if mentioned_char in processed_mentions:
                    continue
                
                # Skip if this character doesn't allow follow-ups
                if not AI_CHARACTERS.get(mentioned_char, {}).get('allow_followups', True):
                    continue
                    
                processed_mentions.add(mentioned_char)
                
                try:
                    follow_up_content = get_ai_follow_up_response(
                        mentioned_char, 
                        mentioning_char, 
                        mentioning_msg, 
                        updated_conversation
                    )
                    
                    follow_up_response = {
                        "role": "assistant",
                        "content": follow_up_content,
                        "character": mentioned_char,
                        "character_name": AI_CHARACTERS[mentioned_char]['name'],
                        "order": len(ai_responses) + len(follow_up_responses) + 1,
                        "mentions": detect_mentions(follow_up_content),
                        "is_follow_up": True,
                        "responding_to": mentioning_char
                    }
                    
                    follow_up_responses.append(follow_up_response)
                    
                    # Add follow-up to conversation history
                    add_to_conversation("assistant", follow_up_content, mentioned_char)
                    
                except Exception as e:
                    print(f"Error generating follow-up for {mentioned_char}: {str(e)}")
                    continue
        
        # Combine main responses and follow-ups
        all_responses = ai_responses + follow_up_responses
        
        return jsonify({
            'responses': ai_responses,
            'follow_ups': follow_up_responses,
            'all_responses': all_responses,
            'ai_order': ai_order,
            'has_mentions': len(mention_follow_ups) > 0,
            'success': True
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history"""
    session['conversation'] = []
    session.modified = True
    return jsonify({'success': True, 'message': 'Conversation cleared'})

@app.route('/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    return jsonify({'conversation': get_conversation_history()})

@app.route('/avatars', methods=['GET'])
def get_avatars():
    """Get avatar configuration"""
    return jsonify({'avatars': AI_CHARACTERS})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7632, debug=True)

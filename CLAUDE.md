# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agora Chat is a multi-AI chatbot web application built with Flask that features three distinct AI characters (Kora, Sassi, and Riku) that respond to user messages with unique perspectives. The application supports @mentions between AI characters for follow-up conversations and maintains conversation history through Flask sessions.

## Development Commands

### Starting the Application
```bash
./startup.sh
```
This script handles the complete startup process:
- Kills any existing processes on port 7632
- Creates/activates virtual environment
- Installs/updates Python dependencies
- Starts Flask app on port 7632
- Opens browser automatically
- Shows real-time logs

### Manual Development Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### Testing Commands
```bash
# Test OpenAI API connection and environment variables
python test_openai.py

# Test avatar configuration and speaker order
python test_speaker_order.py
```

### Environment Setup
The application requires a `.env` file with:
```
OPENAI_API_KEY=your_api_key_here
```

## Architecture Overview

### Backend Structure (Flask)
- **app.py**: Main Flask application with multi-AI conversation logic
- **avatar_config.md**: Configurable avatar settings (names, order, activation, follow-ups)
- **AI Characters**: Dynamically loaded from markdown configuration
- **Conversation Flow**: Configurable speaker order with @mention follow-up system
- **Session Management**: Conversation history stored in Flask sessions

### Frontend Structure
- **templates/chat.html**: Main chat interface with Tailwind CSS styling
- **static/js/chat.js**: Chat functionality using vanilla JavaScript classes
- **static/css/theme.css**: Custom styling and animations

### Key Features Implementation
- **Multi-AI Responses**: AIs respond in configurable speaker order, each seeing previous responses
- **@Mention System**: AIs can mention each other for follow-up responses (configurable per avatar)
- **Sequential Awareness**: Later AIs in the sequence see earlier responses with position context
- **Conversation Memory**: Full conversation history maintained in session
- **Real-time UI**: Animated message bubbles with typing indicators
- **Dynamic Avatar Configuration**: Runtime loading of avatar settings from markdown file

### API Endpoints
- `GET /`: Main chat interface
- `POST /chat`: Handle user messages and generate AI responses
- `POST /clear`: Clear conversation history
- `GET /history`: Retrieve conversation history
- `GET /avatars`: Get current avatar configuration for frontend

### Prompt System
- Character prompts stored as markdown files in `prompts/` directory
- Dynamic thought injection for sequential AI awareness
- Follow-up prompt generation for @mention responses

## Important Implementation Details

### AI Response Generation
The application uses a sophisticated multi-step process:
1. User message is added to conversation history as "boss"
2. AIs respond in configured speaker order, each seeing all previous responses
3. Each AI receives position-aware thought injection (first, second, last)
4. @mentions trigger follow-up responses from mentioned characters (if enabled)
5. All responses are added to session history immediately

### Avatar Configuration System
Avatars are configured via `avatar_config.md` with these settings:
- **Active**: Enable/disable avatar participation
- **Name**: Display name (can be customized)
- **Prompt File**: Path to personality prompt
- **Color**: Tailwind CSS gradient classes for avatar styling
- **Text Color**: Text color for avatar name
- **Icon**: Font Awesome icon class
- **Allow Follow-ups**: Control @mention follow-up responses
- **Speaker Order**: Numeric order for response sequence (1=first, 2=second, etc.)

Each AI character has:
- Dynamic loading from markdown configuration
- Unique prompt file in `prompts/` directory
- Configurable visual styling and behavior
- Position-aware response generation

### Error Handling
- OpenAI API errors are caught and display user-friendly messages
- Port conflicts are handled aggressively in startup script
- Conversation state is preserved across browser refreshes

## File Structure Context

```
Agora/
├── app.py                    # Main Flask application with multi-AI logic
├── avatar_config.md         # Avatar configuration (names, order, settings)
├── startup.sh               # Development startup script
├── requirements.txt         # Python dependencies
├── test_openai.py           # OpenAI API connection test script
├── test_speaker_order.py    # Avatar configuration test script
├── prompts/                 # AI character prompts
│   ├── kora_prompt.md      # Kora's system prompt
│   ├── sassi_prompt.md     # Sassi's system prompt
│   └── riku_prompt.md      # Riku's system prompt
├── templates/
│   └── chat.html           # Main chat interface
├── static/
│   ├── css/
│   │   └── theme.css       # Custom styling
│   └── js/
│       └── chat.js         # Chat functionality
└── venv/                   # Virtual environment (auto-created)
```

## OpenAI Integration

- Uses OpenAI GPT-4o-mini model
- Supports conversation context with full message history
- Implements character-specific system prompts
- Handles API rate limiting and error responses gracefully

## Common Issues and Debugging

### Dependency Conflicts
The project has specific version requirements due to compatibility issues:
- **OpenAI v1.12.0**: Newer versions (v1.30+) have proxy configuration conflicts
- **Flask 2.3.3 + Werkzeug 2.3.7**: Flask 3.0+ has watchdog compatibility issues
- Use the provided `test_openai.py` script to verify API connectivity

### OpenAI Client Proxy Issues
Systems with corporate proxies may encounter:
```
TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
```
Solution: The app includes proxy error handling with httpx.Client() fallback

### Avatar Configuration Parsing
The markdown parser only reads the "Avatar Settings" section and stops at:
- "## Configuration Notes" 
- "## Examples"
- Any section containing example ### headers

**Key Debugging Insight**: Markdown examples with `### AvatarName` can be misread as avatar definitions if not properly sectioned.

### Speaker Order Logic
- Avatars with same speaker order are sorted alphabetically by key name
- Inactive avatars (Active: false) are excluded from speaker order
- Default speaker order is 999 for undefined values
- Use `test_speaker_order.py` to verify configuration parsing

### Frontend Avatar Loading
- Frontend dynamically loads avatar config via `/avatars` endpoint
- Welcome message adapts to active avatar names and count
- Avatar configuration is loaded asynchronously on page load
- Fallback to default configuration if server request fails

## Troubleshooting Commands

```bash
# Test OpenAI API and environment
python test_openai.py

# Debug avatar configuration parsing  
python test_speaker_order.py

# Check server logs for errors
tail -f agora_chat.log

# Restart with clean environment
rm -rf venv && ./startup.sh
```
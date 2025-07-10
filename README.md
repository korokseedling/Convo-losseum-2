# Agora Chat 🚀

A beautiful, modern AI chatbot built with Flask and powered by OpenAI's GPT-4.

## Features ✨

- **Modern UI**: Beautiful glassmorphism design with Tailwind CSS
- **Real-time Chat**: Instant messaging with AI assistant
- **Conversation Memory**: Maintains context throughout the session
- **Responsive Design**: Works perfectly on desktop and mobile
- **Custom Prompts**: Easily configurable system prompts via markdown
- **Keyboard Shortcuts**: Quick navigation and controls
- **Auto-scroll**: Smooth scrolling to new messages
- **Loading States**: Clear visual feedback during AI responses

## Quick Start 🎯

1. Make sure you have your OpenAI API key in the `.env` file
2. Run the startup script:
   ```bash
   ./startup.sh
   ```
3. Your browser will automatically open to `http://localhost:7632`
4. Start chatting with your AI assistant!

## Project Structure 📁

```
Agora/
├── app.py                 # Main Flask application
├── startup.sh            # Startup script with port management
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── prompts/
│   └── system_prompt.md  # AI system prompt configuration
├── templates/
│   └── chat.html         # Main chat interface
└── static/
    ├── css/
    │   └── theme.css     # Custom styling and animations
    └── js/
        └── chat.js       # Chat functionality and interactions
```

## Customization 🎨

### Modify AI Behavior
Edit `prompts/system_prompt.md` to change how the AI responds.

### Update Styling
Modify `static/css/theme.css` to customize the visual appearance.

### Add Features
Extend `static/js/chat.js` and `app.py` to add new functionality.

## Technology Stack 🛠️

- **Backend**: Flask (Python)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **AI**: OpenAI GPT-4
- **Icons**: Font Awesome, Heroicons
- **Fonts**: Google Fonts (Inter)

## Keyboard Shortcuts ⌨️

- `Ctrl/Cmd + K`: Focus message input
- `Ctrl/Cmd + L`: Clear conversation
- `Enter`: Send message
- `Escape`: Blur input field

## Development 🔧

The application runs on port 7632 by default. The startup script handles:
- Environment setup
- Aggressive port cleaning
- Dependency installation
- Server startup
- Browser opening
- Real-time logging

## Troubleshooting 🔍

If you encounter issues:
1. Check `agora_chat.log` for error details
2. Ensure your OpenAI API key is valid
3. Verify port 7632 is not blocked by firewall
4. Make sure all dependencies are installed

Enjoy chatting with your AI assistant! 🤖✨

// Agora Multi-AI Chat JavaScript
class AgoraMultiChat {
    constructor() {
        this.messagesContainer = document.getElementById('messages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        
        // AI Character configurations (will be loaded from server)
        this.aiCharacters = {};
        
        this.initializeApp();
    }

    async initializeApp() {
        await this.loadAvatarConfig();
        this.initializeEventListeners();
        this.loadConversationHistory();
    }

    async loadAvatarConfig() {
        try {
            const response = await fetch('/avatars');
            const data = await response.json();
            
            if (data.avatars) {
                // Convert server config to frontend format
                this.aiCharacters = {};
                for (const [key, config] of Object.entries(data.avatars)) {
                    this.aiCharacters[key] = {
                        name: config.name,
                        color: config.color,
                        textColor: config.text_color,
                        icon: config.icon
                    };
                }
                
                console.log('Loaded avatar configuration:', this.aiCharacters);
            }
        } catch (error) {
            console.error('Failed to load avatar configuration:', error);
            // Fallback to default configuration
            this.aiCharacters = {
                'kora': {
                    name: 'Kora',
                    color: 'from-purple-500 to-blue-500',
                    textColor: 'text-purple-300',
                    icon: 'fas fa-leaf'
                },
                'sassi': {
                    name: 'Sassi',
                    color: 'from-pink-500 to-rose-500',
                    textColor: 'text-pink-300',
                    icon: 'fas fa-palette'
                },
                'riku': {
                    name: 'Riku',
                    color: 'from-green-500 to-emerald-500',
                    textColor: 'text-green-300',
                    icon: 'fas fa-brain'
                }
            };
        }
    }

    initializeEventListeners() {
        // Send button click
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Enter key press
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Clear conversation
        this.clearBtn.addEventListener('click', () => this.clearConversation());
        
        // Auto-resize input
        this.messageInput.addEventListener('input', () => this.autoResizeInput());
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Disable input while processing
        this.setInputState(false);
        
        // Add user message to chat
        this.addUserMessage(message);
        
        // Clear input
        this.messageInput.value = '';
        
        // Show loading indicator
        this.showLoading(true);
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Add main AI responses in sequence with proper delays
                for (let i = 0; i < data.responses.length; i++) {
                    const aiResponse = data.responses[i];
                    
                    // Add delay between responses to show sequential nature
                    if (i > 0) {
                        await new Promise(resolve => setTimeout(resolve, 1200));
                    }
                    
                    this.addAIMessage(aiResponse);
                }
                
                // Add follow-up responses if any @mentions were detected
                if (data.follow_ups && data.follow_ups.length > 0) {
                    // Add a longer delay before follow-ups to show they're separate
                    await new Promise(resolve => setTimeout(resolve, 1800));
                    
                    for (let i = 0; i < data.follow_ups.length; i++) {
                        const followUpResponse = data.follow_ups[i];
                        
                        // Add delay between follow-ups
                        if (i > 0) {
                            await new Promise(resolve => setTimeout(resolve, 800));
                        }
                        
                        this.addAIMessage(followUpResponse, true); // true = is follow-up
                    }
                }
            } else {
                this.addErrorMessage('Sorry, I encountered an error. Please try again.');
                console.error('Chat error:', data.error);
            }
        } catch (error) {
            console.error('Network error:', error);
            this.addErrorMessage('Connection error. Please check your internet connection and try again.');
        } finally {
            // Hide loading and re-enable input
            this.showLoading(false);
            this.setInputState(true);
            this.messageInput.focus();
        }
    }

    addUserMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-bubble user-message animate-slide-up';
        
        const timestamp = this.getCurrentTime();

        messageDiv.innerHTML = `
            <div class="flex items-start space-x-3 flex-row-reverse space-x-reverse">
                <div class="avatar user-avatar">
                    <i class="fas fa-user text-white"></i>
                </div>
                <div class="message-content text-right">
                    <div class="message-text">
                        ${this.formatMessage(content)}
                    </div>
                    <div class="message-time">
                        ${timestamp}
                    </div>
                </div>
            </div>
        `;

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Add entrance animation
        setTimeout(() => {
            messageDiv.classList.add('message-appear');
        }, 50);
    }

    addAIMessage(aiResponse, isFollowUp = false) {
        const character = this.aiCharacters[aiResponse.character];
        const messageDiv = document.createElement('div');
        
        // Add different styling for follow-ups
        let bubbleClass = 'message-bubble assistant-message animate-slide-up';
        if (isFollowUp) {
            bubbleClass += ' follow-up-message';
        }
        
        messageDiv.className = bubbleClass;
        
        const timestamp = this.getCurrentTime();
        
        // Format the content and highlight @mentions
        const formattedContent = this.formatMessageWithMentions(aiResponse.content);
        
        // Create order badge with follow-up indicator
        let orderBadge = `#${aiResponse.order}`;
        if (isFollowUp) {
            orderBadge = `↳ Follow-up`;
        }

        messageDiv.innerHTML = `
            <div class="flex items-start space-x-3">
                <div class="avatar bg-gradient-to-br ${character.color}">
                    <i class="${character.icon} text-white"></i>
                </div>
                <div class="message-content">
                    <div class="character-name ${character.textColor} text-sm font-semibold mb-1 flex items-center">
                        ${character.name}
                        <span class="ml-2 text-xs bg-white/20 px-2 py-1 rounded-full">${orderBadge}</span>
                        ${isFollowUp ? '<span class="ml-1 text-xs opacity-75">💬</span>' : ''}
                    </div>
                    <div class="message-text ${isFollowUp ? 'follow-up-bubble' : ''}">
                        ${formattedContent}
                    </div>
                    <div class="message-time">
                        ${timestamp}
                    </div>
                </div>
            </div>
        `;

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Add entrance animation
        setTimeout(() => {
            messageDiv.classList.add('message-appear');
        }, 50);
    }

    addErrorMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-bubble assistant-message error-message animate-slide-up';
        
        const timestamp = this.getCurrentTime();

        messageDiv.innerHTML = `
            <div class="flex items-start space-x-3">
                <div class="avatar bg-red-500">
                    <i class="fas fa-exclamation-triangle text-white"></i>
                </div>
                <div class="message-content">
                    <div class="character-name text-red-300 text-sm font-semibold mb-1">System</div>
                    <div class="message-text bg-red-500/20 border-red-500/30">
                        ${this.formatMessage(content)}
                    </div>
                    <div class="message-time">
                        ${timestamp}
                    </div>
                </div>
            </div>
        `;

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessage(content) {
        // Basic markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code class="bg-white/20 px-1 py-0.5 rounded text-sm">$1</code>')
            .replace(/\n/g, '<br>');
    }
    
    formatMessageWithMentions(content) {
        // First apply basic formatting
        let formatted = this.formatMessage(content);
        
        // Then highlight @mentions
        const mentionColors = {
            '@kora': 'text-purple-300 bg-purple-500/20',
            '@sassi': 'text-pink-300 bg-pink-500/20', 
            '@riku': 'text-green-300 bg-green-500/20',
            '@boss': 'text-blue-300 bg-blue-500/20'
        };
        
        // Replace @mentions with styled spans
        for (const [mention, colorClass] of Object.entries(mentionColors)) {
            const regex = new RegExp(`(${mention.replace('@', '@')})`, 'gi');
            formatted = formatted.replace(regex, `<span class="mention ${colorClass} px-2 py-1 rounded-md font-semibold text-sm">$1</span>`);
        }
        
        return formatted;
    }

    async clearConversation() {
        if (!confirm('Are you sure you want to clear the conversation?')) {
            return;
        }

        try {
            const response = await fetch('/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                // Clear messages container but keep welcome message
                this.addWelcomeMessage();
                
                // Show success message briefly
                this.showNotification('Conversation cleared successfully!', 'success');
            }
        } catch (error) {
            console.error('Error clearing conversation:', error);
            this.showNotification('Failed to clear conversation', 'error');
        }
    }

    addWelcomeMessage() {
        // Get active avatar names for welcome message
        const activeNames = Object.values(this.aiCharacters).map(char => char.name);
        const namesText = activeNames.length > 1 
            ? activeNames.slice(0, -1).join(', ') + ' and ' + activeNames.slice(-1)
            : activeNames[0] || 'your AI companion';
        
        // Use the first available avatar for the welcome message
        const firstAvatar = Object.keys(this.aiCharacters)[0];
        const welcomeAvatar = firstAvatar ? this.aiCharacters[firstAvatar] : {
            name: 'AI Assistant',
            color: 'from-purple-500 to-blue-500',
            textColor: 'text-purple-300',
            icon: 'fas fa-robot'
        };

        this.messagesContainer.innerHTML = `
            <div class="message-bubble assistant-message">
                <div class="flex items-start space-x-3">
                    <div class="avatar bg-gradient-to-br ${welcomeAvatar.color}">
                        <i class="${welcomeAvatar.icon} text-white"></i>
                    </div>
                    <div class="message-content">
                        <div class="character-name ${welcomeAvatar.textColor} text-sm font-semibold mb-1">${welcomeAvatar.name}</div>
                        <div class="message-text">
                            Welcome to Agora Chat! We're ${namesText} - your AI companion${activeNames.length > 1 ? 's' : ''}. We'll each share our unique perspectives on your questions!
                        </div>
                        <div class="message-time">
                            Just now
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadConversationHistory() {
        try {
            const response = await fetch('/history');
            const data = await response.json();
            
            if (data.conversation && data.conversation.length > 0) {
                // Clear welcome message if we have history
                this.messagesContainer.innerHTML = '';
                
                // Add each message from history
                data.conversation.forEach(msg => {
                    if (msg.role === 'user') {
                        this.addUserMessage(msg.content);
                    } else if (msg.role === 'assistant') {
                        // Create mock AI response object for history
                        const aiResponse = {
                            content: msg.content,
                            character: msg.character || Object.keys(this.aiCharacters)[0],
                            order: 1
                        };
                        this.addAIMessage(aiResponse);
                    }
                });
            } else {
                // Show welcome message if no history
                this.addWelcomeMessage();
            }
        } catch (error) {
            console.error('Error loading conversation history:', error);
            this.addWelcomeMessage();
        }
    }

    setInputState(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendBtn.disabled = !enabled;
        
        if (enabled) {
            this.sendBtn.innerHTML = '<i class="fas fa-paper-plane mr-3"></i>Send';
            this.messageInput.focus();
        } else {
            this.sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-3"></i>Thinking...';
        }
    }

    showLoading(show) {
        if (show) {
            this.loadingIndicator.classList.remove('hidden');
        } else {
            this.loadingIndicator.classList.add('hidden');
        }
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    autoResizeInput() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 150) + 'px';
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg text-white font-semibold transition-all duration-300 transform translate-x-full`;
        
        switch (type) {
            case 'success':
                notification.classList.add('bg-green-500');
                break;
            case 'error':
                notification.classList.add('bg-red-500');
                break;
            default:
                notification.classList.add('bg-blue-500');
        }
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // Animate out and remove
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // Utility methods
    getCurrentTime() {
        return new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Keyboard Shortcuts
class KeyboardShortcuts {
    constructor(chatInstance) {
        this.chat = chatInstance;
        this.initializeShortcuts();
    }

    initializeShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K to focus input
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.chat.messageInput.focus();
            }
            
            // Ctrl/Cmd + L to clear conversation
            if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
                e.preventDefault();
                this.chat.clearConversation();
            }
            
            // Escape to blur input
            if (e.key === 'Escape') {
                this.chat.messageInput.blur();
            }
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const chat = new AgoraMultiChat();
    const shortcuts = new KeyboardShortcuts(chat);
    
    // Global chat instance for debugging
    window.agoraChat = chat;
    
    console.log('Agora Multi-AI Chat initialized successfully!');
    console.log('Meet your AI companions: Kora (wise), Sassi (creative), Riku (analytical)');
    console.log('Keyboard shortcuts:');
    console.log('  Ctrl/Cmd + K: Focus input');
    console.log('  Ctrl/Cmd + L: Clear conversation');
    console.log('  Enter: Send message');
    console.log('  Escape: Blur input');
});

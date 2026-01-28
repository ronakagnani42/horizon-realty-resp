/**
 * Advanced AI Chatbot - Complete JavaScript Implementation
 * Integrates with Django backend for intelligent property assistance
 */

(function() {
    'use strict';

    // ==========================================
    // CONFIGURATION
    // ==========================================
    const CONFIG = {
        API_ENDPOINT: '/chatbot/get-response/',
        TYPING_DELAY: 1000,
        MAX_MESSAGE_LENGTH: 500,
        AUTO_SCROLL_DELAY: 100,
        CSRF_TOKEN: null
    };

    // ==========================================
    // DOM ELEMENTS
    // ==========================================
    let chatBubble, chatOverlay, chatContainer, chatMessages, 
        chatInput, chatSend, chatClose, typingIndicator, quickOptions;

    // ==========================================
    // STATE MANAGEMENT
    // ==========================================
    const chatState = {
        isOpen: false,
        isTyping: false,
        messageHistory: [],
        sessionId: null
    };

    // ==========================================
    // INITIALIZATION
    // ==========================================
    function initializeChatbot() {
        // Get DOM elements
        chatBubble = document.getElementById('chatBubble');
        chatOverlay = document.getElementById('chatOverlay');
        chatContainer = document.querySelector('.chat-container');
        chatMessages = document.getElementById('chatMessages');
        chatInput = document.getElementById('chatInput');
        chatSend = document.getElementById('chatSend');
        chatClose = document.getElementById('chatClose');
        typingIndicator = document.getElementById('typingIndicator');
        quickOptions = document.getElementById('quickOptions');

        // Get CSRF token
        CONFIG.CSRF_TOKEN = getCookie('csrftoken');

        // Attach event listeners
        attachEventListeners();

        // Load conversation history if exists
        loadConversationHistory();

        console.log('AskHorizon Chatbot initialized successfully');
    }

    // ==========================================
    // EVENT LISTENERS
    // ==========================================
    function attachEventListeners() {
        // Open chat
        if (chatBubble) {
            chatBubble.addEventListener('click', openChat);
        }

        // Close chat
        if (chatClose) {
            chatClose.addEventListener('click', closeChat);
        }

        // Close on overlay click (outside chat container)
        if (chatOverlay) {
            chatOverlay.addEventListener('click', function(e) {
                if (e.target === chatOverlay) {
                    closeChat();
                }
            });
        }

        // Send message on button click
        if (chatSend) {
            chatSend.addEventListener('click', sendMessage);
        }

        // Send message on Enter key
        if (chatInput) {
            chatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            // Character counter
            chatInput.addEventListener('input', function() {
                const remaining = CONFIG.MAX_MESSAGE_LENGTH - this.value.length;
                if (remaining < 50) {
                    console.log(`Characters remaining: ${remaining}`);
                }
            });
        }

        // Quick options buttons
        if (quickOptions) {
            const optionButtons = quickOptions.querySelectorAll('.quick-option-btn');
            optionButtons.forEach(btn => {
                btn.addEventListener('click', function() {
                    const option = this.getAttribute('data-option');
                    handleQuickOption(option);
                });
            });
        }

        // Prevent chat container clicks from closing overlay
        if (chatContainer) {
            chatContainer.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
    }

    // ==========================================
    // CHAT CONTROLS
    // ==========================================
    function openChat() {
        if (chatOverlay) {
            chatOverlay.classList.add('show');
            chatState.isOpen = true;
            
            // Focus input
            setTimeout(() => {
                if (chatInput) chatInput.focus();
            }, 300);

            // Load suggestions
            loadQuickSuggestions();
        }
    }

    function closeChat() {
        if (chatOverlay) {
            chatOverlay.classList.remove('show');
            chatState.isOpen = false;
        }
    }

    // ==========================================
    // MESSAGE HANDLING
    // ==========================================
    function sendMessage() {
        const message = chatInput.value.trim();

        // Validate message
        if (!message) {
            showNotification('Please enter a message', 'warning');
            return;
        }

        if (message.length > CONFIG.MAX_MESSAGE_LENGTH) {
            showNotification(`Message too long (max ${CONFIG.MAX_MESSAGE_LENGTH} characters)`, 'error');
            return;
        }

        if (chatState.isTyping) {
            showNotification('Please wait for the response', 'info');
            return;
        }

        // Add user message to chat
        addMessage(message, 'user');

        // Clear input
        chatInput.value = '';

        // Disable input while processing
        setInputState(false);

        // Show typing indicator
        showTypingIndicator();

        // Send to backend
        sendToBackend(message);
    }

    function sendToBackend(message) {
        fetch(CONFIG.API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CONFIG.CSRF_TOKEN
            },
            body: JSON.stringify({
                message: message,
                session_id: chatState.sessionId
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Hide typing indicator
            hideTypingIndicator();

            // Store session ID
            if (data.session_id) {
                chatState.sessionId = data.session_id;
            }

            // Add bot response
            setTimeout(() => {
                addMessage(data.response, 'bot');
                setInputState(true);
                
                // Save to history
                saveConversationHistory();
            }, CONFIG.TYPING_DELAY);
        })
        .catch(error => {
            console.error('Chatbot error:', error);
            hideTypingIndicator();
            
            // Show error message
            setTimeout(() => {
                addMessage(
                    "I apologize, but I'm having trouble connecting right now. " +
                    "Please try again or call us at +91 9104828680.",
                    'bot'
                );
                setInputState(true);
            }, CONFIG.TYPING_DELAY);
        });
    }

    function addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        if (sender === 'bot') {
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.textContent = '🤖';
            messageDiv.appendChild(avatar);
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        
        // Convert markdown-style links to HTML
        const formattedContent = formatMessageContent(content);
        contentDiv.innerHTML = formattedContent;

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Store in history
        chatState.messageHistory.push({
            content: content,
            sender: sender,
            timestamp: new Date().toISOString()
        });

        // Scroll to bottom
        scrollToBottom();
    }

    function formatMessageContent(content) {
        // Convert markdown-style bold to HTML
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert line breaks to <br>
        content = content.replace(/\n/g, '<br>');
        
        // Convert bullet points
        content = content.replace(/^• /gm, '&bull; ');
        
        // Handle links (already in HTML format from backend)
        // No need to convert as backend sends proper HTML links
        
        return content;
    }

    // ==========================================
    // UI CONTROLS
    // ==========================================
    function showTypingIndicator() {
        chatState.isTyping = true;
        if (typingIndicator) {
            typingIndicator.style.display = 'flex';
            setTimeout(() => {
                typingIndicator.classList.add('show');
            }, 10);
        }
        scrollToBottom();
    }

    function hideTypingIndicator() {
        chatState.isTyping = false;
        if (typingIndicator) {
            typingIndicator.classList.remove('show');
            setTimeout(() => {
                typingIndicator.style.display = 'none';
            }, 300);
        }
    }

    function setInputState(enabled) {
        if (chatInput) {
            chatInput.disabled = !enabled;
        }
        if (chatSend) {
            chatSend.disabled = !enabled;
        }
    }

    function scrollToBottom() {
        setTimeout(() => {
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }, CONFIG.AUTO_SCROLL_DELAY);
    }

    function showNotification(message, type = 'info') {
        // Simple console notification for now
        // You can implement a toast notification system here
        console.log(`[${type.toUpperCase()}] ${message}`);
    }

    // ==========================================
    // QUICK OPTIONS
    // ==========================================
    function handleQuickOption(option) {
        const optionMessages = {
            'about': 'What is Horizon Reality?',
            'services': 'Tell me about your services',
            'properties': 'Show me available properties'
        };

        const message = optionMessages[option] || option;
        
        // Set input value and send
        if (chatInput) {
            chatInput.value = message;
            sendMessage();
        }
    }

    function loadQuickSuggestions() {
        fetch('/chatbot/suggestions/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CONFIG.CSRF_TOKEN
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.suggestions && data.suggestions.length > 0) {
                updateQuickOptions(data.suggestions);
            }
        })
        .catch(error => {
            console.log('Could not load suggestions:', error);
        });
    }

    function updateQuickOptions(suggestions) {
        if (!quickOptions) return;

        const buttonsContainer = quickOptions.querySelector('.quick-options-buttons');
        if (!buttonsContainer) return;

        // Clear existing buttons
        buttonsContainer.innerHTML = '';

        // Add new suggestion buttons
        suggestions.slice(0, 4).forEach(suggestion => {
            const button = document.createElement('button');
            button.className = 'quick-option-btn';
            button.textContent = suggestion;
            button.addEventListener('click', function() {
                if (chatInput) {
                    chatInput.value = suggestion;
                    sendMessage();
                }
            });
            buttonsContainer.appendChild(button);
        });
    }

    // ==========================================
    // LOCAL STORAGE
    // ==========================================
    function saveConversationHistory() {
        try {
            localStorage.setItem('chatbot_history', JSON.stringify({
                messages: chatState.messageHistory.slice(-20), // Keep last 20
                sessionId: chatState.sessionId,
                timestamp: new Date().toISOString()
            }));
        } catch (e) {
            console.log('Could not save conversation history:', e);
        }
    }

    function loadConversationHistory() {
        try {
            const saved = localStorage.getItem('chatbot_history');
            if (saved) {
                const data = JSON.parse(saved);
                const savedTime = new Date(data.timestamp);
                const now = new Date();
                const hoursDiff = (now - savedTime) / (1000 * 60 * 60);

                // Load history if less than 24 hours old
                if (hoursDiff < 24 && data.messages && data.messages.length > 0) {
                    chatState.sessionId = data.sessionId;
                    
                    // Restore messages (skip welcome message, keep last 5)
                    data.messages.slice(-5).forEach(msg => {
                        if (msg.sender !== 'bot' || !msg.content.includes('Hi there!')) {
                            addMessage(msg.content, msg.sender);
                        }
                    });
                }
            }
        } catch (e) {
            console.log('Could not load conversation history:', e);
        }
    }

    // ==========================================
    // UTILITY FUNCTIONS
    // ==========================================
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // ==========================================
    // INITIALIZE ON DOM READY
    // ==========================================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeChatbot);
    } else {
        initializeChatbot();
    }

    // ==========================================
    // EXPOSE PUBLIC API (optional)
    // ==========================================
    window.AskHorizon = {
        open: openChat,
        close: closeChat,
        send: function(message) {
            if (chatInput) {
                chatInput.value = message;
                sendMessage();
            }
        },
        clear: function() {
            if (chatMessages) {
                // Keep only welcome message
                const messages = chatMessages.querySelectorAll('.message');
                messages.forEach((msg, index) => {
                    if (index > 0) msg.remove();
                });
            }
            chatState.messageHistory = [];
            localStorage.removeItem('chatbot_history');
        }
    };

})();
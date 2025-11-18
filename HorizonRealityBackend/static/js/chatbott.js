
document.addEventListener('DOMContentLoaded', function() {
     const chatBubble = document.getElementById('chatBubble');
    const chatOverlay = document.getElementById('chatOverlay');
    const chatClose = document.getElementById('chatClose');
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    const chatMessages = document.getElementById('chatMessages');
    const typingIndicator = document.getElementById('typingIndicator');
    const quickOptions = document.getElementById('quickOptions');

    // Ensure all elements are found
    if (!chatBubble || !chatOverlay || !chatClose || !chatInput || !chatSend || !chatMessages || !typingIndicator) {
        console.error('One or more chat elements not found');
        return;
    }

    // Initialize typing indicator
    typingIndicator.style.display = 'none';

    // Quick options responses
    const quickOptionsResponses = {
        about: `🏠 **About Horizon Reality**

👋 Welcome to Horizon Reality : Your Gateway to Real Estate Excellence!

I'm your virtual guide here to make your real estate journey easy, informed, and personalized.
✨ Whether you're buying, selling, investing, or designing your space, we've got you covered.

• Get expert help with managing your investment portfolio, financing, legal advice, and interiors.
• Access premium properties through our trusted developer network.
• Explore trending listings and unlock the best market deals.
• Receive tailored support backed by real insights.

Personal Consultation: Book time with our team for personalized guidance.
Let's turn your dream space into a reality with trust, transparency, and complete support.

How can I assist you today? 💬`,

        services: `🛠️ **Our Services**

**Property Services:**
🛠 Our Services

Property Services:
🏠 Residential Properties
🏢 Commercial Properties
🔄 Resale & Leasing 
💰 Property Investment Consultation

Additional Services:
🎨 Interior Design consultancy & Turnkey Solutions
📋 Legal Documentation & Financing
📊 Market Analysis & Insights
🤝 Developer Partnerships

Why Choose Us:
✨ Client-centric approach with personalized solutions
✨ Transparent and reliable processes
✨ One-stop solution for all property needs
✨ Strong network with trusted developers

Want to know more about any specific service? Just ask! 😊`,

        properties: `🏘️ **Our Property Portfolio**

**Residential Properties:**
🏠 1BHK, 2BHK, 3BHK, 4BHK, 5BHK Apartments
🏡 Villas & Bungalows
🏘 Duplex & Penthouse Options
🏠 Tenements & Row Houses

Commercial Properties:
🏢 Office Spaces
🏪 Retail Showrooms
🏬 Shop Spaces
🏢 Corporate Floors

Property Categories:
🆕 New Launch Projects
🔄 Resale Properties
🏠 Rental/Leasing Options
💼 Investment Properties

Some of the Popular Locations in Ahmedabad:
📍Thaltej , South Bopal, Shela
📍 Gota , Vaishnodevi, Science Park 
📍 Prahlad Nagar, Satellite, SG Highway
📍  Iscon, Ambli, Bodakdev, Vastrapur 

Want to search for specific properties? Try asking:
• "2BHK in Bopal under 50 lakhs"
• "Commercial office space in SG Highway"
• "Villas in Shela"`
    };

    // Handle quick option clicks
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('quick-option-btn')) {
            const option = e.target.getAttribute('data-option');
            const optionText = e.target.textContent.trim();
            
            // Add user message
            addMessage(optionText, 'user');
            
            // KEEP QUICK OPTIONS VISIBLE - Remove this line
            // if (quickOptions) {
            //     quickOptions.style.display = 'none';
            // }
            
            // Show typing indicator
            showTyping();
            
            // Simulate delay and show response
            setTimeout(() => {
                hideTyping();
                const response = quickOptionsResponses[option] || "Thanks for your question! How can I help you with your property needs?";
                addMessage(response, 'bot');
            }, 1500);
        }
    });

    chatBubble.addEventListener('click', () => {
        console.log('Chat bubble clicked');
        chatOverlay.classList.add('show');
        
        // Quick options are always visible, no need to show/hide
        
        setTimeout(() => {
            chatInput.focus();
        }, 300);
    });

    chatClose.addEventListener('click', () => {
        chatOverlay.classList.remove('show');
        
        // Quick options remain visible, no reset needed
    });

    chatOverlay.addEventListener('click', function (e) {
        if (e.target === chatOverlay) {
            chatOverlay.classList.remove('show');
            
            // Quick options remain visible, no reset needed
        }
    });

    chatSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    console.log('Sending message:', message);
    addMessage(message, 'user');
    chatInput.value = '';
    
    // Ensure quick options remain visible (no hiding)
    // quickOptions.style.display = 'block'; // Uncomment if needed to ensure visibility
    
    chatSend.disabled = true;
    chatInput.disabled = true;
    chatBubble.classList.add('typing');

    showTyping();

    setTimeout(() => {
        fetch(`/chatbot/get-response/?message=${encodeURIComponent(message)}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        })
            .then(res => {
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                return res.json();
            })
            .then(data => {
                hideTyping();
                chatBubble.classList.remove('typing');
                const formattedResponse = formatBotResponse(data.response || 'Thanks for your message! How can I help you with your property needs?');
                addMessage(formattedResponse, 'bot');
                chatSend.disabled = false;
                chatInput.disabled = false;
                chatInput.focus();
            })
            .catch(error => {
                console.error('Chat error:', error);
                hideTyping();
                chatBubble.classList.remove('typing');
                addMessage("Thanks for your message! I'm here to help with all your property needs. What would you like to know?", 'bot');
                chatSend.disabled = false;
                chatInput.disabled = false;
                chatInput.focus();
            });
    }, 1500);
}

    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.className = `message ${sender}`;

        if (sender === 'user') {
            // Remove the "You" label by just showing the content
            div.innerHTML = `<div class="content">${escapeHtml(text)}</div>`;
        } else {
            const formattedText = text
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/🔗\s*<a\s+href="([^"]+)"\s+target="_blank"\s+class="property-link">([^<]+)<\/a>/g,
                    '🔗 <a href="$1" target="_blank" class="property-link">$2</a>')
                .replace(/📞\s*<a\s+href="([^"]+)"\s+class="contact-link">([^<]+)<\/a>/g,
                    '📞 <a href="$1" class="contact-link">$2</a>');

            div.innerHTML = `<div class="avatar">👩</div><div class="content">${formattedText}</div>`;
        }

        chatMessages.appendChild(div);

        // Handle property links
        div.querySelectorAll('.property-link').forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                const url = this.getAttribute('href');
                window.open(url, '_blank');
                console.log('Opening property link:', url);
            });
        });

        // Handle contact links
        div.querySelectorAll('.contact-link').forEach(link => {
            link.addEventListener('click', function (e) {
                console.log('Calling:', this.getAttribute('href'));
            });
        });

        // Smooth scroll to bottom
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }

    function formatBotResponse(response) {
        let formatted = response
            .replace(/\*\*[^*]+\*\*/g, match => match)
            .replace(/🏠|🏡|🔑|💰|📍|🏢|🔗|✅|📊|🛠️|🏘️|🆕|🔄|💼|📋|🎨|🏗️|🤝|✨|🌟|😊|😄|👋|💙|🤗|🌟|💫/g, match => match)
            .replace(/Location:\s*/g, '\n📍 Location: ')
            .replace(/Type:\s*/g, '\n🏗️ Type: ')
            .replace(/Area:\s*/g, '\n📐 Area: ')
            .replace(/Budget:\s*/g, '\n💰 Budget: ')
            .replace(/Status:\s*/g, '\n📅 Status: ')
            .replace(/View Details:/g, '\n🔗 View Details: ')
            .replace(/\s+/g, ' ')
            .replace(/\n+/g, '\n')
            .trim();

        if (formatted.includes('Found') && formatted.includes('properties')) {
            formatted = formatted.replace(/Found \d+ properties for you:/, 'I found some properties for you:\n\n');
            formatted = formatted.replace(/\n\n+/g, '\n\n');
        }

        return formatted;
    }

    function showTyping() {
        console.log('Showing typing indicator');
        typingIndicator.style.display = 'flex';
        typingIndicator.classList.add('show');
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }

    function hideTyping() {
        console.log('Hiding typing indicator');
        typingIndicator.classList.remove('show');
        setTimeout(() => {
            typingIndicator.style.display = 'none';
        }, 300);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Optional: Keyboard shortcut Ctrl + Space to open chat
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.code === 'Space') {
            e.preventDefault();
            if (!chatOverlay.classList.contains('show')) {
                chatBubble.click();
            }
        }
    });

    // Make makeCall function globally available
    window.makeCall = makeCall;
});
 // connected_chatManager.js - 处理聊天界面和消息

export class ChatManager {
    constructor(sendMessageCallback) {
        this.chatContainer = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-btn');
        this.sendMessageCallback = sendMessageCallback;
    }

    // Initialize chat manager
    init() {
        // Bind send button click event
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        // Bind input box enter key event
        this.userInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                this.sendMessage();
            }
        });

        // Adjust input box height
        this.userInput.addEventListener('input', () => {
            this.adjustTextareaHeight();
        });
    }

    // Send message
    sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;

        // Call callback function to send message
        if (this.sendMessageCallback) {
            this.sendMessageCallback(message);
        }

        // Clear and adjust input box
        this.userInput.value = '';
        this.adjustTextareaHeight();
    }

    // Add user message
    addUserMessage(message) {
        const messageElement = this.createMessageElement('user-message', message);
        this.chatContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    // Add AI message
    addAIMessage(message) {
        const messageElement = this.createMessageElement('ai-message', message);
        this.chatContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    // Add system message
    addSystemMessage(message) {
        const messageElement = this.createMessageElement('system-message', message);
        this.chatContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    // Create message element
    createMessageElement(className, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // Process Markdown format
        const formattedContent = this.formatMessage(content);
        contentDiv.innerHTML = formattedContent;

        messageDiv.appendChild(contentDiv);
        return messageDiv;
    }

    // Format message content (process simple Markdown)
    formatMessage(content) {
        if (!content) return '';

        // Escape HTML special characters
        let formatted = content
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // Process code blocks
        formatted = formatted.replace(/\`\`\`([^\`]+)\`\`\`/g, '<pre><code>$1</code></pre>');

        // Process inline code
        formatted = formatted.replace(/\`([^\`]+)\`/g, '<code>$1</code>');

        // Process bold
        formatted = formatted.replace(/\*\*([^\*]+)\*\*/g, '<strong>$1</strong>');

        // Process italic
        formatted = formatted.replace(/\*([^\*]+)\*/g, '<em>$1</em>');

        // Process line breaks
        formatted = formatted.replace(/\n/g, '<br>');

        return formatted;
    }

    // Clear all messages
    clearMessages() {
        this.chatContainer.innerHTML = '';
    }

    // Scroll to bottom
    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    // Adjust input box height
    adjustTextareaHeight() {
        this.userInput.style.height = 'auto';
        this.userInput.style.height = (this.userInput.scrollHeight) + 'px';
    }
}

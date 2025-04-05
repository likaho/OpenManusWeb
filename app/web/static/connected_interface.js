// connected_interface.js - Main JavaScript file, responsible for initializing and coordinating other modules

// Import various manager classes
import { WebSocketManager } from '/static/connected_websocketManager.js';
import { ChatManager } from '/static/connected_chatManager.js';
import { ThinkingManager } from '/static/connected_thinkingManager.js';
import { WorkspaceManager } from '/static/connected_workspaceManager.js';
import { FileViewerManager } from '/static/connected_fileViewerManager.js';
import { initLanguage, setLanguage, updatePageTexts, t } from '/static/i18n.js';

// Main application class
class App {
    constructor() {
        this.sessionId = null;
        this.isProcessing = false;

        // Initialize various managers
        this.websocketManager = new WebSocketManager(this.handleWebSocketMessage.bind(this));
        this.chatManager = new ChatManager(this.handleSendMessage.bind(this));
        this.thinkingManager = new ThinkingManager();
        this.workspaceManager = new WorkspaceManager(this.handleFileClick.bind(this));
        this.fileViewerManager = new FileViewerManager();

        // Bind UI events
        this.bindEvents();
    }

    // Initialize application
    init() {
        console.log('Initializing OpenManus Web application...');

        // Initialize language settings
        const currentLang = initLanguage();
        document.getElementById('language-selector').value = currentLang;
        updatePageTexts();
        
        // Initialize managers
        this.chatManager.init();
        this.thinkingManager.init();
        this.workspaceManager.init();
        this.fileViewerManager.init();

        // Load workspace files
        this.loadWorkspaceFiles();
    }

    // Bind UI events
    bindEvents() {
        // Bind send button
        document.getElementById('send-btn').addEventListener('click', () => {
            const message = document.getElementById('input-text').value.trim();
            if (message) {
                this.handleSendMessage(message);
            }
        });

        // Bind stop button
        document.getElementById('stop-btn').addEventListener('click', () => {
            this.stopProcessing();
        });

        // Bind file refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadWorkspaceFiles();
        });
    }

    // Update dynamically generated text
    updateDynamicTexts() {
        // Update status indicator
        const statusIndicator = document.getElementById('status-indicator');
        statusIndicator.textContent = t('ready');

        // Update refresh countdown
        const refreshCountdown = document.getElementById('refresh-countdown');
        if (refreshCountdown) {
            const seconds = refreshCountdown.textContent.match(/\d+/g);
            if (seconds && seconds.length > 0) {
                refreshCountdown.textContent = t('refresh_countdown', { seconds: seconds[0] });
            }
        }
    }

    // Handle sending messages
    async handleSendMessage(message) {
        if (this.isProcessing) {
            console.log('Processing in progress, please wait...');
            return;
        }

        this.isProcessing = true;
        document.getElementById('send-btn').disabled = true;
        document.getElementById('stop-btn').disabled = false;
        document.getElementById('status-indicator').textContent = t('processing_request');

        try {
            // Send API request to create new session
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: message }),
            });

            if (!response.ok) {
                throw new Error(t('api_error', { status: response.status }));
            }

            const data = await response.json();
            this.sessionId = data.session_id;
            this.chatManager.startSession(this.sessionId);
        } catch (error) {
            console.error('Error:', error);
            this.isProcessing = false;
            document.getElementById('send-btn').disabled = false;
            document.getElementById('stop-btn').disabled = true;
            document.getElementById('status-indicator').textContent = t('error_occurred');
        }
    }

    // Handle WebSocket messages
    handleWebSocketMessage(data) {
        if (data.type === 'thinking') {
            this.thinkingManager.updateThinking(data);
        } else if (data.type === 'chat') {
            this.chatManager.updateChat(data);
        } else if (data.type === 'file') {
            this.workspaceManager.updateFile(data);
        }
    }

    // Stop processing
    stopProcessing() {
        if (this.sessionId) {
            fetch(`/api/chat/${this.sessionId}/stop`, { method: 'POST' });
        }
        this.isProcessing = false;
        document.getElementById('send-btn').disabled = false;
        document.getElementById('stop-btn').disabled = true;
        document.getElementById('status-indicator').textContent = t('stopped');
    }

    // Load workspace files
    loadWorkspaceFiles() {
        this.workspaceManager.loadFiles();
    }

    // Handle file click
    handleFileClick(filePath) {
        this.fileViewerManager.showFile(filePath);
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.init();
});
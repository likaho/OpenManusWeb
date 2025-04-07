// i18n.js - Internationalization module, manages Chinese and English translations

// Supported languages
export const SUPPORTED_LANGUAGES = {
    'en-US': 'English',
    'zh-CN': '中文'
};

// Translation texts
export const translations = {
    // Chinese translation
    'zh-CN': {
        // Page title and header
        'page_title': 'OpenManus Web - 网页版',
        'app_title': 'OpenManus',
        'app_subtitle': 'AI智能助手 - 网页版',
        
        // 主要区域标题
        'processing_progress': '处理进度',
        'ai_thinking_process': 'AI思考过程',
        'workspace_files': '工作区文件',
        'conversation': '对话',
        
        // 按钮和控件
        'auto_scroll': '自动滚动',
        'clear': '清空',
        'refresh': '刷新',
        'send': '发送',
        'stop': '停止',
        'close': '关闭',
        
        // 状态和提示
        'records_count': '{count} records',
        'refresh_countdown': '{seconds}秒后刷新',
        'processing_request': '正在处理您的请求...',
        'processing_stopped': '处理已停止',
        'file_name': '文件名',
        
        // 输入框占位符
        'input_placeholder': '输入您的问题或指令...',
        
        // 页脚
        'ui_made_by': 'Web界面制作:',
        'powered_by': 'Powered by OpenManus -',
        
        // 错误消息
        'api_error': 'API错误: {status}',
        'send_message_error': '发送消息错误: {message}',
        'stop_processing_error': '停止处理错误: {message}',
        'load_workspace_error': '加载工作区文件错误: {message}',
        'load_file_error': '加载文件内容错误: {message}',
        
        // 系统消息
        'error_occurred': '发生错误: {message}',
        'processing_in_progress': '正在处理中，请等待...',
        
        // 语言切换
        'language': '语言',
        'switch_language': '切换语言'
    },
    
    // English translation
    'en-US': {
        // Page title and header
        'page_title': 'OpenManus Web - Web Version',
        'app_title': 'OpenManus',
        'app_subtitle': 'AI Assistant - Web Version',
        
        // Main section titles
        'processing_progress': 'Processing Progress',
        'ai_thinking_process': 'AI Thinking Process',
        'workspace_files': 'Workspace Files',
        'conversation': 'Conversation',
        
        // Buttons and controls
        'auto_scroll': 'Auto Scroll',
        'clear': 'Clear',
        'refresh': 'Refresh',
        'send': 'Send',
        'stop': 'Stop',
        'close': 'Close',
        
        // Status and prompts
        'records_count': '{count} Records',
        'refresh_countdown': 'Refresh in {seconds}s',
        'processing_request': 'Processing your request...',
        'processing_stopped': 'Processing stopped',
        'file_name': 'File Name',
        
        // Input placeholder
        'input_placeholder': 'Enter your question or instruction...',
        
        // Footer
        'ui_made_by': 'UI Made by:',
        'powered_by': 'Powered by OpenManus -',
        
        // Error messages
        'api_error': 'API Error: {status}',
        'send_message_error': 'Send message error: {message}',
        'stop_processing_error': 'Stop processing error: {message}',
        'load_workspace_error': 'Load workspace files error: {message}',
        'load_file_error': 'Load file content error: {message}',
        
        // System messages
        'error_occurred': 'Error occurred: {message}',
        'processing_in_progress': 'Processing in progress, please wait...',
        
        // Language switch
        'language': 'Language',
        'switch_language': 'Switch Language'
    }
};

// Current language
let currentLanguage = 'en-US';

// Get browser language
export function getBrowserLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;
    // If browser language starts with 'zh', return Chinese, otherwise return English
    return browserLang.startsWith('zh') ? 'zh-CN' : 'en-US';
}

// Set current language
export function setLanguage(lang) {
    if (translations[lang]) {
        currentLanguage = lang;
        // Save language setting to localStorage
        localStorage.setItem('openmanus_language', lang);
        return true;
    }
    return false;
}

// Get current language
export function getCurrentLanguage() {
    return currentLanguage;
}

// Initialize language settings
export function initLanguage() {
    // First try to get language setting from localStorage
    const savedLang = localStorage.getItem('openmanus_language');
    if (savedLang && translations[savedLang]) {
        currentLanguage = savedLang;
    } else {
        // If no saved language setting, use browser language
        currentLanguage = getBrowserLanguage();
    }
    return currentLanguage;
}

// Get translation text
export function t(key, params = {}) {
    // Get current language translation
    const translation = translations[currentLanguage];
    
    // If translation not found, try English, if English also not found, return key name
    let text = translation[key] || translations['en-US'][key] || key;
    
    // Replace parameters
    Object.keys(params).forEach(param => {
        text = text.replace(`{${param}}`, params[param]);
    });
    
    return text;
}

// Update text of all elements with data-i18n attribute
export function updatePageTexts() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        
        // If element is input or textarea, update placeholder
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            if (element.getAttribute('placeholder')) {
                element.setAttribute('placeholder', t(key));
            }
        } else {
            // Otherwise update internal text
            element.textContent = t(key);
        }
    });
    
    // Update page title
    document.title = t('page_title');
}

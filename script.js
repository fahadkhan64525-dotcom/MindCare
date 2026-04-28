// API Configuration
const API_BASE_URL = 'http://localhost:5000';
const API_TIMEOUT = 10000; // 10 seconds
const MAX_RETRIES = 2;

// Show error notification
function showError(message) {
    const notification = document.createElement('div');
    notification.className = 'notification notification-error';
    notification.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="notification-close">&times;</button>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

// Show success notification
function showSuccess(message) {
    const notification = document.createElement('div');
    notification.className = 'notification notification-success';
    notification.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="notification-close">&times;</button>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// API call with timeout and retry logic
async function fetchWithRetry(url, options = {}, retries = MAX_RETRIES) {
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), API_TIMEOUT);
        
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        
        clearTimeout(timeout);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        if (error.name === 'AbortError') {
            if (retries > 0) {
                console.log(`Request timeout, retrying... (${MAX_RETRIES - retries + 1}/${MAX_RETRIES})`);
                return fetchWithRetry(url, options, retries - 1);
            }
            throw new Error('Request timeout. Please check your connection and try again.');
        }
        
        if (retries > 0 && error.message.includes('Failed to fetch')) {
            console.log(`Network error, retrying... (${MAX_RETRIES - retries + 1}/${MAX_RETRIES})`);
            return fetchWithRetry(url, options, retries - 1);
        }
        
        throw error;
    }
}

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    // Load history if on dashboard
    if (document.getElementById('history-container')) {
        loadHistory();
    }
    
    // Mood selector functionality
    setupMoodSelector();
    
    // Modal functionality
    setupModal();
    
    // Chat functionality
    setupChat();
    
    // Form submission
    setupForms();

    // UI animations (anime.js)
    setupAnimations();
}); 

// Setup Mood Selector
function setupMoodSelector() {
    const moodOptions = document.querySelectorAll('.mood-option');
    moodOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all
            moodOptions.forEach(opt => opt.classList.remove('selected'));
            // Add to clicked
            this.classList.add('selected');
            // Update hidden input
            const input = document.getElementById('mood-input');
            if (input) {
                input.value = this.dataset.mood;
            }

            // small selection animation (requires anime.js)
            if (window.anime) {
                anime({ targets: this, scale: [1, 1.06, 1], duration: 650, easing: 'easeOutElastic(1, .6)' });
                anime({ targets: this.querySelector('i'), rotate: [0, 10, -6, 0], duration: 800, easing: 'easeOutCubic' });
            }
        });

        // keyboard accessibility (Enter / Space)
        option.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.click(); }
        });
    });
} 

// Load History
async function loadHistory() {
    try {
        const data = await fetchWithRetry(`${API_BASE_URL}/history`);
        
        const container = document.getElementById('history-container');
        if (!data.history || data.history.length === 0) {
            container.innerHTML = '<p>No entries yet. <a href="mood-tracker.html">Log your first mood!</a></p>';
            return;
        }
        
        let html = '<div class="history-list">';
        data.history.forEach(entry => {
            const moodIcons = {
                'happy': '😊',
                'neutral': '😐',
                'sad': '😔',
                'stressed': '😫'
            };
            
            html += `
                <div class="history-entry">
                    <div class="entry-date">${entry.date}</div>
                    <div class="entry-mood">${moodIcons[entry.mood] || '❓'} ${entry.mood}</div>
                    <div class="entry-stress stress-${entry.stress_level.toLowerCase()}">${entry.stress_level}</div>
                    <div class="entry-details">
                        Sleep: ${entry.sleep}h • Screen: ${entry.screen_time}h • Work: ${entry.workload_hours}h
                    </div>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading history:', error);
        const container = document.getElementById('history-container');
        if (container) {
            container.innerHTML = `
                <div style="padding: 20px; background: linear-gradient(135deg, rgba(255,243,205,0.04), rgba(255,250,240,0.02)); border-radius: 8px; color: var(--text-muted);">
                    <i class="fas fa-exclamation-circle"></i> 
                    Unable to load history. Please try again later.
                </div>
            `;
        }
    }
}

// Setup Forms
function setupForms() {
    const moodForm = document.getElementById('mood-form');
    if (moodForm) {
        moodForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalHtml = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            
            try {
                // Validate inputs
                const mood = document.getElementById('mood-input').value;
                const sleep = parseFloat(document.getElementById('sleep').value);
                const screenTime = parseFloat(document.getElementById('screen-time').value);
                const workload = parseFloat(document.getElementById('workload').value);
                
                if (!mood) {
                    throw new Error('Please select a mood');
                }
                
                if (isNaN(sleep) || sleep < 0 || sleep > 24) {
                    throw new Error('Sleep hours must be between 0 and 24');
                }
                
                if (isNaN(screenTime) || screenTime < 0 || screenTime > 24) {
                    throw new Error('Screen time must be between 0 and 24');
                }
                
                if (isNaN(workload) || workload < 0 || workload > 24) {
                    throw new Error('Workload hours must be between 0 and 24');
                }
                
                const formData = {
                    mood: mood,
                    sleep: sleep,
                    screen_time: screenTime,
                    workload: workload
                };
                
                const result = await fetchWithRetry(`${API_BASE_URL}/predict`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                if (result.error) {
                    throw new Error(result.error);
                }
                
                displayResult(result);
                showSuccess('Stress analysis completed!');
                
            } catch (error) {
                showError('Error: ' + error.message);
                console.error('Form submission error:', error);
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalHtml;
            }
        });
    }
}

// Display Prediction Result
function displayResult(result) {
    const container = document.getElementById('result-container') || document.body;
    
    let resultBox = document.getElementById('stress-result');
    if (!resultBox) {
        resultBox = document.createElement('div');
        resultBox.id = 'stress-result';
        container.appendChild(resultBox);
    }
    
    const stressClass = `result-${result.stress_level.toLowerCase()}`;
    
    let html = `
        <div class="result-box ${stressClass}">
            <h2><i class="fas fa-chart-bar"></i> Stress Analysis</h2>
            <div class="stress-level">${result.stress_level} Stress</div>
            <p>Based on your input, you're experiencing <strong>${result.stress_level.toLowerCase()} stress</strong>.</p>
    `;
    
    if (result.emergency_message) {
        html += `
            <div class="emergency-alert">
                <i class="fas fa-exclamation-circle"></i>
                <h3>Important Notice</h3>
                <p>${result.emergency_message}</p>
                <button onclick="window.open('tel:988')" class="emergency-btn">
                    <i class="fas fa-phone"></i> Call 988 Now
                </button>
            </div>
        `;
    }
    
    if (result.tips && result.tips.length > 0) {
        html += `<div class="tips-section"><h3><i class="fas fa-lightbulb"></i> Personalized Tips</h3><ul>`;
        result.tips.forEach(tip => {
            html += `<li>${tip}</li>`;
        });
        html += `</ul></div>`;
    }
    
    html += `
        <div class="result-actions">
            <button onclick="loadHistory()" class="btn-secondary">
                <i class="fas fa-history"></i> View History
            </button>
            <button onclick="window.location.href='chatbot.html'" class="btn-primary">
                <i class="fas fa-robot"></i> Chat with Support
            </button>
        </div>
    </div>`;
    
    resultBox.innerHTML = html;
    resultBox.scrollIntoView({ behavior: 'smooth' });
}

// Setup Chat
function setupChat() {
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        const chatContainer = document.getElementById('chat-container');
        const chatInput = document.getElementById('chat-input');
        
        // Add initial bot message
        addBotMessage("Hello! I'm your mental health support chatbot. I'm here to listen and offer supportive suggestions. Remember, I'm not a medical professional. How are you feeling today?");
        
        chatForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const message = chatInput.value.trim();
            if (!message) {
                showError('Please type a message first');
                return;
            }
            
            // Add user message
            addUserMessage(message);
            chatInput.value = '';
            
            // Show typing indicator
            const typingIndicator = addTypingIndicator();
            
            try {
                const data = await fetchWithRetry(`${API_BASE_URL}/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: message })
                });
                
                // Remove typing indicator
                typingIndicator.remove();
                
                // Add bot response
                addBotMessage(data.response);
                
                // Add disclaimer on first response
                if (!window.disclaimerShown) {
                    addBotMessage(`<strong>Note:</strong> ${data.note} ${data.disclaimer}`);
                    window.disclaimerShown = true;
                }
                
            } catch (error) {
                typingIndicator.remove();
                console.error('Chat error:', error);
                
                // Provide fallback responses
                const fallbackResponses = [
                    "I understand you're reaching out. Sometimes just expressing how you feel can be helpful.",
                    "Thank you for sharing. Remember to be kind to yourself today.",
                    "I hear you. Taking slow, deep breaths can sometimes help create a moment of calm.",
                    "That sounds challenging. Would you like to try a quick grounding exercise?"
                ];
                
                const randomResponse = fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];
                addBotMessage(randomResponse);
            }
        });
    }
}

// Chat Helper Functions
function addUserMessage(text) {
    const container = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `<p>${text}</p>`;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function addBotMessage(text) {
    const container = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.innerHTML = `<p>${text}</p>`;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function addTypingIndicator() {
    const container = document.getElementById('chat-container');
    const indicator = document.createElement('div');
    indicator.className = 'message bot-message typing-indicator';
    indicator.innerHTML = '<p><i class="fas fa-ellipsis-h"></i> Thinking...</p>';
    container.appendChild(indicator);
    container.scrollTop = container.scrollHeight;
    return indicator;
}

// UI animations (uses anime.js when available)
function setupAnimations() {
    if (!window.anime) return;

    // Hero/title
    const heroTitle = document.querySelector('header h1');
    const heroSub = document.querySelector('header .subtitle');
    anime.timeline({ easing: 'easeOutExpo' })
        .add({ targets: heroTitle, translateY: [20,0], opacity: [0,1], duration: 700 })
        .add({ targets: heroSub, translateY: [10,0], opacity: [0,1], duration: 600 }, '-=400');

    // Cards
    anime({ targets: '.stat-card', translateY: [20,0], opacity: [0,1], delay: anime.stagger(120), duration: 600, easing: 'easeOutCubic' });
    anime({ targets: '.action-card', translateY: [12,0], opacity: [0,1], delay: anime.stagger(140), duration: 700 });

    // Mood selector
    anime({ targets: '.mood-option', translateY: [10,0], opacity: [0,1], delay: anime.stagger(80), duration: 600 });

    // Chat and chips
    anime({ targets: '.chat-header, .chat-page .bot-message:first-child', translateY: [10,0], opacity: [0,1], duration: 700, delay: 200 });
    anime({ targets: '.question-chip', scale: [0.96,1], opacity: [0,1], delay: anime.stagger(60), duration: 450 });

    // Progress fill (mood tracker)
    const progress = document.querySelector('.progress-fill');
    if (progress) anime({ targets: progress, width: [0, '33%'], easing: 'easeOutQuart', duration: 800 });

    // gentle floating glow
    anime({ targets: '.action-card i, .chat-bot-icon, .stat-card > div', scale: [1,1.03,1], easing: 'easeInOutSine', duration: 2000, direction: 'alternate', loop: true });
}


// Modal Setup
function setupModal() {
    const modal = document.getElementById('tips-modal');
    const btn = document.getElementById('quick-tips-btn');
    const closeBtn = document.querySelector('.close');
    
    if (btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            showQuickTips();
        });
    }
    
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Show Quick Tips
async function showQuickTips() {
    const tips = [
        "Take a 5-minute break every hour to stretch and breathe deeply",
        "Practice gratitude: write down 3 things you're thankful for today",
        "Stay hydrated - even mild dehydration can affect mood",
        "Connect with someone you care about, even for a few minutes",
        "Get natural sunlight exposure in the morning if possible",
        "Try the 5-4-3-2-1 grounding technique: Name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste",
        "Digital detox: Schedule screen-free time each day",
        "Listen to calming music or nature sounds",
        "Practice mindful breathing: inhale for 4 counts, hold for 4, exhale for 6",
        "Create a relaxing bedtime routine to improve sleep quality"
    ];
    
    const tipsList = document.getElementById('tips-list');
    tipsList.innerHTML = '<ul>' + tips.map(tip => `<li>${tip}</li>`).join('') + '</ul>';
    
    document.getElementById('tips-modal').style.display = 'block';
}
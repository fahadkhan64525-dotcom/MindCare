"""
MindCare Mental Health Support API
A Flask-based REST API for mental health mood tracking and AI support
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import sqlite3
import json
from datetime import datetime, timedelta
import random
import logging
import os
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
MODEL_PATH = 'model.pkl'
DB_PATH = 'mental_health.db'
DB_TIMEOUT = 30

# Constants
VALID_MOODS = {'happy', 'neutral', 'sad', 'stressed'}
STRESS_LEVELS = {0: 'Low', 1: 'Medium', 2: 'High'}
MOOD_MAPPING = {'happy': 1, 'neutral': 2, 'sad': 3, 'stressed': 4}

# Input validation defaults
MIN_SLEEP = 0
MAX_SLEEP = 24
MIN_SCREEN_TIME = 0
MAX_SCREEN_TIME = 24
MIN_WORKLOAD = 0
MAX_WORKLOAD = 24

# Load ML model
model = None
try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    logger.info("ML model loaded successfully")
except FileNotFoundError:
    logger.warning(f"Model not found at {MODEL_PATH}. Run train_model.py first.")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")

# Safety disclaimer
DISCLAIMER = """
⚠️ IMPORTANT DISCLAIMER:
This is a demonstration tool for educational purposes only.
It is NOT a medical device and does NOT provide medical advice.
If you're experiencing a mental health crisis, please contact a professional:
• National Suicide Prevention Lifeline: 988
• Crisis Text Line: Text HOME to 741741
"""

# Enhanced chatbot responses with more variety
CHATBOT_RESPONSES = {
    'stress': [
        "Deep breathing can help. Try inhaling for 4 seconds, holding for 4, exhaling for 6.",
        "Taking a short walk outside might help clear your mind and reduce stress.",
        "Remember to hydrate and take regular breaks from screens.",
        "Try progressive muscle relaxation: tense and release each muscle group.",
        "Consider doing something you enjoy, even for just 10 minutes.",
        "Breaking tasks into smaller, manageable pieces can make things feel less overwhelming."
    ],
    'sad': [
        "It's okay to feel sad sometimes. This emotion will pass. Would you like to try a grounding exercise?",
        "Talking to a friend or writing in a journal can help process emotions.",
        "Small acts of self-care, like a warm drink, can sometimes help.",
        "Consider spending time in nature or with someone you care about.",
        "Remember: your feelings are valid, and it's okay to ask for help.",
        "Try the 5-4-3-2-1 technique: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste."
    ],
    'sleep': [
        "Try maintaining a consistent sleep schedule, even on weekends.",
        "Avoid screens 1 hour before bed for better sleep quality.",
        "A cool, dark room often promotes better sleep.",
        "Try reading or meditation before bed to help you wind down.",
        "Limit caffeine intake after 2 PM for better sleep quality.",
        "A gentle yoga routine in the evening can improve sleep quality."
    ],
    'work': [
        "The Pomodoro technique (25min work, 5min break) can help manage workload.",
        "Prioritize tasks using the Eisenhower Matrix: urgent/important.",
        "Remember to celebrate small victories throughout the day.",
        "Set realistic goals and don't be afraid to delegate if possible.",
        "Take regular breaks to maintain focus and productivity.",
        "Remember: done is better than perfect. Progress over perfection."
    ],
    'anxiety': [
        "Anxiety is manageable. Try grounding techniques like the 5-4-3-2-1 method.",
        "Box breathing can help calm anxiety: 4 counts in, hold 4, out 4, hold 4.",
        "Remember: worry is about the future, stay present with what's happening now.",
        "Physical exercise can significantly reduce anxiety symptoms.",
        "Talking to someone you trust about your anxiety can help."
    ],
    'default': [
        "I'm here to listen. Could you tell me more about how you're feeling?",
        "Remember, it's okay to not be okay. Taking it one step at a time is enough.",
        "Would you like to try a quick mindfulness exercise? Close your eyes and name 3 things you can hear.",
        "You're not alone in what you're feeling. Many people experience similar challenges.",
        "That sounds challenging. Remember to be kind to yourself."
    ]
}

# Database functions
def init_db():
    """Initialize the SQLite database with required tables"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS mood_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                mood TEXT NOT NULL,
                sleep_hours REAL NOT NULL,
                screen_time REAL NOT NULL,
                workload_hours REAL NOT NULL,
                stress_prediction TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        
        # Create index for faster queries
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_date ON mood_entries(date)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

def validate_input(data):
    """
    Validate input data for mood prediction
    Returns: (is_valid: bool, errors: dict)
    """
    errors = {}
    
    # Validate mood
    if 'mood' not in data:
        errors['mood'] = 'Mood is required'
    elif data['mood'].lower() not in VALID_MOODS:
        errors['mood'] = f'Mood must be one of: {", ".join(VALID_MOODS)}'
    
    # Validate sleep
    try:
        sleep = float(data.get('sleep', 0))
        if not (MIN_SLEEP <= sleep <= MAX_SLEEP):
            errors['sleep'] = f'Sleep must be between {MIN_SLEEP} and {MAX_SLEEP}'
    except (ValueError, TypeError):
        errors['sleep'] = 'Sleep must be a number'
    
    # Validate screen time
    try:
        screen_time = float(data.get('screen_time', 0))
        if not (MIN_SCREEN_TIME <= screen_time <= MAX_SCREEN_TIME):
            errors['screen_time'] = f'Screen time must be between {MIN_SCREEN_TIME} and {MAX_SCREEN_TIME}'
    except (ValueError, TypeError):
        errors['screen_time'] = 'Screen time must be a number'
    
    # Validate workload
    try:
        workload = float(data.get('workload', 0))
        if not (MIN_WORKLOAD <= workload <= MAX_WORKLOAD):
            errors['workload'] = f'Workload must be between {MIN_WORKLOAD} and {MAX_WORKLOAD}'
    except (ValueError, TypeError):
        errors['workload'] = 'Workload must be a number'
    
    return len(errors) == 0, errors

# API Routes
@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        'message': 'MindCare Mental Health Support API',
        'status': 'active',
        'version': '1.0.0',
        'endpoints': {
            'POST /predict': 'Get stress level prediction',
            'POST /chat': 'Chat with support bot',
            'GET /history': 'Get mood history',
            'GET /health': 'Health check'
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    db_status = 'connected'
    try:
        conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
        conn.execute('SELECT 1')
        conn.close()
    except Exception as e:
        db_status = f'error: {str(e)}'
        logger.error(f"Database health check failed: {str(e)}")
    
    return jsonify({
        'status': 'healthy' if db_status == 'connected' else 'degraded',
        'database': db_status,
        'model': 'loaded' if model else 'not loaded',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/predict', methods=['POST'])
def predict_stress():
    """
    Predict stress level based on user input
    Expected JSON: {mood, sleep, screen_time, workload}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Validate input
        is_valid, errors = validate_input(data)
        if not is_valid:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Extract and convert features
        sleep = float(data['sleep'])
        screen_time = float(data['screen_time'])
        workload = float(data['workload'])
        mood = MOOD_MAPPING.get(data['mood'].lower(), 2)
        
        # Make prediction
        stress_prediction = None
        confidence = None
        
        if model:
            features = [[sleep, screen_time, workload, mood]]
            stress_prediction = model.predict(features)[0]
            
            # Get prediction probabilities if available
            try:
                probabilities = model.predict_proba(features)[0]
                confidence = float(max(probabilities))
            except:
                pass
        else:
            # Fallback rule-based prediction
            score = 0
            if sleep < 6:
                score += 1
            if screen_time > 8:
                score += 1
            if workload > 10:
                score += 1
            if mood in [3, 4]:
                score += 1
            stress_prediction = min(score, 2)
            logger.warning("Using fallback rule-based prediction")
        
        stress_result = STRESS_LEVELS[stress_prediction]
        
        # Store in database
        try:
            store_mood_entry(
                date=datetime.now().strftime('%Y-%m-%d'),
                mood=data['mood'],
                sleep=sleep,
                screen_time=screen_time,
                workload=workload,
                stress_prediction=stress_result
            )
        except Exception as e:
            logger.error(f"Error storing mood entry: {str(e)}")
        
        # Check for emergency situation
        emergency_msg = None
        if stress_result == 'High' and (sleep < 4 or data['mood'].lower() in ['stressed', 'sad']):
            emergency_msg = (
                "⚠️ You're showing signs of significant stress. "
                "Please consider reaching out to a mental health professional "
                "or call 988 if you need immediate support."
            )
            logger.warning(f"Emergency indicator detected for user")
        
        response = {
            'stress_level': stress_result,
            'emergency_message': emergency_msg,
            'tips': get_wellness_tips(stress_result, sleep, screen_time, workload),
            'summary': {
                'sleep_hours': sleep,
                'screen_time_hours': screen_time,
                'workload_hours': workload,
                'mood': data['mood']
            }
        }
        
        if confidence:
            response['confidence'] = round(confidence, 2)
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in predict_stress: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def store_mood_entry(date, mood, sleep, screen_time, workload, stress_prediction):
    """Store mood entry in database"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
        c = conn.cursor()
        c.execute('''
            INSERT INTO mood_entries 
            (date, mood, sleep_hours, screen_time, workload_hours, stress_prediction)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, mood, sleep, screen_time, workload, stress_prediction))
        conn.commit()
        conn.close()
        logger.info(f"Mood entry stored: {mood} - {stress_prediction}")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise

def get_wellness_tips(stress_level, sleep, screen_time, workload):
    """Generate personalized wellness tips"""
    tips = []
    
    if sleep < 7:
        tips.append("💤 Aim for 7-9 hours of sleep. Establish a consistent bedtime routine.")
    elif sleep < 5:
        tips.append("🚨 Severe sleep deprivation detected. Prioritize sleep for your health.")
    
    if screen_time > 8:
        tips.append("📱 High screen time detected. Take regular screen breaks (20-20-20 rule).")
    
    if workload > 9:
        tips.append("💼 Heavy workload detected. Break tasks into smaller chunks and prioritize.")
    
    if stress_level == 'High':
        tips.append("🧘 Try the 4-7-8 breathing technique: inhale 4, hold 7, exhale 8.")
        tips.append("🚶 Physical activity, even a 10-minute walk, can significantly reduce stress.")
    elif stress_level == 'Medium':
        tips.append("✅ You're managing well. Continue your healthy habits.")
    else:
        tips.append("🌟 Great job maintaining good wellness habits! Keep it up.")
    
    if not tips:
        tips.append("Remember to take breaks throughout the day and practice self-care.")
    
    return tips

@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for conversational support
    Expected JSON: {message: string}
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message = str(data['message']).lower().strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Sanitize message (prevent injection)
        message = re.sub(r'[^\w\s\']', '', message)[:500]  # Limit to 500 chars
        
        # Determine response category
        response_key = 'default'
        
        keywords = {
            'stress': ['stress', 'overwhelm', 'anxious', 'panic', 'tension'],
            'sad': ['sad', 'down', 'depress', 'unhappy', 'blue', 'low'],
            'sleep': ['sleep', 'tired', 'exhaust', 'insomnia', 'rest'],
            'work': ['work', 'busy', 'overwork', 'deadline', 'project'],
            'anxiety': ['anxiety', 'worry', 'fear', 'nervous', 'concern']
        }
        
        for key, words in keywords.items():
            if any(word in message for word in words):
                response_key = key
                break
        
        response = random.choice(CHATBOT_RESPONSES[response_key])
        
        logger.info(f"Chat message processed: {response_key}")
        
        return jsonify({
            'response': response,
            'category': response_key,
            'disclaimer': 'I am a demo chatbot, not a mental health professional.',
            'note': 'For emergencies, please call 988 or contact a mental health professional.'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """
    Get user's mood history
    Query params: limit (default 10), days (optional, last N days)
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        days = request.args.get('days', None, type=int)
        
        # Validate limit
        limit = max(1, min(100, limit))  # Between 1 and 100
        
        conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        query = 'SELECT * FROM mood_entries'
        params = []
        
        # Filter by days if specified
        if days and days > 0:
            date_threshold = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            query += ' WHERE date >= ?'
            params.append(date_threshold)
        
        query += ' ORDER BY date DESC LIMIT ?'
        params.append(limit)
        
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'id': row['id'],
                'date': row['date'],
                'mood': row['mood'],
                'sleep': row['sleep_hours'],
                'screen_time': row['screen_time'],
                'workload': row['workload_hours'],
                'stress_level': row['stress_prediction'],
                'timestamp': row['timestamp']
            })
        
        logger.info(f"History retrieved: {len(history)} entries")
        
        return jsonify({
            'history': history,
            'count': len(history),
            'limit': limit
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/history/<int:entry_id>', methods=['DELETE'])
def delete_history_entry(entry_id):
    """Delete a specific mood entry"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
        c = conn.cursor()
        c.execute('DELETE FROM mood_entries WHERE id = ?', (entry_id,))
        deleted = c.rowcount
        conn.commit()
        conn.close()
        
        if deleted == 0:
            return jsonify({'error': 'Entry not found'}), 404
        
        logger.info(f"History entry deleted: {entry_id}")
        return jsonify({'message': 'Entry deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting history entry: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/analytics', methods=['GET'])
def get_analytics():
    """
    Get analytics and insights about mood trends
    """
    try:
        conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
        c = conn.cursor()
        
        # Get statistics
        c.execute('''
            SELECT 
                mood,
                COUNT(*) as count,
                AVG(sleep_hours) as avg_sleep,
                AVG(screen_time) as avg_screen_time,
                AVG(workload_hours) as avg_workload,
                stress_prediction
            FROM mood_entries
            GROUP BY mood
        ''')
        
        analytics = {}
        for row in c.fetchall():
            mood = row[0]
            analytics[mood] = {
                'entries': row[1],
                'avg_sleep': round(row[2], 1) if row[2] else 0,
                'avg_screen_time': round(row[3], 1) if row[3] else 0,
                'avg_workload': round(row[4], 1) if row[4] else 0,
                'stress_level': row[5]
            }
        
        # Get stress level distribution
        c.execute('''
            SELECT stress_prediction, COUNT(*) as count
            FROM mood_entries
            GROUP BY stress_prediction
        ''')
        
        stress_distribution = {}
        for row in c.fetchall():
            stress_distribution[row[0]] = row[1]
        
        conn.close()
        
        logger.info("Analytics retrieved")
        
        return jsonify({
            'mood_analytics': analytics,
            'stress_distribution': stress_distribution,
            'total_entries': sum(a['entries'] for a in analytics.values())
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_analytics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 Error: {request.path}")
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 Error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

@app.before_request
def log_request():
    """Log incoming requests"""
    logger.debug(f"{request.method} {request.path}")

# Initialize database and start app
init_db()

if __name__ == '__main__':
    logger.info("Starting MindCare API Server on port 5000")
    app.run(debug=True, port=5000, host='0.0.0.0')

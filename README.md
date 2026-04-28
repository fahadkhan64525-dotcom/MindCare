# MindCare Backend API

A Flask-based REST API for mental health mood tracking and AI-powered support.

## Features

- 🧠 **ML-Powered Stress Prediction** - Logistic Regression and Random Forest models
- 💬 **Intelligent Chatbot** - Keyword-based conversational support with personalized responses
- 📊 **Mood Tracking** - Store and analyze mood history with analytics
- ✅ **Input Validation** - Comprehensive validation and error handling
- 📝 **Logging** - Detailed request and error logging
- 🔒 **Security** - Input sanitization and CORS protection
- 📈 **Analytics** - Track mood trends and wellness patterns

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
- Copy `.env.example` to `.env` (if available)
- Edit `.env` with your settings
- Or use default settings in `.env`

## Usage

### Train the Model

First time setup - train the stress prediction model:

```bash
python train_model.py
```

This will:
- Generate a synthetic dataset (if none exists)
- Train both Logistic Regression and Random Forest models
- Compare models and save the best one
- Display detailed metrics and cross-validation scores

### Run the API Server

```bash
python app.py
```

The API will start on `http://localhost:5000`

## API Endpoints

### 1. Home
```
GET /
```
Returns API information and available endpoints.

**Response:**
```json
{
  "message": "MindCare Mental Health Support API",
  "status": "active",
  "version": "1.0.0",
  "endpoints": {...}
}
```

---

### 2. Health Check
```
GET /health
```
Health status of the API and database.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "model": "loaded",
  "timestamp": "2024-02-06T10:30:00"
}
```

---

### 3. Predict Stress Level
```
POST /predict
```

Predict stress level based on daily metrics.

**Request:**
```json
{
  "mood": "stressed",
  "sleep": 5.5,
  "screen_time": 10,
  "workload": 12
}
```

**Parameters:**
- `mood` (string, required): One of: `happy`, `neutral`, `sad`, `stressed`
- `sleep` (float, required): Hours of sleep (0-24)
- `screen_time` (float, required): Hours on screens (0-24)
- `workload` (float, required): Hours of work/study (0-24)

**Response:**
```json
{
  "stress_level": "High",
  "emergency_message": "⚠️ You're showing signs of significant stress...",
  "confidence": 0.87,
  "tips": [
    "💤 Aim for 7-9 hours of sleep. Establish a consistent bedtime routine.",
    "🧘 Try the 4-7-8 breathing technique: inhale 4, hold 7, exhale 8.",
    "🚶 Physical activity, even a 10-minute walk, can significantly reduce stress."
  ],
  "summary": {
    "sleep_hours": 5.5,
    "screen_time_hours": 10,
    "workload_hours": 12,
    "mood": "stressed"
  }
}
```

---

### 4. Chat Support
```
POST /chat
```

Get supportive responses to messages.

**Request:**
```json
{
  "message": "I'm feeling very stressed about work"
}
```

**Response:**
```json
{
  "response": "Prioritize tasks using the Eisenhower Matrix: urgent/important.",
  "category": "work",
  "disclaimer": "I am a demo chatbot, not a mental health professional.",
  "note": "For emergencies, please call 988 or contact a mental health professional."
}
```

---

### 5. Get Mood History
```
GET /history?limit=10&days=30
```

Get user's mood tracking history.

**Query Parameters:**
- `limit` (int, optional): Number of entries (1-100, default: 10)
- `days` (int, optional): Filter to last N days

**Response:**
```json
{
  "history": [
    {
      "id": 1,
      "date": "2024-02-06",
      "mood": "stressed",
      "sleep": 5.5,
      "screen_time": 10,
      "workload": 12,
      "stress_level": "High",
      "timestamp": "2024-02-06T10:30:00"
    }
  ],
  "count": 1,
  "limit": 10
}
```

---

### 6. Delete History Entry
```
DELETE /history/<entry_id>
```

Delete a specific mood entry.

**Response:**
```json
{
  "message": "Entry deleted successfully"
}
```

---

### 7. Get Analytics
```
GET /analytics
```

Get mood trends and analytics.

**Response:**
```json
{
  "mood_analytics": {
    "happy": {
      "entries": 5,
      "avg_sleep": 7.8,
      "avg_screen_time": 4.2,
      "avg_workload": 6.5,
      "stress_level": "Low"
    }
  },
  "stress_distribution": {
    "Low": 8,
    "Medium": 12,
    "High": 5
  },
  "total_entries": 25
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

```json
{
  "error": "Validation failed",
  "details": {
    "mood": "Mood must be one of: happy, neutral, sad, stressed",
    "sleep": "Sleep must be between 0 and 24"
  }
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request (validation error)
- `404`: Not found
- `500`: Internal server error

## Configuration

Edit `.env` to customize:

```
FLASK_ENV=development          # Flask environment
API_PORT=5000                  # Server port
DB_PATH=mental_health.db       # Database file
MODEL_PATH=model.pkl           # Trained model file
MAX_MESSAGE_LENGTH=500         # Chat message limit
```

## Logging

Logs are saved to `app.log` with entries for:
- Request information
- Error details
- Model training metrics
- Database operations

View logs:
```bash
tail -f app.log
```

## Development

### Running with auto-reload:
```bash
python app.py
```

### Running with production server (Gunicorn):
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Testing the API:

Using curl:
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"mood":"stressed","sleep":5,"screen_time":10,"workload":12}'
```

Using Python requests:
```python
import requests

response = requests.post('http://localhost:5000/predict', json={
    'mood': 'stressed',
    'sleep': 5,
    'screen_time': 10,
    'workload': 12
})

print(response.json())
```

## Project Structure

```
backend/
├── app.py                  # Main Flask application
├── train_model.py          # Model training script
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration
├── mental_health.db        # SQLite database (created at runtime)
├── model.pkl              # Trained model (created after training)
├── scaler.pkl             # Feature scaler (created after training)
└── stress_dataset.csv     # Dataset for training
```

## Important Notes

⚠️ **Disclaimer**: This is an educational demonstration tool only. It is NOT a medical device and does NOT provide medical advice. If you're experiencing a mental health crisis, please contact:
- **988** - Suicide & Crisis Lifeline
- **741741** - Crisis Text Line (text HOME)
- Your local emergency services

## Performance Tips

- Keep database records for analytics
- Train model periodically with new data
- Monitor logs for errors and issues
- Use appropriate database indexes

## Future Improvements

- [ ] User authentication and sessions
- [ ] Advanced ML models (Neural Networks, Transformers)
- [ ] Real-time stress analysis
- [ ] Integration with professional resources
- [ ] Mobile app backend support
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Export mood history (PDF/CSV)

## Support

For issues or questions, refer to:
- Main project README
- API endpoint documentation
- Log files for error details

---

**Created with ❤️ for mental health awareness**

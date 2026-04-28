# MindCare Backend - Quick Start Guide

Get the backend running in 5 minutes! 🚀

## Option 1: Quick Start (Recommended)

### Step 1: Navigate to backend directory
```bash
cd backend
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Train the model (first time only)
```bash
python train_model.py
```

You'll see:
- ✅ Dataset generation
- ✅ Model training with metrics
- ✅ Cross-validation results
- ✅ Model saved to `model.pkl`

### Step 4: Start the API server
```bash
python run.py
```

Or using the startup script with training:
```bash
python run.py --train --port 5000
```

**That's it!** Your API is now running at: `http://localhost:5000`

---

## Option 2: Manual Setup (Advanced)

### 1. Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env` file and customize if needed:
```bash
cp .env .env.local  # (optional)
```

### 4. Train Model
```bash
python train_model.py
```

### 5. Start Server
```bash
python app.py
```

---

## Testing the API

### Option 1: Automatic Testing
```bash
python test_api.py
```

This runs:
- 10 comprehensive test suites
- All endpoints validation
- Error handling tests
- Input validation tests

### Option 2: Manual Testing with curl

**Test 1: Health Check**
```bash
curl http://localhost:5000/health
```

**Test 2: Predict Stress**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "mood": "stressed",
    "sleep": 5.5,
    "screen_time": 10,
    "workload": 12
  }'
```

**Test 3: Chat Support**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I Am feeling stressed about work"}'
```

**Test 4: Get History**
```bash
curl http://localhost:5000/history?limit=10
```

**Test 5: Analytics**
```bash
curl http://localhost:5000/analytics
```

### Option 3: Python Testing
```python
import requests

# Predict stress
response = requests.post('http://localhost:5000/predict', json={
    'mood': 'stressed',
    'sleep': 5,
    'screen_time': 10,
    'workload': 12
})

print(response.json())
```

---

## Common Issues

### Issue: Module not found (ModuleNotFoundError)
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Model not found warning
**Solution:** Train the model first
```bash
python train_model.py
```
(The API will still work with fallback rules)

### Issue: Port 5000 already in use
**Solution:** Use a different port
```bash
python run.py --port 8000
```

### Issue: Cannot connect to API
**Solution:** Check if server is running
```bash
# From another terminal:
curl http://localhost:5000/health
```

---

## Project Structure

```
backend/
├── app.py                    # Main Flask API
├── train_model.py            # ML model training
├── config.py                 # Configuration management
├── run.py                    # Startup script
├── test_api.py               # API tests
├── requirements.txt          # Dependencies
├── .env                      # Environment config
├── README.md                 # Full documentation
├── QUICKSTART.md             # This file
├── mental_health.db          # Database (created)
├── model.pkl                 # Trained model (created)
└── stress_dataset.csv        # Training data
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| POST | `/predict` | Predict stress level |
| POST | `/chat` | Chat support |
| GET | `/history` | Get mood history |
| DELETE | `/history/<id>` | Delete entry |
| GET | `/analytics` | Get analytics |

---

## Next Steps

1. **Frontend Integration**: Update frontend API URL if needed
2. **Model Improvement**: Train with real data
3. **Production Deployment**: Use Gunicorn
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
4. **Monitoring**: Check `app.log` for details

---

## Quick Commands Reference

```bash
# Training
python train_model.py              # Train the model

# Server
python app.py                      # Start server (simple)
python run.py                      # Start server (advanced)
python run.py --train              # Train & start
python run.py --port 8000          # Use port 8000
python run.py --debug              # Debug mode

# Testing
python test_api.py                 # Run all tests

# Production
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Logs
tail -f app.log                    # Watch logs
```

---

## Troubleshooting

**Q: How do I view the database?**
A: Use SQLite tools:
```bash
sqlite3 mental_health.db
> SELECT * FROM mood_entries;
> .exit
```

**Q: How do I reset everything?**
A: Delete these files and restart:
```bash
rm mental_health.db model.pkl scaler.pkl
python run.py --train
```

**Q: Can I use a different database?**
A: Yes, modify `DB_PATH` in `.env`

**Q: How do I update the model?**
A: Simply run training again:
```bash
python train_model.py
```

---

## Support

- **Full Documentation**: See `README.md`
- **Configuration**: See `.env` file
- **Logs**: Check `app.log`
- **Testing**: Run `test_api.py`

---

**Ready to go! 🎉**

Start the server: ```bash
python run.py
```

Access the API: `http://localhost:5000`

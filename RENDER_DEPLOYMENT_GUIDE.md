# 🚀 Render Deployment Guide

Complete guide to deploy your LLM Query-Retrieval System to Render for webhook submission.

## 📋 **Prerequisites**

1. **GitHub Account** - Your code needs to be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🔧 **Step 1: Prepare Your Repository**

### **1.1 Push Code to GitHub**
```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Deploy optimized LLM Query-Retrieval System"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

### **1.2 Required Files (Already Created)**
- ✅ `render.yaml` - Render configuration
- ✅ `requirements-fast.txt` - Optimized dependencies
- ✅ `main.py` - FastAPI application with webhook endpoint
- ✅ All service files

## 🌐 **Step 2: Deploy to Render**

### **2.1 Create New Web Service**
1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository from the list

### **2.2 Configure Deployment Settings**
- **Name**: `hackrx-api` (or your preferred name)
- **Environment**: `Python`
- **Build Command**: `pip install -r requirements-fast.txt`
- **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Plan**: `Free` (sufficient for testing)

### **2.3 Set Environment Variables**
Add these environment variables in Render dashboard:

| Variable | Value | Required |
|----------|-------|----------|
| `GEMINI_API_KEY` | `your_actual_gemini_api_key` | ✅ **REQUIRED** |
| `API_BEARER_TOKEN` | `87e1f87355284c19bac1880413d4a1e7cb868891939fc1c6d8227ee2c1b89cb0` | ✅ **REQUIRED** |
| `EMBEDDING_PROVIDER` | `gemini` | ✅ **REQUIRED** |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Optional |
| `MAX_TOKENS` | `4000` | Optional |
| `CHUNK_SIZE` | `1024` | Optional |

### **2.4 Deploy**
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Your service will be available at: `https://YOUR_SERVICE_NAME.onrender.com`

## 🔗 **Step 3: Get Your Webhook URL**

After successful deployment, your webhook URL will be:
```
https://YOUR_SERVICE_NAME.onrender.com/api/v1/hackrx/run
```

**Example:**
```
https://hackrx-api-xyz123.onrender.com/api/v1/hackrx/run
```

## 🧪 **Step 4: Test Your Deployment**

### **4.1 Health Check**
```bash
curl https://YOUR_SERVICE_NAME.onrender.com/health
```

### **4.2 Test Webhook Endpoint**
```bash
curl -X POST "https://YOUR_SERVICE_NAME.onrender.com/api/v1/hackrx/run" \
  -H "Authorization: Bearer 87e1f87355284c19bac1880413d4a1e7cb868891939fc1c6d8227ee2c1b89cb0" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
      "What is the grace period for premium payment?",
      "What is the waiting period for cataract surgery?"
    ]
  }'
```

## 📝 **Step 5: Submit Your Webhook**

### **5.1 Submission Format**
When submitting to the competition website:

**Webhook URL:**
```
https://YOUR_SERVICE_NAME.onrender.com/api/v1/hackrx/run
```

### **5.2 API Specification**
Your webhook supports:

**Endpoint:** `POST /api/v1/hackrx/run`

**Headers:**
```
Authorization: Bearer 87e1f87355284c19bac1880413d4a1e7cb868891939fc1c6d8227ee2c1b89cb0
Content-Type: application/json
```

**Request Body:**
```json
{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "Question 1?",
    "Question 2?"
  ]
}
```

**Response:**
```json
{
  "answers": [
    "Answer to question 1",
    "Answer to question 2"
  ]
}
```

## ⚡ **Performance Features**

Your deployed system includes:
- 🚀 **~30 second response time** (optimized)
- 📄 **PDF & DOCX support** (including Google Drive)
- 🔄 **Concurrent processing** for multiple questions
- 💾 **Document caching** for repeated requests
- 🎯 **Gemini-powered** embeddings and LLM

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **Build Failed**
   - Check `requirements-fast.txt` exists
   - Verify Python version compatibility

2. **Service Won't Start**
   - Check environment variables are set
   - Verify `GEMINI_API_KEY` is valid

3. **API Returns 401**
   - Check `API_BEARER_TOKEN` is set correctly
   - Verify authorization header format

4. **Slow Response**
   - Free tier has cold starts (~30s first request)
   - Subsequent requests should be fast (~30s)

### **Logs Access**
- Go to Render dashboard
- Select your service
- Click "Logs" tab to see real-time logs

## 🎯 **Final Checklist**

Before submission:
- ✅ Service deployed successfully
- ✅ Health endpoint returns 200
- ✅ Webhook endpoint processes requests
- ✅ Both PDF and DOCX documents work
- ✅ Response time under 2 minutes
- ✅ Webhook URL format correct

## 📞 **Support**

If you encounter issues:
1. Check Render logs for errors
2. Test locally first with `python run-fast.py`
3. Verify all environment variables are set
4. Ensure Gemini API key has sufficient quota

Your webhook URL will be:
```
https://YOUR_SERVICE_NAME.onrender.com/api/v1/hackrx/run
```

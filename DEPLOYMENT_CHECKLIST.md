# ✅ Deployment Checklist

## 🚀 **Quick Deployment Steps**

### **1. Push to GitHub** (5 minutes)
```bash
git add .
git commit -m "Deploy optimized system"
git push origin main
```

### **2. Deploy to Render** (10 minutes)
1. Go to [render.com](https://render.com)
2. **New +** → **Web Service**
3. Connect your GitHub repo
4. Use these settings:
   - **Build Command**: `pip install -r requirements-fast.txt`
   - **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

### **3. Set Environment Variables** (2 minutes)
**REQUIRED:**
- `GEMINI_API_KEY` = `your_actual_gemini_api_key`
- `API_BEARER_TOKEN` = `87e1f87355284c19bac1880413d4a1e7cb868891939fc1c6d8227ee2c1b89cb0`

**OPTIONAL:**
- `EMBEDDING_PROVIDER` = `gemini`
- `CHUNK_SIZE` = `1024`

### **4. Test Deployment** (5 minutes)
```bash
python test_webhook.py
```
Enter your Render URL when prompted.

### **5. Submit Webhook** (1 minute)
Your webhook URL format:
```
https://YOUR_SERVICE_NAME.onrender.com/api/v1/hackrx/run
```

## 🎯 **What You Need to Provide**

### **For Render Deployment:**
1. **GitHub Repository URL** - Your code repository
2. **Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

### **For Competition Submission:**
1. **Webhook URL** - `https://your-service.onrender.com/api/v1/hackrx/run`

## 📋 **Pre-Deployment Checklist**

- ✅ Code pushed to GitHub
- ✅ `requirements-fast.txt` exists
- ✅ `render.yaml` configured
- ✅ `main.py` has webhook endpoint `/api/v1/hackrx/run`
- ✅ Gemini API key ready
- ✅ Bearer token set: `87e1f87355284c19bac1880413d4a1e7cb868891939fc1c6d8227ee2c1b89cb0`

## 🧪 **Post-Deployment Testing**

### **Test Commands:**
```bash
# Health check
curl https://your-service.onrender.com/health

# Webhook test
python test_webhook.py
```

### **Expected Results:**
- ✅ Health check returns 200
- ✅ PDF processing works (~30-60s)
- ✅ DOCX processing works (~30-60s)
- ✅ Both endpoints return valid JSON

## 🎉 **Success Criteria**

Your deployment is ready when:
- ✅ Service builds successfully
- ✅ Health endpoint responds
- ✅ Webhook processes both PDF and DOCX
- ✅ Response time under 2 minutes
- ✅ Returns proper JSON format

## 🔗 **Final Submission**

Submit this URL format:
```
https://YOUR_SERVICE_NAME.onrender.com/api/v1/hackrx/run
```

**Example:**
```
https://hackrx-api-abc123.onrender.com/api/v1/hackrx/run
```

## 🆘 **Quick Troubleshooting**

| Issue | Solution |
|-------|----------|
| Build fails | Check `requirements-fast.txt` exists |
| Service won't start | Verify `GEMINI_API_KEY` is set |
| 401 errors | Check `API_BEARER_TOKEN` is correct |
| Slow responses | Normal for free tier (cold starts) |
| 500 errors | Check logs in Render dashboard |

## ⏱️ **Timeline**

- **Setup**: 15-20 minutes
- **First request**: 30-60 seconds (cold start)
- **Subsequent requests**: 30-45 seconds
- **Total deployment time**: ~20 minutes

Your optimized system is ready for deployment! 🚀

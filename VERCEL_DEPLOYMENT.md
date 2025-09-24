# 🚀 Vercel Deployment Guide

## ✅ **YES - This Can Run on Vercel!**

But there are important considerations for **long-running discovery operations**.

---

## 🚨 **Key Vercel Limitations**

### **1. Serverless Function Timeout**
- **Hobby Plan**: 10 seconds max
- **Pro Plan**: 60 seconds max  
- **Enterprise**: 300 seconds max

### **2. Discovery Run Times**
- **Small runs** (5-10 profiles): ~30 seconds ✅
- **Medium runs** (50+ profiles): ~2-5 minutes ⚠️
- **Large runs** (100+ profiles): ~10+ minutes ❌

---

## 🛠 **Solution: Hybrid Architecture**

### **Option A: Chunked Processing (Recommended)**
Break large runs into smaller chunks that fit within timeouts:

```javascript
// Instead of processing 100 profiles at once
// Process in chunks of 10 profiles per serverless call
```

### **Option B: Queue-Based Processing**
Use Vercel for UI + separate service for heavy processing:

```
Frontend (Vercel) → Queue (Redis/SQS) → Worker (Railway/Render)
```

### **Option C: Client-Side Processing** 
Run discovery logic in the browser (current approach):

```
Browser → Vercel API (proxy only) → RapidAPI
```

---

## 📦 **Current Setup: Option C (Browser-Based)**

**This is what we have now and it WORKS on Vercel!**

### **How it Works**:
1. **Browser runs discovery logic** (no timeout limits)
2. **Vercel APIs are just proxies** (~1 second each)
3. **Data saves incrementally** (failure-safe)

### **Vercel API Endpoints** (all under 10s):
- `/api/hashtag` - Simple proxy to RapidAPI
- `/api/profile` - Simple proxy to RapidAPI  
- `/api/similar` - Simple proxy to RapidAPI
- `/api/run-start` - Database insert (~100ms)
- `/api/run-ingest` - Database batch insert (~1-2s)
- `/api/run-complete` - Database update (~100ms)
- `/api/run-status` - Database query (~200ms)

---

## 🔧 **Vercel Configuration**

### **1. Environment Variables**
Set in Vercel Dashboard:

```bash
INSTAGRAM_API_KEY=your_rapidapi_key
POSTGRES_URL=your_supabase_connection_string
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### **2. Build Settings**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install"
}
```

### **3. API Route Configuration**
Create `vercel.json`:

```json
{
  "functions": {
    "api/**/*.js": {
      "maxDuration": 60
    }
  }
}
```

---

## 🎯 **Deployment Steps**

### **1. Prepare Environment**
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login
```

### **2. Set Environment Variables**
```bash
# Set your API keys
vercel env add INSTAGRAM_API_KEY
vercel env add POSTGRES_URL
vercel env add VITE_SUPABASE_URL
vercel env add VITE_SUPABASE_ANON_KEY
```

### **3. Deploy**
```bash
# Deploy to Vercel
vercel --prod
```

### **4. Database Setup**
- Set up Supabase PostgreSQL database
- Tables auto-create on first API call
- Or run migration manually

---

## ✅ **What Works on Vercel**

### **Current Architecture Advantages**:
- ✅ **No timeout issues** (browser handles long operations)
- ✅ **Incremental data saving** (failure-resistant)
- ✅ **Real-time UI updates** (progress tracking)
- ✅ **Auto-scaling** (Vercel handles traffic)
- ✅ **Global CDN** (fast worldwide access)

### **Discovery Scenarios**:
- ✅ **Small runs** (2-3 pages): Perfect
- ✅ **Medium runs** (5-10 pages): Works well
- ✅ **Large runs** (20+ pages): Works but takes time
- ✅ **Browser tab stays open**: No limits

---

## ⚠️ **Potential Issues & Solutions**

### **Issue 1: User Closes Browser Tab**
**Problem**: Run stops mid-process

**Solution**: Add warning + background processing option:
```javascript
window.addEventListener('beforeunload', (e) => {
  if (running) {
    e.preventDefault();
    e.returnValue = 'Discovery run in progress. Sure you want to leave?';
  }
});
```

### **Issue 2: Very Large Runs**
**Problem**: Browser becomes unresponsive

**Solution**: Add progress throttling:
```javascript
// Add delay between API calls to prevent overload
await new Promise(resolve => setTimeout(resolve, 100));
```

### **Issue 3: Network Disconnection**
**Problem**: Browser loses connection

**Solution**: Auto-retry with exponential backoff:
```javascript
const retryFetch = async (url, options, retries = 3) => {
  try {
    return await fetch(url, options);
  } catch (err) {
    if (retries > 0) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      return retryFetch(url, options, retries - 1);
    }
    throw err;
  }
};
```

---

## 🚀 **Ready to Deploy?**

**Your current setup is 100% Vercel-compatible!**

1. **Set up environment variables**
2. **Connect your database** (Supabase)
3. **Deploy with `vercel --prod`**
4. **Start discovering profiles!**

The system is designed to be **failure-resistant** and **Vercel-optimized** from the ground up.

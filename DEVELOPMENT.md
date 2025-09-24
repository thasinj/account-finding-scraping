# 🛠️ Development Setup Guide

## 🚨 **SOLUTION TO THE 404 ERROR**

The error you're seeing:
```
POST http://localhost:5173/api/run-start net::ERR_ABORTED 404 (Not Found)
```

This happens because **Vite dev server doesn't include the API routes**. Here's how to fix it:

---

## 🔧 **Quick Fix - Run Both Servers**

### **Option 1: Run Full Development Environment**
```bash
# This runs both API server (port 3001) and Vite (port 5176) 
npm run dev:full
```

### **Option 2: Run Servers Separately**
```bash
# Terminal 1: Start API server
npm run dev:api

# Terminal 2: Start Vite dev server  
npm run dev
```

---

## 📋 **Environment Setup**

Create a `.env` file in your project root:

```bash
# Instagram API (RapidAPI)
INSTAGRAM_API_KEY=your_rapidapi_key_here

# Database (Supabase PostgreSQL)
POSTGRES_URL=your_postgres_connection_string

# Frontend Supabase Config  
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

---

## 🎯 **What's Happening**

### **Development Architecture**:
```
Frontend (Vite) → http://localhost:5176
    ↓ (proxy /api requests)
API Server → http://localhost:3001
    ↓ (connects to)
Database → Supabase PostgreSQL
```

### **Production Architecture** (Vercel):
```
Frontend → your-app.vercel.app
    ↓ (serverless functions)
API Routes → your-app.vercel.app/api/*
    ↓ (connects to)
Database → Supabase PostgreSQL
```

---

## 🔍 **Development vs Production**

| Environment | Frontend | API Routes | Database |
|-------------|----------|------------|----------|
| **Development** | Vite (5176) | Express (3001) | Supabase |
| **Production** | Vercel | Vercel Functions | Supabase |

---

## 🚀 **Getting Started**

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual keys
   ```

3. **Start development servers**:
   ```bash
   npm run dev:full
   ```

4. **Open browser**:
   ```
   http://localhost:5176
   ```

---

## 🧪 **Testing API Endpoints**

Once servers are running, test API endpoints:

```bash
# Health check
curl http://localhost:3001/health

# Test run start (requires environment variables)
curl -X POST http://localhost:3001/api/run-start \
  -H "Content-Type: application/json" \
  -d '{"type":"combined","input":"edm","params":{}}'
```

---

## 🛠️ **Available Scripts**

- `npm run dev` - Start Vite dev server only
- `npm run dev:api` - Start API server only  
- `npm run dev:full` - Start both servers
- `npm run build` - Build for production
- `npm run preview` - Preview production build

---

## 🚨 **Common Issues**

### **"404 Not Found" on API calls**
- **Cause**: API server not running
- **Fix**: Run `npm run dev:api` or `npm run dev:full`

### **"ECONNREFUSED" errors**
- **Cause**: Database connection issues
- **Fix**: Check your `POSTGRES_URL` in `.env`

### **"Server misconfiguration" errors**  
- **Cause**: Missing environment variables
- **Fix**: Set `INSTAGRAM_API_KEY` in `.env`

### **Port conflicts**
- **Cause**: Ports 3001 or 5176 already in use
- **Fix**: Kill other processes or change ports in configs

---

## 📦 **Deployment Ready**

Once development works locally:

1. **Set environment variables in Vercel**
2. **Deploy**: `vercel --prod`
3. **Done!** - API routes become serverless functions automatically

Your app will work exactly the same in production! 🎉

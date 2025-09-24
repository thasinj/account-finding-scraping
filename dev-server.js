import express from 'express';
import cors from 'cors';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { config } from 'dotenv';

// Load environment variables FIRST
config();

// Debug environment variables
console.log('Environment check:');
console.log('VITE_SUPABASE_URL:', process.env.VITE_SUPABASE_URL ? 'Found' : 'Not found');
console.log('VITE_SUPABASE_KEY:', process.env.VITE_SUPABASE_KEY ? 'Found' : 'Not found');

const __dirname = dirname(fileURLToPath(import.meta.url));

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Helper function to wrap Vercel API handlers for Express
const wrapHandler = (handler) => {
  return async (req, res) => {
    try {
      // Ensure req.query and req.body exist
      if (!req.query) req.query = {};
      if (!req.body) req.body = {};
      
      // Vercel-style response methods
      const originalStatus = res.status.bind(res);
      const originalJson = res.json.bind(res);
      
      res.status = (code) => {
        res.statusCode = code;
        return res;
      };
      
      res.json = (data) => {
        res.setHeader('Content-Type', 'application/json');
        return originalJson(data);
      };

      await handler(req, res);
    } catch (error) {
      console.error('Handler error:', error);
      res.status(500).json({ 
        message: 'Internal server error', 
        error: error.message 
      });
    }
  };
};

// Dynamically import API handlers after environment is loaded
async function setupRoutes() {
  try {
    const runStart = (await import('./api/run-start.js')).default;
    const runIngest = (await import('./api/run-ingest.js')).default;
    const runComplete = (await import('./api/run-complete.js')).default;
    const runFail = (await import('./api/run-fail.js')).default;
    const runStatus = (await import('./api/run-status.js')).default;
    const runsList = (await import('./api/runs-list.js')).default;
    const profilesList = (await import('./api/profiles-list.js')).default;
    const hashtag = (await import('./api/hashtag.js')).default;
    const profile = (await import('./api/profile.js')).default;
    const similar = (await import('./api/similar.js')).default;

    // API Routes
    app.post('/api/run-start', wrapHandler(runStart));
    app.post('/api/run-ingest', wrapHandler(runIngest));
    app.post('/api/run-complete', wrapHandler(runComplete));
    app.post('/api/run-fail', wrapHandler(runFail));
    app.get('/api/run-status', wrapHandler(runStatus));
    app.get('/api/runs-list', wrapHandler(runsList));
    app.get('/api/profiles-list', wrapHandler(profilesList));
    app.get('/api/hashtag', wrapHandler(hashtag));
    app.get('/api/profile', wrapHandler(profile));
    app.get('/api/similar', wrapHandler(similar));

    // Health check
    app.get('/health', (req, res) => {
      res.json({ status: 'ok', message: 'Development API server running' });
    });

    app.listen(PORT, () => {
      console.log(`🚀 Development API server running on http://localhost:${PORT}`);
      console.log(`📡 API endpoints available at http://localhost:${PORT}/api/*`);
    });
  } catch (error) {
    console.error('Failed to setup routes:', error);
    process.exit(1);
  }
}

// Start the server
setupRoutes();

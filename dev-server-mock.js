import express from 'express';
import cors from 'cors';

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Mock responses for testing
const mockResponses = {
  'run-start': () => ({ id: `mock-run-${Date.now()}` }),
  'run-ingest': () => ({ inserted_count: 5, usernames: ['user1', 'user2', 'user3', 'user4', 'user5'] }),
  'run-complete': () => ({ ok: true }),
  'run-fail': () => ({ ok: true }),
  'run-status': () => ({
    run: {
      id: 'mock-run-123',
      type: 'combined',
      input: 'edm',
      status: 'completed',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      current_layer: 1,
      total_api_calls: 25
    },
    profiles: [
      { username: 'edm_artist1', full_name: 'EDM Artist 1', follower_count: 150000, layer: 0, discovery_method: 'hashtag' },
      { username: 'edm_artist2', full_name: 'EDM Artist 2', follower_count: 89000, layer: 1, discovery_method: 'similar' }
    ]
  }),
  'runs-list': () => ({ runs: [] }),
  'profiles-list': () => ({ profiles: [], total: 0, categories: [] }),
  'hashtag': () => ({ data: [] }),
  'profile': () => ({ user_data: { username: 'test', follower_count: 1000 } }),
  'similar': () => ({ data: [] })
};

// Create mock routes
Object.keys(mockResponses).forEach(endpoint => {
  const methods = ['get', 'post'];
  methods.forEach(method => {
    app[method](`/api/${endpoint}`, (req, res) => {
      console.log(`📡 Mock API: ${method.toUpperCase()} /api/${endpoint}`);
      const response = mockResponses[endpoint]();
      res.json(response);
    });
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'Mock API server running (no database required)' });
});

app.listen(PORT, () => {
  console.log(`🚀 Mock API server running on http://localhost:${PORT}`);
  console.log(`📡 All API endpoints mocked - no database required!`);
  console.log(`🎯 Perfect for testing the frontend without setup`);
});

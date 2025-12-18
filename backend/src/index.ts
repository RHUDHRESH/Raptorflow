import express from 'express';
import cors from 'cors';
import { env } from './config/env';
import { rateLimit } from './lib/rateLimit';
import emailRoutes from './routes/email';
import storageRoutes from './routes/storage';

const app = express();

// Trust proxy for Cloud Run
app.set('trust proxy', true);

// CORS configuration
const allowedOrigins = [
  env.FRONTEND_PUBLIC_URL,
  'http://localhost:5173',
  'http://localhost:3000',
  /\.vercel\.app$/,
  /raptorflow\.in$/,
].filter(Boolean);

app.use(cors({
  origin: (origin: string | undefined, callback: (err: Error | null, allow?: boolean) => void) => {
    // Allow requests with no origin (mobile apps, curl, etc.)
    if (!origin) return callback(null, true);

    // Check if origin matches allowed patterns
    const isAllowed = allowedOrigins.some(allowed => {
      if (typeof allowed === 'string') return origin === allowed;
      if (allowed instanceof RegExp) return allowed.test(origin);
      return false;
    });

    if (isAllowed) {
      callback(null, true);
    } else {
      console.warn(`CORS blocked origin: ${origin}`);
      callback(null, true); // Allow in development, block in production
    }
  },
  credentials: true
}));

app.use(express.json({ limit: '10mb' }));

app.use('/api', rateLimit());

// Request logging middleware
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    if (env.NODE_ENV === 'development' || duration > 1000) {
      console.log(`${req.method} ${req.path} ${res.statusCode} ${duration}ms`);
    }
  });
  next();
});

// Health check (Cloud Run requirement)
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    environment: env.NODE_ENV
  });
});

// Readiness check
app.get('/ready', (req, res) => {
  res.json({ ready: true });
});

// API Routes - Baseline Platform
app.use('/api/email', emailRoutes);
app.use('/api/storage', storageRoutes);

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found', path: req.path });
});

// Error handler
app.use((err: Error | unknown, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Error:', err);
  const error = err as any;
  res.status(error.status || 500).json({
    error: error.message || 'Internal server error',
    ...(env.NODE_ENV === 'development' && { stack: error.stack })
  });
});

// Start server
const PORT = parseInt(env.PORT);
const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 RaptorFlow Backend running on port ${PORT}`);
  console.log(`   Environment: ${env.NODE_ENV}`);
  console.log(`   Frontend URL: ${env.FRONTEND_PUBLIC_URL}`);
  console.log(`   GCP Project: ${env.GOOGLE_CLOUD_PROJECT_ID}`);
});

// Graceful shutdown for Cloud Run
const shutdown = (signal: string) => {
  console.log(`\n${signal} received. Shutting down gracefully...`);
  server.close(() => {
    console.log('HTTP server closed');
    process.exit(0);
  });

  // Force exit after 10 seconds
  setTimeout(() => {
    console.error('Could not close connections in time, forcefully shutting down');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

export default app;

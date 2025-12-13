import express from 'express';
import cors from 'cors';
import { env } from './config/env';
import onboardingRoutes from './routes/onboarding';
import paymentRoutes from './routes/payments';
import sharedRoutes from './routes/shared';
import icpRoutes from './routes/icps';
import campaignRoutes from './routes/campaigns';
import moveRoutes from './routes/moves';
import protocolRoutes from './routes/protocols';
import metricRoutes from './routes/metrics';
import spikeRoutes from './routes/spikes';
import assetRoutes from './routes/assets';
import enrichRoutes from './routes/enrich';
import radarRoutes from './routes/radar';
import cohortRoutes from './routes/cohorts';

// Advanced Agentic API Routes (LangChain Highest Level) - temporarily disabled
// import advancedApiRoutes from './v2/advanced_api';

// Unified V3 API Routes (V1 + V2 orchestration)
import v3ApiRoutes from './v3/api';

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
  origin: (origin, callback) => {
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

// API Routes - Core
app.use('/api/onboarding', onboardingRoutes);
app.use('/api/payments', paymentRoutes);
app.use('/api/shared', sharedRoutes);

// API Routes - Platform
app.use('/api/icps', icpRoutes);
app.use('/api/campaigns', campaignRoutes);
app.use('/api/moves', moveRoutes);
app.use('/api/protocols', protocolRoutes);
app.use('/api/metrics', metricRoutes);
app.use('/api/spikes', spikeRoutes);
app.use('/api/assets', assetRoutes);
app.use('/api/enrich', enrichRoutes);
app.use('/api/radar', radarRoutes);
app.use('/api/cohorts', cohortRoutes);

// API Routes - Advanced Agentic (LangChain Highest Level) - temporarily disabled
// app.use('/api/v2', advancedApiRoutes);

// API Routes - Unified V3 Orchestration (V1 + V2)
app.use('/api/v3', v3ApiRoutes);

// API Routes - Muse Orchestrator (New AI Content Generation System)
import museOrchestratorRoutes from './orchestrator/server';
app.use('/api/muse', museOrchestratorRoutes);

// Start Muse Orchestrator Worker (for async job processing)
import { startWorker } from './orchestrator/worker';
startWorker().catch(error => {
  console.error('❌ Failed to start Muse orchestrator worker:', error);
  process.exit(1);
});

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

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

const app = express();

// Middleware
app.use(cors({
  origin: env.FRONTEND_PUBLIC_URL,
  credentials: true
}));
app.use(express.json({ limit: '10mb' }));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
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

// Error handler
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Error:', err);
  res.status(err.status || 500).json({
    error: err.message || 'Internal server error',
    ...(env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// Start server
const PORT = parseInt(env.PORT);
app.listen(PORT, () => {
  console.log(`🚀 RaptorFlow Backend running on port ${PORT}`);
  console.log(`   Environment: ${env.NODE_ENV}`);
  console.log(`   Frontend URL: ${env.FRONTEND_PUBLIC_URL}`);
});

export default app;


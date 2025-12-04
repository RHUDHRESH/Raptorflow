import express from 'express';
import cors from 'cors';
import { env } from './config/env';
import onboardingRoutes from './routes/onboarding';
import paymentRoutes from './routes/payments';
import sharedRoutes from './routes/shared';

const app = express();

// Middleware
app.use(cors({
  origin: env.FRONTEND_PUBLIC_URL,
  credentials: true
}));
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API Routes
app.use('/api/onboarding', onboardingRoutes);
app.use('/api/payments', paymentRoutes);
app.use('/api/shared', sharedRoutes);

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


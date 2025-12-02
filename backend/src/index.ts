import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { env } from './config/env';
import { onboardingRouter } from './routes/onboarding';
import { paymentsRouter } from './routes/payments';

const app = express();

// Middleware
app.use(helmet());
app.use(cors({
  origin: env.FRONTEND_PUBLIC_URL,
  credentials: true,
}));
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', env: env.NODE_ENV });
});

// Routes
app.use('/api/onboarding', onboardingRouter);
app.use('/api/payments', paymentsRouter);

// Error handler
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
const port = parseInt(env.PORT, 10);
app.listen(port, () => {
  console.log(`🚀 Backend running on port ${port}`);
  console.log(`🌍 Environment: ${env.NODE_ENV}`);
});

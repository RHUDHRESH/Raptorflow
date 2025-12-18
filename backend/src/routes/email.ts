import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { env } from '../config/env';
import { requireSupabaseUser } from '../lib/requireSupabaseUser';

const router = Router();

const sendSchema = z.object({
  to: z.union([z.string().email(), z.array(z.string().email()).min(1)]),
  subject: z.string().min(1),
  text: z.string().optional(),
  html: z.string().optional(),
});

router.post('/send', requireSupabaseUser, async (req: Request, res: Response) => {
  if (!env.SENDGRID_API_KEY) {
    return res.status(500).json({ error: 'SendGrid is not configured' });
  }

  const from = env.SENDGRID_FROM_EMAIL;
  if (!from) {
    return res.status(500).json({ error: 'SENDGRID_FROM_EMAIL is not configured' });
  }

  const parsed = sendSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ error: 'Invalid request', details: parsed.error });
  }

  const { to, subject, text, html } = parsed.data;

  if (!text && !html) {
    return res.status(400).json({ error: 'Either text or html is required' });
  }

  const payload = {
    personalizations: [
      {
        to: (Array.isArray(to) ? to : [to]).map((email) => ({ email })),
      },
    ],
    from: { email: from },
    subject,
    content: [
      ...(text ? [{ type: 'text/plain', value: text }] : []),
      ...(html ? [{ type: 'text/html', value: html }] : []),
    ],
  };

  const response = await fetch('https://api.sendgrid.com/v3/mail/send', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.SENDGRID_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => '');
    return res.status(502).json({ error: 'Failed to send email', details: errorText });
  }

  return res.json({ ok: true });
});

export default router;

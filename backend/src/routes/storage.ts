import { Router, Request, Response } from 'express';
import crypto from 'crypto';
import { z } from 'zod';
import { Storage } from '@google-cloud/storage';
import { env } from '../config/env';
import { requireSupabaseUser } from '../lib/requireSupabaseUser';

const router = Router();

const storage = new Storage();

const signedUploadSchema = z.object({
  filename: z.string().min(1),
  contentType: z.string().min(1),
});

function sanitizeFilename(filename: string) {
  return filename.replace(/[^a-zA-Z0-9._-]/g, '_');
}

router.post('/signed-upload', requireSupabaseUser, async (req: Request, res: Response) => {
  const bucketName = env.GCS_BUCKET;
  if (!bucketName) {
    return res.status(500).json({ error: 'GCS_BUCKET is not configured' });
  }

  const parsed = signedUploadSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ error: 'Invalid request', details: parsed.error });
  }

  const { filename, contentType } = parsed.data;
  const userId = (req as any).user?.id || 'anonymous';
  const key = `uploads/${userId}/${crypto.randomUUID()}_${sanitizeFilename(filename)}`;

  const expiresSeconds = Number(env.GCS_SIGNED_URL_EXPIRES_SECONDS || '900');
  const expires = Date.now() + expiresSeconds * 1000;

  const bucket = storage.bucket(bucketName);
  const file = bucket.file(key);

  const [url] = await file.getSignedUrl({
    version: 'v4',
    action: 'write',
    expires,
    contentType,
  });

  return res.json({
    url,
    method: 'PUT',
    headers: {
      'Content-Type': contentType,
    },
    key,
    bucket: bucketName,
    expiresAt: new Date(expires).toISOString(),
  });
});

export default router;

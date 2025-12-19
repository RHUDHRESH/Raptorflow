/**
 * GCS (Google Cloud Storage) Connector Service
 *
 * Handles file uploads, downloads, and signed URLs for asset management.
 * Replaces S3 connector for GCP-native storage.
 */

import { Storage, Bucket, File } from '@google-cloud/storage';
import { env } from '../config/env';
import { redisMemory } from './redisMemory';

export interface UploadOptions {
  contentType?: string;
  metadata?: Record<string, string>;
  cacheControl?: string;
  public?: boolean;
}

export interface UploadResult {
  key: string;
  bucket: string;
  location: string;
  size: number;
}

export interface SignedUrlOptions {
  expiresIn?: number; // seconds
  contentType?: string;
  action?: 'read' | 'write';
}

export interface FileInfo {
  key: string;
  size: number;
  lastModified: Date;
  contentType?: string;
  metadata?: Record<string, string>;
}

class GCSConnectorService {
  private storage: Storage;
  private bucket: Bucket | null = null;
  private bucketName: string;
  private readonly maxFileSize = 100 * 1024 * 1024; // 100MB
  private readonly defaultExpiresIn = 3600; // 1 hour

  constructor() {
    this.storage = new Storage();
    this.bucketName = env.GCS_BUCKET || '';
  }

  private getBucket(): Bucket {
    if (!this.bucketName) {
      throw new Error('GCS_BUCKET environment variable is not configured');
    }
    if (!this.bucket) {
      this.bucket = this.storage.bucket(this.bucketName);
    }
    return this.bucket;
  }

  /**
   * Upload a file from buffer
   */
  async uploadFile(
    key: string,
    buffer: Buffer,
    options: UploadOptions = {}
  ): Promise<UploadResult> {
    const bucket = this.getBucket();
    const file = bucket.file(key);

    try {
      await file.save(buffer, {
        contentType: options.contentType,
        metadata: {
          metadata: options.metadata,
          cacheControl: options.cacheControl,
        },
        public: options.public,
      });

      const result: UploadResult = {
        key,
        bucket: this.bucketName,
        location: `https://storage.googleapis.com/${this.bucketName}/${key}`,
        size: buffer.length,
      };

      console.log(`📤 Uploaded file to GCS: ${key} (${buffer.length} bytes)`);

      // Cache file info
      await this.cacheFileInfo(key, {
        key,
        size: buffer.length,
        lastModified: new Date(),
        contentType: options.contentType,
        metadata: options.metadata,
      });

      return result;

    } catch (error: any) {
      console.error('GCS upload error:', error);
      throw new Error(`Failed to upload file to GCS: ${error.message}`);
    }
  }

  /**
   * Upload a large file using resumable upload
   */
  async uploadLargeFile(
    key: string,
    stream: NodeJS.ReadableStream,
    contentType?: string,
    fileSize?: number
  ): Promise<UploadResult> {
    const bucket = this.getBucket();
    const file = bucket.file(key);

    try {
      await new Promise<void>((resolve, reject) => {
        stream
          .pipe(file.createWriteStream({
            contentType,
            resumable: true,
          }))
          .on('finish', resolve)
          .on('error', reject);
      });

      const result: UploadResult = {
        key,
        bucket: this.bucketName,
        location: `https://storage.googleapis.com/${this.bucketName}/${key}`,
        size: fileSize || 0,
      };

      console.log(`📤 Large file uploaded to GCS: ${key}`);

      return result;

    } catch (error: any) {
      console.error('GCS large file upload error:', error);
      throw new Error(`Failed to upload large file to GCS: ${error.message}`);
    }
  }

  /**
   * Download a file
   */
  async downloadFile(key: string): Promise<{ buffer: Buffer; contentType?: string; metadata?: Record<string, string> }> {
    const bucket = this.getBucket();
    const file = bucket.file(key);

    try {
      const [buffer] = await file.download();
      const [metadata] = await file.getMetadata();

      console.log(`📥 Downloaded file from GCS: ${key} (${buffer.length} bytes)`);

      return {
        buffer,
        contentType: metadata.contentType,
        metadata: metadata.metadata as Record<string, string>,
      };

    } catch (error: any) {
      console.error('GCS download error:', error);
      throw new Error(`Failed to download file from GCS: ${error.message}`);
    }
  }

  /**
   * Generate a signed URL for upload
   */
  async generateUploadUrl(
    key: string,
    options: SignedUrlOptions = {}
  ): Promise<string> {
    const bucket = this.getBucket();
    const file = bucket.file(key);

    try {
      const [url] = await file.getSignedUrl({
        version: 'v4',
        action: 'write',
        expires: Date.now() + (options.expiresIn || this.defaultExpiresIn) * 1000,
        contentType: options.contentType,
      });

      console.log(`🔗 Generated upload URL for: ${key}`);
      return url;

    } catch (error: any) {
      console.error('GCS signed URL generation error:', error);
      throw new Error(`Failed to generate upload URL: ${error.message}`);
    }
  }

  /**
   * Generate a signed URL for download
   */
  async generateDownloadUrl(
    key: string,
    options: SignedUrlOptions = {}
  ): Promise<string> {
    const bucket = this.getBucket();
    const file = bucket.file(key);

    try {
      const [url] = await file.getSignedUrl({
        version: 'v4',
        action: 'read',
        expires: Date.now() + (options.expiresIn || this.defaultExpiresIn) * 1000,
      });

      console.log(`🔗 Generated download URL for: ${key}`);
      return url;

    } catch (error: any) {
      console.error('GCS signed URL generation error:', error);
      throw new Error(`Failed to generate download URL: ${error.message}`);
    }
  }

  /**
   * Get signed URL (alias for generateDownloadUrl for S3 compatibility)
   */
  async getSignedUrl(key: string, expiresIn?: number): Promise<string> {
    return this.generateDownloadUrl(key, { expiresIn });
  }

  /**
   * Delete a file
   */
  async deleteFile(key: string): Promise<void> {
    const bucket = this.getBucket();
    const file = bucket.file(key);

    try {
      await file.delete();

      // Remove from cache
      await redisMemory.delete(`gcs:file:${key}`);

      console.log(`🗑️ Deleted file from GCS: ${key}`);

    } catch (error: any) {
      console.error('GCS delete error:', error);
      throw new Error(`Failed to delete file from GCS: ${error.message}`);
    }
  }

  /**
   * Check if file exists
   */
  async fileExists(key: string): Promise<boolean> {
    const bucket = this.getBucket();
    const file = bucket.file(key);

    try {
      const [exists] = await file.exists();
      return exists;
    } catch (error: any) {
      return false;
    }
  }

  /**
   * Get file information
   */
  async getFileInfo(key: string): Promise<FileInfo | null> {
    // Try cache first
    const cached = await redisMemory.retrieve<FileInfo>(`gcs:file:${key}`);
    if (cached) return cached;

    const bucket = this.getBucket();
    const file = bucket.file(key);

    try {
      const [metadata] = await file.getMetadata();

      const fileInfo: FileInfo = {
        key,
        size: parseInt(metadata.size as string) || 0,
        lastModified: new Date(metadata.updated || metadata.timeCreated || new Date()),
        contentType: metadata.contentType,
        metadata: metadata.metadata as Record<string, string>,
      };

      // Cache file info
      await this.cacheFileInfo(key, fileInfo);

      return fileInfo;

    } catch (error: any) {
      if (error.code === 404) {
        return null;
      }
      console.error('GCS file info error:', error);
      throw new Error(`Failed to get file info: ${error.message}`);
    }
  }

  /**
   * List files in a folder
   */
  async listFiles(prefix?: string, maxResults: number = 1000): Promise<FileInfo[]> {
    const bucket = this.getBucket();

    try {
      const [files] = await bucket.getFiles({
        prefix,
        maxResults,
      });

      const fileInfos: FileInfo[] = files.map(file => ({
        key: file.name,
        size: parseInt(file.metadata.size as string) || 0,
        lastModified: new Date(file.metadata.updated || file.metadata.timeCreated || new Date()),
        contentType: file.metadata.contentType,
      }));

      return fileInfos;

    } catch (error: any) {
      console.error('GCS list files error:', error);
      throw new Error(`Failed to list files: ${error.message}`);
    }
  }

  /**
   * Generate a unique key for file upload
   */
  generateKey(prefix: string, filename: string, userId?: string): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 9);
    const userPrefix = userId ? `${userId}/` : '';
    const sanitizedFilename = filename.replace(/[^a-zA-Z0-9.-]/g, '_');

    return `${prefix}/${userPrefix}${timestamp}_${random}_${sanitizedFilename}`;
  }

  /**
   * Get bucket statistics
   */
  async getBucketStats(): Promise<{
    totalFiles: number;
    totalSize: number;
    lastActivity: Date | null;
  }> {
    try {
      const files = await this.listFiles('', 100);
      const totalSize = files.reduce((sum, file) => sum + file.size, 0);
      const lastActivity = files.length > 0
        ? files.reduce((latest, file) =>
            file.lastModified > latest ? file.lastModified : latest,
            files[0].lastModified)
        : null;

      return {
        totalFiles: files.length,
        totalSize,
        lastActivity,
      };
    } catch (error) {
      console.error('GCS bucket stats error:', error);
      return { totalFiles: 0, totalSize: 0, lastActivity: null };
    }
  }

  // =====================================================
  // PRIVATE METHODS
  // =====================================================

  private async cacheFileInfo(key: string, fileInfo: FileInfo): Promise<void> {
    await redisMemory.store(`gcs:file:${key}`, fileInfo, 3600); // Cache for 1 hour
  }
}

// Export singleton instance
export const gcsConnector = new GCSConnectorService();

// Export types
export type { UploadOptions, UploadResult, SignedUrlOptions, FileInfo };

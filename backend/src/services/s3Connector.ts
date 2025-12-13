/**
 * S3 Connector Service
 *
 * Handles file uploads, downloads, and pre-signed URLs for asset management.
 */

import {
  S3Client,
  PutObjectCommand,
  GetObjectCommand,
  DeleteObjectCommand,
  HeadObjectCommand,
  ListObjectsV2Command,
  CreateMultipartUploadCommand,
  UploadPartCommand,
  CompleteMultipartUploadCommand,
  GetObjectCommandOutput,
} from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import { env } from '../config/env';
import { redisMemory } from './redisMemory';

export interface UploadOptions {
  contentType?: string;
  metadata?: Record<string, string>;
  cacheControl?: string;
  acl?: string;
}

export interface UploadResult {
  key: string;
  bucket: string;
  location: string;
  etag: string;
  size: number;
}

export interface PreSignedUrlOptions {
  expiresIn?: number; // seconds
  contentType?: string;
}

export interface FileInfo {
  key: string;
  size: number;
  lastModified: Date;
  etag: string;
  contentType?: string;
  metadata?: Record<string, string>;
}

class S3ConnectorService {
  private s3Client: S3Client;
  private bucketName: string;
  private readonly maxFileSize = 100 * 1024 * 1024; // 100MB
  private readonly defaultExpiresIn = 3600; // 1 hour

  constructor() {
    this.s3Client = new S3Client({
      region: env.AWS_REGION,
    });
    this.bucketName = env.S3_ASSETS_BUCKET || '';
  }

  /**
   * Upload a file from buffer
   */
  async uploadFile(
    key: string,
    buffer: Buffer,
    options: UploadOptions = {}
  ): Promise<UploadResult> {
    const command = new PutObjectCommand({
      Bucket: this.bucketName,
      Key: key,
      Body: buffer,
      ContentType: options.contentType,
      Metadata: options.metadata,
      CacheControl: options.cacheControl,
      ACL: options.acl as any,
    });

    try {
      const response = await this.s3Client.send(command);

      const result: UploadResult = {
        key,
        bucket: this.bucketName,
        location: `https://${this.bucketName}.s3.${env.AWS_REGION}.amazonaws.com/${key}`,
        etag: response.ETag || '',
        size: buffer.length,
      };

      console.log(`📤 Uploaded file to S3: ${key} (${buffer.length} bytes)`);

      // Cache file info
      await this.cacheFileInfo(key, {
        key,
        size: buffer.length,
        lastModified: new Date(),
        etag: response.ETag || '',
        contentType: options.contentType,
        metadata: options.metadata,
      });

      return result;

    } catch (error) {
      console.error('S3 upload error:', error);
      throw new Error(`Failed to upload file to S3: ${error.message}`);
    }
  }

  /**
   * Upload a large file using multipart upload
   */
  async uploadLargeFile(
    key: string,
    stream: NodeJS.ReadableStream,
    contentType?: string,
    fileSize?: number
  ): Promise<UploadResult> {
    const multipartUpload = await this.s3Client.send(
      new CreateMultipartUploadCommand({
        Bucket: this.bucketName,
        Key: key,
        ContentType: contentType,
      })
    );

    if (!multipartUpload.UploadId) {
      throw new Error('Failed to initiate multipart upload');
    }

    const uploadId = multipartUpload.UploadId;
    const parts: { ETag: string; PartNumber: number }[] = [];
    let partNumber = 1;
    const chunkSize = 5 * 1024 * 1024; // 5MB chunks

    try {
      for await (const chunk of this.streamToChunks(stream, chunkSize)) {
        const uploadPartCommand = new UploadPartCommand({
          Bucket: this.bucketName,
          Key: key,
          UploadId: uploadId,
          PartNumber: partNumber,
          Body: chunk,
        });

        const response = await this.s3Client.send(uploadPartCommand);
        parts.push({
          ETag: response.ETag || '',
          PartNumber: partNumber,
        });

        partNumber++;
      }

      // Complete multipart upload
      const completeCommand = new CompleteMultipartUploadCommand({
        Bucket: this.bucketName,
        Key: key,
        UploadId: uploadId,
        MultipartUpload: { Parts: parts },
      });

      const response = await this.s3Client.send(completeCommand);

      const result: UploadResult = {
        key,
        bucket: this.bucketName,
        location: `https://${this.bucketName}.s3.${env.AWS_REGION}.amazonaws.com/${key}`,
        etag: response.ETag || '',
        size: fileSize || 0,
      };

      console.log(`📤 Large file uploaded to S3: ${key} (${parts.length} parts)`);

      return result;

    } catch (error) {
      // TODO: Abort multipart upload on error
      console.error('S3 multipart upload error:', error);
      throw new Error(`Failed to upload large file to S3: ${error.message}`);
    }
  }

  /**
   * Download a file
   */
  async downloadFile(key: string): Promise<{ buffer: Buffer; contentType?: string; metadata?: Record<string, string> }> {
    const command = new GetObjectCommand({
      Bucket: this.bucketName,
      Key: key,
    });

    try {
      const response = await this.s3Client.send(command);

      if (!response.Body) {
        throw new Error('No file content received');
      }

      const buffer = Buffer.from(await response.Body.transformToByteArray());

      console.log(`📥 Downloaded file from S3: ${key} (${buffer.length} bytes)`);

      return {
        buffer,
        contentType: response.ContentType,
        metadata: response.Metadata,
      };

    } catch (error) {
      console.error('S3 download error:', error);
      throw new Error(`Failed to download file from S3: ${error.message}`);
    }
  }

  /**
   * Generate a pre-signed URL for upload
   */
  async generateUploadUrl(
    key: string,
    options: PreSignedUrlOptions = {}
  ): Promise<string> {
    const command = new PutObjectCommand({
      Bucket: this.bucketName,
      Key: key,
      ContentType: options.contentType,
    });

    try {
      const signedUrl = await getSignedUrl(
        this.s3Client,
        command,
        { expiresIn: options.expiresIn || this.defaultExpiresIn }
      );

      console.log(`🔗 Generated upload URL for: ${key}`);
      return signedUrl;

    } catch (error) {
      console.error('S3 pre-signed URL generation error:', error);
      throw new Error(`Failed to generate upload URL: ${error.message}`);
    }
  }

  /**
   * Generate a pre-signed URL for download
   */
  async generateDownloadUrl(
    key: string,
    options: PreSignedUrlOptions = {}
  ): Promise<string> {
    const command = new GetObjectCommand({
      Bucket: this.bucketName,
      Key: key,
    });

    try {
      const signedUrl = await getSignedUrl(
        this.s3Client,
        command,
        { expiresIn: options.expiresIn || this.defaultExpiresIn }
      );

      console.log(`🔗 Generated download URL for: ${key}`);
      return signedUrl;

    } catch (error) {
      console.error('S3 pre-signed URL generation error:', error);
      throw new Error(`Failed to generate download URL: ${error.message}`);
    }
  }

  /**
   * Delete a file
   */
  async deleteFile(key: string): Promise<void> {
    const command = new DeleteObjectCommand({
      Bucket: this.bucketName,
      Key: key,
    });

    try {
      await this.s3Client.send(command);

      // Remove from cache
      await redisMemory.delete(`s3:file:${key}`);

      console.log(`🗑️ Deleted file from S3: ${key}`);

    } catch (error) {
      console.error('S3 delete error:', error);
      throw new Error(`Failed to delete file from S3: ${error.message}`);
    }
  }

  /**
   * Check if file exists
   */
  async fileExists(key: string): Promise<boolean> {
    const command = new HeadObjectCommand({
      Bucket: this.bucketName,
      Key: key,
    });

    try {
      await this.s3Client.send(command);
      return true;
    } catch (error: any) {
      if (error.name === 'NotFound') {
        return false;
      }
      throw error;
    }
  }

  /**
   * Get file information
   */
  async getFileInfo(key: string): Promise<FileInfo | null> {
    // Try cache first
    const cached = await redisMemory.retrieve<FileInfo>(`s3:file:${key}`);
    if (cached) return cached;

    const command = new HeadObjectCommand({
      Bucket: this.bucketName,
      Key: key,
    });

    try {
      const response = await this.s3Client.send(command);

      const fileInfo: FileInfo = {
        key,
        size: response.ContentLength || 0,
        lastModified: response.LastModified || new Date(),
        etag: response.ETag || '',
        contentType: response.ContentType,
        metadata: response.Metadata,
      };

      // Cache file info
      await this.cacheFileInfo(key, fileInfo);

      return fileInfo;

    } catch (error: any) {
      if (error.name === 'NotFound') {
        return null;
      }
      console.error('S3 file info error:', error);
      throw new Error(`Failed to get file info: ${error.message}`);
    }
  }

  /**
   * List files in a folder
   */
  async listFiles(prefix?: string, maxKeys: number = 1000): Promise<FileInfo[]> {
    const command = new ListObjectsV2Command({
      Bucket: this.bucketName,
      Prefix: prefix,
      MaxKeys: maxKeys,
    });

    try {
      const response = await this.s3Client.send(command);

      const files: FileInfo[] = (response.Contents || []).map(obj => ({
        key: obj.Key || '',
        size: obj.Size || 0,
        lastModified: obj.LastModified || new Date(),
        etag: obj.ETag || '',
      }));

      return files;

    } catch (error) {
      console.error('S3 list files error:', error);
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
    // This is a simplified implementation
    // In production, you might want to use S3 inventory or CloudWatch metrics
    try {
      const files = await this.listFiles('', 100); // Sample first 100 files
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
      console.error('S3 bucket stats error:', error);
      return { totalFiles: 0, totalSize: 0, lastActivity: null };
    }
  }

  // =====================================================
  // PRIVATE METHODS
  // =====================================================

  private async *streamToChunks(
    stream: NodeJS.ReadableStream,
    chunkSize: number
  ): AsyncGenerator<Buffer> {
    let buffer = Buffer.alloc(0);

    for await (const chunk of stream) {
      buffer = Buffer.concat([buffer, chunk]);

      while (buffer.length >= chunkSize) {
        yield buffer.subarray(0, chunkSize);
        buffer = buffer.subarray(chunkSize);
      }
    }

    if (buffer.length > 0) {
      yield buffer;
    }
  }

  private async cacheFileInfo(key: string, fileInfo: FileInfo): Promise<void> {
    await redisMemory.store(`s3:file:${key}`, fileInfo, 3600); // Cache for 1 hour
  }
}

// Export singleton instance
export const s3Connector = new S3ConnectorService();

// Export types
export type { UploadOptions, UploadResult, PreSignedUrlOptions, FileInfo };


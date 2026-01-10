import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export interface StorageUpload {
  file: File;
  userId: string;
  fileType: 'avatar' | 'document' | 'workspace';
  onProgress?: (progress: number) => void;
}

export interface StorageResult {
  url: string;
  path: string;
  size: number;
  type: string;
}

export class GCPStorageService {
  private static instance: GCPStorageService;

  static getInstance(): GCPStorageService {
    if (!GCPStorageService.instance) {
      GCPStorageService.instance = new GCPStorageService();
    }
    return GCPStorageService.instance;
  }

  async uploadFile(upload: StorageUpload): Promise<StorageResult> {
    try {
      // Get signed upload URL from backend
      const response = await fetch('/api/storage/upload-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: upload.userId,
          file_name: upload.file.name,
          file_type: upload.fileType,
          file_size: upload.file.size
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get upload URL');
      }

      const { upload_url, file_path } = await response.json();

      // Upload file to GCS
      const xhr = new XMLHttpRequest();

      return new Promise((resolve, reject) => {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable && upload.onProgress) {
            const progress = (event.loaded / event.total) * 100;
            upload.onProgress(progress);
          }
        });

        xhr.addEventListener('load', () => {
          if (xhr.status === 200) {
            // Update user's storage usage
            this.updateStorageUsage(upload.userId, upload.file.size);

            resolve({
              url: upload_url.split('?')[0], // Remove query params
              path: file_path,
              size: upload.file.size,
              type: upload.file.type
            });
          } else {
            reject(new Error('Upload failed'));
          }
        });

        xhr.addEventListener('error', () => {
          reject(new Error('Upload error'));
        });

        xhr.open('PUT', upload_url);
        xhr.setRequestHeader('Content-Type', upload.file.type);
        xhr.send(upload.file);
      });
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  }

  async getDownloadUrl(filePath: string, userId: string): Promise<string> {
    try {
      const response = await fetch('/api/storage/download-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, file_path: filePath })
      });

      if (!response.ok) {
        throw new Error('Failed to get download URL');
      }

      const { download_url } = await response.json();
      return download_url;
    } catch (error) {
      console.error('Download URL error:', error);
      throw error;
    }
  }

  private async updateStorageUsage(userId: string, fileSize: number): Promise<void> {
    try {
      const { data: profile } = await supabase
        .from('user_profiles')
        .select('storage_used_mb')
        .eq('id', userId)
        .single();

      if (profile) {
        const newUsage = profile.storage_used_mb + Math.ceil(fileSize / (1024 * 1024));

        await supabase
          .from('user_profiles')
          .update({ storage_used_mb: newUsage })
          .eq('id', userId);
      }
    } catch (error) {
      console.error('Failed to update storage usage:', error);
    }
  }

  async getUserStorageInfo(userId: string): Promise<{
    quota_mb: number;
    used_mb: number;
    available_mb: number;
  }> {
    try {
      const { data: profile } = await supabase
        .from('user_profiles')
        .select('storage_quota_mb, storage_used_mb')
        .eq('id', userId)
        .single();

      if (profile) {
        return {
          quota_mb: profile.storage_quota_mb,
          used_mb: profile.storage_used_mb,
          available_mb: profile.storage_quota_mb - profile.storage_used_mb
        };
      }

      return { quota_mb: 100, used_mb: 0, available_mb: 100 }; // Default free tier
    } catch (error) {
      console.error('Failed to get storage info:', error);
      return { quota_mb: 100, used_mb: 0, available_mb: 100 };
    }
  }

  async deleteFile(filePath: string, userId: string): Promise<void> {
    try {
      // Get file info to update storage usage
      const response = await fetch('/api/storage/file-info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, file_path: filePath })
      });

      if (response.ok) {
        const { size } = await response.json();
        // Update storage usage (subtract file size)
        const { data: profile } = await supabase
          .from('user_profiles')
          .select('storage_used_mb')
          .eq('id', userId)
          .single();

        if (profile) {
          const newUsage = Math.max(0, profile.storage_used_mb - Math.ceil(size / (1024 * 1024)));

          await supabase
            .from('user_profiles')
            .update({ storage_used_mb: newUsage })
            .eq('id', userId);
        }
      }
    } catch (error) {
      console.error('Failed to delete file:', error);
      throw error;
    }
  }
}

export const gcpStorage = GCPStorageService.getInstance();

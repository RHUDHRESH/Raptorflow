/**
 * ≡ƒÜÇ UNIFIED STORAGE INTEGRATION LAYER
 *
 * This is the SINGLE source of truth for all file operations in Raptorflow.
 *
 * USAGE:
 * import { unifiedStorage } from '@/lib/unified-storage';
 *
 * // Upload any file
 * const result = await unifiedStorage.uploadFile(file, options);
 *
 * // Get download URL
 * const url = await unifiedStorage.getDownloadUrl(fileId);
 *
 * // Delete file
 * await unifiedStorage.deleteFile(fileId);
 */

import { gcpStorage, StorageUpload, StorageResult } from './gcp-storage';

// ============================================================================
// CONFIGURATION - EASY TO SWITCH STORAGE PROVIDERS
// ============================================================================

type StorageProvider = 'gcs' | 'supabase' | 'local' | 'backend';

interface StorageConfig {
  provider: StorageProvider;
  fallbackProvider?: StorageProvider;
  enableCdn: boolean;
  maxFileSize: number; // bytes
  allowedTypes: string[];
}

// ≡ƒöº EASY CONFIGURATION - Change this to switch providers
const STORAGE_CONFIG: StorageConfig = {
  provider: 'gcs', // ΓåÉ CHANGE THIS: 'gcs' | 'supabase' | 'local' | 'backend'
  fallbackProvider: 'local',
  enableCdn: true,
  maxFileSize: 100 * 1024 * 1024, // 100MB
  allowedTypes: [
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'application/pdf', 'text/plain', 'application/json', 'text/csv',
    'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'video/mp4', 'video/quicktime'
  ]
};

// ============================================================================
// UNIFIED STORAGE INTERFACE
// ============================================================================

export interface UnifiedStorageOptions {
  userId?: string;
  workspaceId?: string;
  category?: 'avatar' | 'document' | 'workspace' | 'evidence' | 'temp';
  onProgress?: (progress: number) => void;
  metadata?: Record<string, any>;
}

export interface UnifiedStorageResult {
  success: boolean;
  fileId: string;
  fileName: string;
  url: string;
  path: string;
  size: number;
  type: string;
  provider: StorageProvider;
  error?: string;
}

// ============================================================================
// MAIN UNIFIED STORAGE CLASS
// ============================================================================

class UnifiedStorage {
  private config: StorageConfig;

  constructor() {
    this.config = STORAGE_CONFIG;
  }

  /**
   * ≡ƒÜÇ UPLOAD FILE - Main entry point for all uploads
   *
   * @param file - File to upload
   * @param options - Upload options
   * @returns Promise<UnifiedStorageResult>
   */
  async uploadFile(file: File, options: UnifiedStorageOptions = {}): Promise<UnifiedStorageResult> {
    const startTime = Date.now();
    console.log(`≡ƒÜÇ [UnifiedStorage] Starting upload: ${file.name} (${this.config.provider})`);

    try {
      // Validate file
      const validation = this.validateFile(file);
      if (!validation.valid) {
        return this.createErrorResult(file.name, validation.error!);
      }

      // Route to appropriate provider
      const result = await this.uploadToProvider(file, options);

      const duration = Date.now() - startTime;
      console.log(`Γ£à [UnifiedStorage] Upload complete in ${duration}ms: ${result.fileId}`);

      return result;
    } catch (error) {
      console.error(`Γ¥î [UnifiedStorage] Upload failed: ${file.name}`, error);
      return this.createErrorResult(file.name, error instanceof Error ? error.message : 'Unknown error');
    }
  }

  /**
   * ≡ƒôÑ GET DOWNLOAD URL
   */
  async getDownloadUrl(fileId: string, userId?: string): Promise<string | null> {
    try {
      switch (this.config.provider) {
        case 'gcs':
          return await this.getGCSDownloadUrl(fileId, userId);
        case 'supabase':
          return await this.getSupabaseDownloadUrl(fileId, userId);
        case 'backend':
          return await this.getBackendDownloadUrl(fileId, userId);
        default:
          return null;
      }
    } catch (error) {
      console.error(`Γ¥î [UnifiedStorage] Failed to get download URL: ${fileId}`, error);
      return null;
    }
  }

  /**
   * ≡ƒùæ∩╕Å DELETE FILE
   */
  async deleteFile(fileId: string, userId?: string): Promise<boolean> {
    try {
      switch (this.config.provider) {
        case 'gcs':
          return await this.deleteGCSFile(fileId, userId);
        case 'supabase':
          return await this.deleteSupabaseFile(fileId, userId);
        case 'backend':
          return await this.deleteBackendFile(fileId, userId);
        default:
          return false;
      }
    } catch (error) {
      console.error(`Γ¥î [UnifiedStorage] Failed to delete file: ${fileId}`, error);
      return false;
    }
  }

  /**
   * ≡ƒôè GET STORAGE INFO
   */
  async getStorageInfo(userId: string): Promise<{
    quotaMb: number;
    usedMb: number;
    availableMb: number;
  }> {
    try {
      switch (this.config.provider) {
        case 'gcs':
          const gcsInfo = await gcpStorage.getUserStorageInfo(userId);
          return {
            quotaMb: gcsInfo.quota_mb,
            usedMb: gcsInfo.used_mb,
            availableMb: gcsInfo.available_mb
          };
        default:
          return { quotaMb: 100, usedMb: 0, availableMb: 100 };
      }
    } catch (error) {
      console.error(`Γ¥î [UnifiedStorage] Failed to get storage info: ${userId}`, error);
      return { quotaMb: 100, usedMb: 0, availableMb: 100 };
    }
  }

  // ============================================================================
  // PROVIDER IMPLEMENTATIONS
  // ============================================================================

  private async uploadToProvider(file: File, options: UnifiedStorageOptions): Promise<UnifiedStorageResult> {
    switch (this.config.provider) {
      case 'gcs':
        return await this.uploadToGCS(file, options);
      case 'supabase':
        return await this.uploadToSupabase(file, options);
      case 'backend':
        return await this.uploadToBackend(file, options);
      case 'local':
        return await this.uploadToLocal(file, options);
      default:
        throw new Error(`Unknown storage provider: ${this.config.provider}`);
    }
  }

  private async uploadToGCS(file: File, options: UnifiedStorageOptions): Promise<UnifiedStorageResult> {
    const upload: StorageUpload = {
      file,
      userId: options.userId || 'anonymous',
      fileType: (options.category as 'avatar' | 'document' | 'workspace') || 'document',
      onProgress: options.onProgress
    };

    const result: StorageResult = await gcpStorage.uploadFile(upload);

    return {
      success: true,
      fileId: result.path,
      fileName: file.name,
      url: result.url,
      path: result.path,
      size: result.size,
      type: result.type,
      provider: 'gcs'
    };
  }

  private async uploadToSupabase(file: File, options: UnifiedStorageOptions): Promise<UnifiedStorageResult> {
    // TODO: Implement Supabase storage
    throw new Error('Supabase storage not yet implemented');
  }

  private async uploadToBackend(file: File, options: UnifiedStorageOptions): Promise<UnifiedStorageResult> {
    // TODO: Implement backend upload (for existing evidence vault)
    throw new Error('Backend storage not yet implemented');
  }

  private async uploadToLocal(file: File, options: UnifiedStorageOptions): Promise<UnifiedStorageResult> {
    // Fallback local storage
    const fileId = `local-${Date.now()}-${file.name}`;
    const url = URL.createObjectURL(file);

    return {
      success: true,
      fileId,
      fileName: file.name,
      url,
      path: fileId,
      size: file.size,
      type: file.type,
      provider: 'local'
    };
  }

  // ============================================================================
  // HELPER METHODS
  // ============================================================================

  private validateFile(file: File): { valid: boolean; error?: string } {
    // Size check
    if (file.size > this.config.maxFileSize) {
      return {
        valid: false,
        error: `File size ${(file.size / (1024 * 1024)).toFixed(1)}MB exceeds maximum ${(this.config.maxFileSize / (1024 * 1024)).toFixed(1)}MB`
      };
    }

    // Type check
    if (!this.config.allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: `File type ${file.type} is not allowed`
      };
    }

    return { valid: true };
  }

  private createErrorResult(fileName: string, error: string): UnifiedStorageResult {
    return {
      success: false,
      fileId: '',
      fileName,
      url: '',
      path: '',
      size: 0,
      type: '',
      provider: this.config.provider,
      error
    };
  }

  // ============================================================================
  // PROVIDER-SPECIFIC METHODS (GCS IMPLEMENTED)
  // ============================================================================

  private async getGCSDownloadUrl(fileId: string, userId?: string): Promise<string | null> {
    try {
      return await gcpStorage.getDownloadUrl(fileId, userId || 'anonymous');
    } catch (error) {
      console.error('GCS download URL error:', error);
      return null;
    }
  }

  private async deleteGCSFile(fileId: string, userId?: string): Promise<boolean> {
    try {
      await gcpStorage.deleteFile(fileId, userId || 'anonymous');
      return true;
    } catch (error) {
      console.error('GCS delete error:', error);
      return false;
    }
  }

  // Placeholder methods for other providers
  private async getSupabaseDownloadUrl(fileId: string, userId?: string): Promise<string | null> {
    // TODO: Implement
    return null;
  }

  private async deleteSupabaseFile(fileId: string, userId?: string): Promise<boolean> {
    // TODO: Implement
    return false;
  }

  private async getBackendDownloadUrl(fileId: string, userId?: string): Promise<string | null> {
    // TODO: Implement
    return null;
  }

  private async deleteBackendFile(fileId: string, userId?: string): Promise<boolean> {
    // TODO: Implement
    return false;
  }
}

// ============================================================================
// EXPORT SINGLETON INSTANCE
// ============================================================================

export const unifiedStorage = new UnifiedStorage();

// ============================================================================
// CONVENIENCE EXPORTS FOR EASY INTEGRATION
// ============================================================================

/**
 * ≡ƒÜÇ QUICK UPLOAD - One-liner for most common use case
 */
export const uploadFile = (file: File, userId?: string) =>
  unifiedStorage.uploadFile(file, { userId });

/**
 * ≡ƒôÑ QUICK DOWNLOAD - Get download URL
 */
export const getDownloadUrl = (fileId: string, userId?: string) =>
  unifiedStorage.getDownloadUrl(fileId, userId);

/**
 * ≡ƒùæ∩╕Å QUICK DELETE - Delete file
 */
export const deleteFile = (fileId: string, userId?: string) =>
  unifiedStorage.deleteFile(fileId, userId);

/**
 * ≡ƒôè QUICK INFO - Get storage usage
 */
export const getStorageInfo = (userId: string) =>
  unifiedStorage.getStorageInfo(userId);

// ============================================================================
// TYPESCRIPT TYPES FOR EASY INTEGRATION
// ============================================================================

// Note: Types are already exported above

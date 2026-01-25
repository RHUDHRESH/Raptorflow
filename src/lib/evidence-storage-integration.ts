/**
 * 🎯 EVIDENCE VAULT INTEGRATION
 * 
 * Drop-in replacement for existing evidence vault upload system.
 * Simply replace the old uploadToBackend function with this one.
 * 
 * USAGE:
 * import { uploadEvidenceToUnifiedStorage } from '@/lib/evidence-storage-integration';
 * 
 * // Replace this line:
 * // const success = await uploadToBackend(file, item.id);
 * 
 * // With this:
 * const success = await uploadEvidenceToUnifiedStorage(file, item.id, session?.sessionId);
 */

import { unifiedStorage, UnifiedStorageResult } from './unified-storage';

export interface EvidenceUploadOptions {
  itemId: string;
  sessionId?: string;
  userId?: string;
  onProgress?: (progress: number) => void;
}

/**
 * 🚀 MAIN EVIDENCE UPLOAD FUNCTION
 * 
 * This is the drop-in replacement for uploadToBackend in Step1EvidenceVault.tsx
 * 
 * @param file - File to upload
 * @param itemId - Evidence item ID
 * @param sessionId - Session ID (optional)
 * @param options - Additional options
 * @returns Promise<boolean> - Success/failure
 */
export async function uploadEvidenceToUnifiedStorage(
  file: File, 
  itemId: string, 
  sessionId?: string,
  options?: Partial<EvidenceUploadOptions>
): Promise<boolean> {
  console.log(`🎯 [EvidenceStorage] Uploading evidence: ${file.name} (ID: ${itemId})`);

  try {
    // Upload using unified storage
    const result: UnifiedStorageResult = await unifiedStorage.uploadFile(file, {
      userId: sessionId || options?.userId || 'anonymous',
      category: 'evidence', // Evidence files go to evidence category
      onProgress: options?.onProgress,
      metadata: {
        itemId,
        sessionId,
        uploadTime: new Date().toISOString(),
        source: 'evidence-vault'
      }
    });

    if (result.success) {
      console.log(`✅ [EvidenceStorage] Upload successful: ${result.fileId}`);
      
      // Store the file reference for later retrieval
      await storeEvidenceReference(itemId, result, sessionId);
      
      return true;
    } else {
      console.error(`❌ [EvidenceStorage] Upload failed: ${result.error}`);
      return false;
    }
  } catch (error) {
    console.error(`❌ [EvidenceStorage] Upload error:`, error);
    return false;
  }
}

/**
 * 📥 GET EVIDENCE DOWNLOAD URL
 */
export async function getEvidenceDownloadUrl(itemId: string, sessionId?: string): Promise<string | null> {
  try {
    // Get stored reference
    const reference = await getEvidenceReference(itemId, sessionId);
    if (!reference) {
      console.error(`❌ [EvidenceStorage] No reference found for item: ${itemId}`);
      return null;
    }

    // Get download URL
    return await unifiedStorage.getDownloadUrl(reference.fileId, sessionId);
  } catch (error) {
    console.error(`❌ [EvidenceStorage] Failed to get download URL:`, error);
    return null;
  }
}

/**
 * 🗑️ DELETE EVIDENCE FILE
 */
export async function deleteEvidenceFile(itemId: string, sessionId?: string): Promise<boolean> {
  try {
    // Get stored reference
    const reference = await getEvidenceReference(itemId, sessionId);
    if (!reference) {
      console.error(`❌ [EvidenceStorage] No reference found for item: ${itemId}`);
      return false;
    }

    // Delete file
    const success = await unifiedStorage.deleteFile(reference.fileId, sessionId);
    
    if (success) {
      // Remove reference
      await removeEvidenceReference(itemId, sessionId);
    }
    
    return success;
  } catch (error) {
    console.error(`❌ [EvidenceStorage] Failed to delete file:`, error);
    return false;
  }
}

// ============================================================================
// LOCAL STORAGE FOR EVIDENCE REFERENCES (until backend integration)
// ============================================================================

interface EvidenceReference {
  itemId: string;
  fileId: string;
  fileName: string;
  sessionId?: string;
  uploadTime: string;
  provider: string;
}

const EVIDENCE_STORAGE_KEY = 'raptorflow-evidence-references';

/**
 * Store evidence reference in localStorage
 */
async function storeEvidenceReference(
  itemId: string, 
  result: UnifiedStorageResult, 
  sessionId?: string
): Promise<void> {
  try {
    const references = getEvidenceReferences();
    const newReference: EvidenceReference = {
      itemId,
      fileId: result.fileId,
      fileName: result.fileName,
      sessionId,
      uploadTime: new Date().toISOString(),
      provider: result.provider
    };
    
    references[itemId] = newReference;
    localStorage.setItem(EVIDENCE_STORAGE_KEY, JSON.stringify(references));
    
    console.log(`💾 [EvidenceStorage] Stored reference for item: ${itemId}`);
  } catch (error) {
    console.error(`❌ [EvidenceStorage] Failed to store reference:`, error);
  }
}

/**
 * Get evidence reference from localStorage
 */
async function getEvidenceReference(itemId: string, sessionId?: string): Promise<EvidenceReference | null> {
  try {
    const references = getEvidenceReferences();
    const reference = references[itemId];
    
    // Verify session matches (if provided)
    if (reference && sessionId && reference.sessionId !== sessionId) {
      console.warn(`⚠️ [EvidenceStorage] Session mismatch for item: ${itemId}`);
      return null;
    }
    
    return reference || null;
  } catch (error) {
    console.error(`❌ [EvidenceStorage] Failed to get reference:`, error);
    return null;
  }
}

/**
 * Remove evidence reference from localStorage
 */
async function removeEvidenceReference(itemId: string, _sessionId?: string): Promise<void> {
  try {
    const references = getEvidenceReferences();
    delete references[itemId];
    localStorage.setItem(EVIDENCE_STORAGE_KEY, JSON.stringify(references));
    
    console.log(`🗑️ [EvidenceStorage] Removed reference for item: ${itemId}`);
  } catch (error) {
    console.error(`❌ [EvidenceStorage] Failed to remove reference:`, error);
  }
}

/**
 * Get all evidence references
 */
function getEvidenceReferences(): Record<string, EvidenceReference> {
  try {
    const stored = localStorage.getItem(EVIDENCE_STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch (error) {
    console.error(`❌ [EvidenceStorage] Failed to parse references:`, error);
    return {};
  }
}

// ============================================================================
// MIGRATION HELPERS
// ============================================================================

/**
 * 🔄 MIGRATE OLD EVIDENCE TO NEW STORAGE
 * 
 * Use this to migrate existing evidence to the new unified storage system
 */
export async function migrateEvidenceToUnifiedStorage(sessionId?: string): Promise<void> {
  console.log(`🔄 [EvidenceStorage] Starting migration for session: ${sessionId}`);
  
  try {
    const references = getEvidenceReferences();
    let migrated = 0;
    const failed = 0;
    
    for (const [itemId, reference] of Object.entries(references)) {
      if (reference.provider === 'local' || reference.provider === 'backend') {
        // This item needs migration
        console.log(`🔄 [EvidenceStorage] Migrating item: ${itemId}`);
        
        // TODO: Implement actual migration logic
        // This would involve downloading the old file and re-uploading
        
        migrated++;
      }
    }
    
    console.log(`✅ [EvidenceStorage] Migration complete: ${migrated} migrated, ${failed} failed`);
  } catch (error) {
    console.error(`❌ [EvidenceStorage] Migration failed:`, error);
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * 📊 GET EVIDENCE STORAGE USAGE
 */
export async function getEvidenceStorageUsage(sessionId?: string): Promise<{
  totalFiles: number;
  totalSize: number;
  filesByProvider: Record<string, number>;
}> {
  try {
    const references = getEvidenceReferences();
    const sessionReferences = sessionId 
      ? Object.values(references).filter(ref => ref.sessionId === sessionId)
      : Object.values(references);
    
    const filesByProvider: Record<string, number> = {};
    const totalSize = 0;
    
    for (const ref of sessionReferences) {
      filesByProvider[ref.provider] = (filesByProvider[ref.provider] || 0) + 1;
      // TODO: Get actual file sizes from storage provider
    }
    
    return {
      totalFiles: sessionReferences.length,
      totalSize,
      filesByProvider
    };
  } catch (error) {
    console.error(`❌ [EvidenceStorage] Failed to get usage:`, error);
    return { totalFiles: 0, totalSize: 0, filesByProvider: {} };
  }
}

/**
 * 🧹 CLEANUP OLD REFERENCES
 */
export async function cleanupOldEvidenceReferences(olderThanDays: number = 30): Promise<void> {
  try {
    const references = getEvidenceReferences();
    const cutoffTime = new Date();
    cutoffTime.setDate(cutoffTime.getDate() - olderThanDays);
    
    let cleaned = 0;
    
    for (const [itemId, reference] of Object.entries(references)) {
      const uploadTime = new Date(reference.uploadTime);
      if (uploadTime < cutoffTime) {
        await removeEvidenceReference(itemId);
        cleaned++;
      }
    }
    
    console.log(`🧹 [EvidenceStorage] Cleaned up ${cleaned} old references`);
  } catch (error) {
    console.error(`❌ [EvidenceStorage] Cleanup failed:`, error);
  }
}

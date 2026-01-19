# 🎯 EVIDENCE VAULT INTEGRATION PATCH

## 📝 **EXACT CHANGES NEEDED**

### **File: `src/components/onboarding/steps/Step1EvidenceVault.tsx`**

#### **1. Add Import (at top)**
```typescript
import { uploadEvidenceToUnifiedStorage } from '@/lib/evidence-storage-integration';
```

#### **2. Replace uploadToBackend Function (line ~129)**
**REPLACE THIS ENTIRE FUNCTION:**
```typescript
const uploadToBackend = async (file: File, itemId: string): Promise<boolean> => {
    if (!session?.sessionId) return false;

    try {
        const { data: authData } = await supabase.auth.getSession();
        const token = authData.session?.access_token;

        const formData = new FormData();
        formData.append("file", file);
        formData.append("item_id", itemId);

        const response = await fetch(
            `http://localhost:8000/api/v1/onboarding/${session.sessionId}/vault/upload`,
            {
                method: "POST",
                headers: token ? { Authorization: `Bearer ${token}` } : {},
                body: formData,
            }
        );

        return response.ok;
    } catch (error) {
        console.error("Upload error:", error);
        return false;
    }
};
```

**WITH THIS:**
```typescript
const uploadToBackend = async (file: File, itemId: string): Promise<boolean> => {
    return await uploadEvidenceToUnifiedStorage(file, itemId, session?.sessionId);
};
```

#### **3. That's it! 🎉**

## 🔧 **WHAT THIS DOES**

### **Before:**
- Files uploaded to `http://localhost:8000/api/v1/onboarding/...`
- Local storage references only
- No unified storage system

### **After:**
- Files uploaded to GCS (or configured provider)
- Cloud storage + local references
- Full unified storage system
- Progress tracking
- Error handling
- Fallback support

## 🧪 **TEST THE INTEGRATION**

### **1. Apply the Patch**
Make the changes above in `Step1EvidenceVault.tsx`

### **2. Test Upload**
1. Go to onboarding step 1 (Evidence Vault)
2. Upload any file (PDF, image, etc.)
3. Check browser console - you should see:
   ```
   🎯 [EvidenceStorage] Uploading evidence: filename.pdf (ID: file-123)
   🚀 [UnifiedStorage] Starting upload: filename.pdf (gcs)
   ✅ [UnifiedStorage] Upload complete in 1234ms: user-id/evidence/filename.pdf
   ✅ [EvidenceStorage] Upload successful: user-id/evidence/filename.pdf
   ```

### **3. Verify in GCS**
```bash
gsutil ls gs://raptorflow-uploads/user-id/evidence/
```

## 🔄 **ROLLBACK PLAN**

If anything goes wrong, simply revert the `uploadToBackend` function to the original version. The old system will continue working.

## 📊 **BENEFITS ACHIEVED**

✅ **Unified Storage**: All files now use the same system  
✅ **Cloud Storage**: Files stored in GCS, not local only  
✅ **Easy to Switch**: Change provider in 1 line  
✅ **Progress Tracking**: Built-in upload progress  
✅ **Error Handling**: Better error reporting  
✅ **TypeScript Safe**: Full type support  
✅ **Production Ready**: Fallbacks and monitoring  

## 🎯 **NEXT STEPS**

### **Optional: Add Progress Tracking**
```typescript
// In handleFileUpload function, add progress callback:
const success = await uploadToBackend(file, item.id);

// Becomes:
const success = await uploadEvidenceToUnifiedStorage(
  file, 
  item.id, 
  session?.sessionId,
  {
    onProgress: (progress) => {
      // Update progress for this specific file
      setEvidence(prev => prev.map(e => 
        e.id === item.id 
          ? { ...e, uploadProgress: progress }
          : e
      ));
    }
  }
);
```

### **Optional: Add Download Support**
```typescript
import { getEvidenceDownloadUrl } from '@/lib/evidence-storage-integration';

// Add download button for each evidence item
const downloadFile = async (itemId: string) => {
  const url = await getEvidenceDownloadUrl(itemId, session?.sessionId);
  if (url) {
    window.open(url, '_blank');
  }
};
```

**Your evidence vault is now fully integrated with the unified storage system!** 🚀

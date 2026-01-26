# Technical Specification: Onboarding Step 1 Overhaul

## Task Complexity Assessment

**Difficulty: Medium**

This task requires refactoring an existing onboarding step to eliminate mock data, graceful fallbacks, and hardcoded values while ensuring real AI-powered functionality works correctly. The complexity is moderate because:

- Multiple interconnected components (frontend + backend)
- Existing infrastructure is present but needs cleanup
- Requires careful removal of fallback mechanisms without breaking the system
- UI improvements and duplicate detection add additional scope

---

## Executive Summary

**Objective**: Transform Onboarding Step 1 (Evidence Vault) from a prototype with mocks and fallbacks into a production-ready, fully functional system that:

1. **Eliminates all mock data** - No hardcoded responses or simulated behavior
2. **Removes graceful fallbacks** - System must work with real APIs or fail clearly
3. **Implements real AI classification** - Evidence classifier must work without local heuristics
4. **Adds duplicate detection** - Prevent users from uploading the same file multiple times
5. **Improves UI/UX** - Make buttons work reliably and design look "nice and crisp"

---

## Current State Analysis

### Problems Identified

#### 1. **Mock Data in Frontend**
- **Location**: `src/components/onboarding/steps/Step2AutoExtraction.tsx:119-126`
- **Issue**: `generateMockFacts()` function provides hardcoded extraction results
- **Impact**: Users see fake data instead of real AI extraction

#### 2. **Graceful Fallback Logic**
- **Location**: `src/components/onboarding/steps/Step1EvidenceVault.tsx:113-122`
- **Issue**: When API fails, falls back to simple filename heuristics
- **Impact**: Classification appears to work but isn't using AI

#### 3. **Fallback System Architecture**
- **Location**: `backend/cognitive/fallback.py` (entire file)
- **Issue**: Complex graceful degradation system that masks failures
- **Impact**: System never truly fails, making bugs hard to detect

#### 4. **Simple/Mock Files Scattered Everywhere**
- **Locations**:
  - `backend/simple_backend.py`
  - `backend/config_simple.py`
  - `backend/run_simple.py`
  - `cloud-scraper/simple_*.py` (7 files)
  - `tests/*simple*` (multiple files)
- **Impact**: Confusion about which backend is "real" vs "simple"

#### 5. **Missing Features**
- No duplicate detection for evidence uploads
- Classification API endpoint not properly wired
- Extraction API may return empty results

#### 6. **UI/UX Issues**
- Buttons may not have proper loading states
- Error handling not user-friendly
- Design could be more polished

---

## Technical Context

### Technology Stack

**Frontend**:
- **Framework**: Next.js 14.2.5 (React 18.3.1)
- **Language**: TypeScript 5.6.3
- **State Management**: Zustand 5.0.9
- **Styling**: Tailwind CSS 3.4.18
- **Animation**: GSAP (via `gsap` import)
- **UI Components**: Custom Blueprint design system

**Backend**:
- **Framework**: FastAPI (Python)
- **AI/ML**: Google Vertex AI, LangChain
- **Storage**: Google Cloud Storage
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: Supabase Auth

**Key Dependencies**:
- `@supabase/supabase-js` for backend communication
- `lucide-react` for icons
- `zod` for validation

---

## Implementation Approach

### Phase 1: Cleanup (Remove Mocks & Fallbacks)

#### 1.1 Frontend Cleanup

**File: `src/components/onboarding/steps/Step1EvidenceVault.tsx`**

**Changes**:
```typescript
// REMOVE: Lines 113-122 (Fallback heuristic logic)
// OLD:
catch (error) {
    console.error('Classification error:', error);
    // Fallback to simple local heuristic only on complete API failure
    const lowerName = fileName.toLowerCase();
    let category = "other";
    if (lowerName.includes("manifesto") || lowerName.includes("brand")) category = "manifesto";
    else if (lowerName.includes("deck") || lowerName.includes("pitch")) category = "sales_deck";
    else if (fileType?.includes("image")) category = "product_screenshots";

    setEvidence(prev => prev.map(e => e.id === itemId ? { ...e, status: "complete", matchedCategory: category } : e));
}

// NEW:
catch (error) {
    console.error('Classification error:', error);
    // Mark as error, no fallback
    setEvidence(prev => prev.map(e =>
        e.id === itemId
            ? { ...e, status: "error", errorMessage: error.message || "Classification failed" }
            : e
    ));
    // Show user-friendly error notification
    toast.error("Failed to classify file. Please try again or check your connection.");
}
```

**File: `src/components/onboarding/steps/Step2AutoExtraction.tsx`**

**Changes**:
```typescript
// REMOVE: Lines 79, 85-88 (Mock data fallback)
// OLD:
const factsToUse = extractedFacts.length > 0 ? extractedFacts : generateMockFacts();
setFacts(factsToUse);

// And in catch block:
const mockFacts = generateMockFacts();
setFacts(mockFacts);
updateStepData(2, { facts: mockFacts });

// NEW:
if (extractedFacts.length === 0) {
    throw new Error("No facts extracted from evidence. Please ensure you have uploaded valid documents.");
}
setFacts(extractedFacts);

// And in catch block:
console.error('Extraction error:', error);
setFacts([]);
updateStepData(2, { facts: [], error: error.message });
updateStepStatus(2, "error");
toast.error("Failed to extract insights. Please review your evidence and try again.");

// DELETE: Lines 119-126 (generateMockFacts function entirely)
```

#### 1.2 Backend Cleanup

**File: `backend/cognitive/fallback.py`**
- **Action**: DELETE entire file or disable all fallback mechanisms
- **Rationale**: Fallbacks mask real failures; we want clear error reporting

**Files to DELETE**:
- `backend/simple_backend.py`
- `backend/config_simple.py`
- `backend/run_simple.py`
- All `cloud-scraper/simple_*.py` files
- `backend/.env.simple`

**Reason**: These are development/testing artifacts that shouldn't be in production

#### 1.3 Update API Endpoints

**File: `backend/api/v1/onboarding.py`**

**Verify/Fix**:
1. `/api/v1/onboarding/{session_id}/classify-evidence` endpoint (lines 215-232)
   - Ensure it calls `evidence_classifier.classify_document()` without fallbacks
   - Return proper error responses (400/500) on failure
   - Add request validation with Pydantic

2. `/api/v1/onboarding/{session_id}/extract-facts` endpoint (lines 235-254)
   - Ensure it calls `extraction_orchestrator.extract_facts_from_evidence()`
   - Must return real extracted facts or clear error
   - No mock data generation

**Changes**:
```python
@router.post("/{session_id}/classify-evidence")
async def classify_evidence(session_id: str, evidence_data: Dict[str, Any]):
    """Classify evidence using AI - NO FALLBACKS"""
    try:
        if not evidence_classifier:
            raise HTTPException(
                status_code=503,
                detail="Evidence classifier service unavailable. Please contact support."
            )

        # Validate input
        if not evidence_data.get("name"):
            raise HTTPException(status_code=400, detail="Evidence name is required")

        result = await evidence_classifier.classify_document(evidence_data)

        # Ensure we got a valid result
        if not result or not hasattr(result, 'category'):
            raise HTTPException(
                status_code=500,
                detail="Classification failed to produce valid result"
            )

        # Store classification in database
        await onboarding_repo.store_evidence_classification(session_id, result)

        return {
            "success": True,
            "classification": {
                "category": result.category,
                "confidence": result.confidence,
                "reasoning": result.reasoning
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error classifying evidence: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )
```

### Phase 2: Add Duplicate Detection

**File: `src/components/onboarding/steps/Step1EvidenceVault.tsx`**

**Implementation**:
```typescript
// Add duplicate detection helper
const isDuplicate = (newFile: File | string, existingEvidence: EvidenceItem[]): boolean => {
    if (typeof newFile === 'string') {
        // URL duplicate check
        return existingEvidence.some(e => e.type === 'url' && e.url === newFile);
    }

    // File duplicate check (by name and size)
    return existingEvidence.some(e =>
        e.type === 'file' &&
        e.name === newFile.name &&
        e.size === newFile.size
    );
};

// Update handleFiles function
const handleFiles = async (files: FileList | null) => {
    if (!files) return;

    const newItems: EvidenceItem[] = [];
    const duplicates: string[] = [];

    Array.from(files).forEach(file => {
        if (isDuplicate(file, evidence)) {
            duplicates.push(file.name);
        } else {
            newItems.push({
                id: `file-${Date.now()}-${Math.random()}`,
                type: "file",
                name: file.name,
                fileType: file.type,
                size: file.size,
                status: "processing",
                tags: [],
            });
        }
    });

    if (duplicates.length > 0) {
        toast.warning(`Skipped ${duplicates.length} duplicate file(s): ${duplicates.join(', ')}`);
    }

    if (newItems.length === 0) return;

    const updated = [...evidence, ...newItems];
    saveToStore(updated);

    // Process each file
    for (const item of newItems) {
        await classifyEvidence(item.id, item.name, item.fileType);
    }
};

// Update handleUrl function
const handleUrl = () => {
    if (!urlInput.trim()) return;

    if (isDuplicate(urlInput, evidence)) {
        toast.warning("This URL has already been added");
        return;
    }

    const newItem: EvidenceItem = {
        id: `url-${Date.now()}`,
        type: "url",
        name: urlInput,
        url: urlInput,
        status: "processing",
        tags: [],
    };

    const updated = [...evidence, newItem];
    saveToStore(updated);
    setUrlInput("");

    // Classify URL
    classifyEvidence(newItem.id, newItem.name);
};
```

### Phase 3: UI/UX Improvements

#### 3.1 Better Error States

**Add toast notifications** (install `sonner` if not present):
```typescript
import { toast } from "sonner";

// In error cases:
toast.error("Classification failed", {
    description: "Unable to classify this file. Please check your connection and try again.",
    duration: 5000
});

// In success cases:
toast.success("Evidence classified", {
    description: `Identified as: ${category}`,
    duration: 3000
});
```

#### 3.2 Loading States for Buttons

**File: `src/components/onboarding/steps/Step1EvidenceVault.tsx`**

```typescript
const [isProcessing, setIsProcessing] = useState(false);

const handleUrl = async () => {
    if (!urlInput.trim()) return;

    setIsProcessing(true);
    try {
        // ... URL handling logic
    } finally {
        setIsProcessing(false);
    }
};

// Update button
<BlueprintButton
    onClick={handleUrl}
    disabled={!urlInput || isProcessing}
    className="h-10 px-4"
    variant="secondary"
>
    {isProcessing ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
</BlueprintButton>
```

#### 3.3 Design Polish

**Visual improvements**:
1. Add subtle box-shadow on hover for evidence cards
2. Improve spacing and typography consistency
3. Add smooth transitions for all interactive elements
4. Show upload progress indicator for large files
5. Better visual feedback for drag-and-drop

**CSS additions**:
```typescript
// Evidence card improvements
<div className="group flex items-center justify-between p-3 bg-[var(--paper)] border border-[var(--border-subtle)] rounded-lg shadow-sm hover:border-[var(--blueprint)] hover:shadow-md transition-all duration-200 hover:scale-[1.01]">

// Drop zone improvements
<div className={cn(
    "relative group border-2 border-dashed rounded-xl bg-[var(--paper)] transition-all duration-300 cursor-pointer overflow-hidden",
    isDragging
        ? "bg-[var(--blueprint-light)]/10 border-[var(--blueprint)] scale-[1.02] shadow-lg"
        : "border-[var(--border)] hover:border-[var(--ink-muted)] hover:shadow-sm"
)}>
```

---

## Source Code Structure Changes

### Files to Modify

1. ✏️ `src/components/onboarding/steps/Step1EvidenceVault.tsx`
   - Remove fallback classification logic
   - Add duplicate detection
   - Improve error handling
   - Add loading states
   - UI polish

2. ✏️ `src/components/onboarding/steps/Step2AutoExtraction.tsx`
   - Remove `generateMockFacts()` function
   - Remove all mock data fallbacks
   - Improve error handling

3. ✏️ `backend/api/v1/onboarding.py`
   - Strengthen error handling in `/classify-evidence` endpoint
   - Strengthen error handling in `/extract-facts` endpoint
   - Add request validation

4. ✏️ `backend/agents/specialists/evidence_classifier.py`
   - Review and ensure no fallback logic exists
   - Verify classification always returns valid results or throws

5. ✏️ `backend/agents/specialists/extraction_orchestrator.py`
   - Review and ensure no mock data generation
   - Verify extraction returns real data or throws

### Files to Delete

1. ❌ `backend/cognitive/fallback.py`
2. ❌ `backend/simple_backend.py`
3. ❌ `backend/config_simple.py`
4. ❌ `backend/run_simple.py`
5. ❌ `backend/.env.simple`
6. ❌ `cloud-scraper/simple_*.py` (7 files)
7. ❌ All test files with "simple" in name (unless actively used)

### Files to Create

1. ✨ `src/lib/duplicateDetection.ts` (optional utility)
2. ✨ `src/components/ui/Toast.tsx` (if not using sonner)

---

## Data Model Changes

### Evidence Item Interface Update

**File: `src/components/onboarding/steps/Step1EvidenceVault.tsx`**

```typescript
interface EvidenceItem {
    id: string;
    type: "url" | "file";
    name: string;
    status: "pending" | "processing" | "complete" | "error";
    url?: string;
    fileType?: string;
    size?: number;
    tags: string[];
    ocrProcessed?: boolean;
    errorMessage?: string;          // Added
    matchedCategory?: string;
    classificationConfidence?: number;  // Added
    uploadedAt?: Date;              // Added for better tracking
}
```

---

## API/Interface Changes

### Frontend to Backend Communication

**Endpoint: `POST /api/v1/onboarding/{session_id}/classify-evidence`**

**Request**:
```json
{
    "session_id": "string",
    "evidence_data": {
        "name": "string (required)",
        "file_type": "string (optional)",
        "item_id": "string (required)",
        "size": "number (optional)"
    }
}
```

**Response (Success)**:
```json
{
    "success": true,
    "classification": {
        "category": "pitch_deck" | "product_screenshot" | "website_content" | ...,
        "confidence": 0.85,
        "reasoning": "Classified as pitch_deck with confidence 0.85. Key indicators: ..."
    }
}
```

**Response (Error)**:
```json
{
    "detail": "Classification failed: <specific error message>",
    "status_code": 400 | 500 | 503
}
```

---

## Verification Approach

### Testing Strategy

#### 1. Unit Tests

**Frontend**:
```typescript
// tests/components/onboarding/Step1EvidenceVault.test.tsx
describe('Step1EvidenceVault', () => {
    it('should detect duplicate files', () => {
        // Test duplicate detection logic
    });

    it('should show error when classification fails', () => {
        // Mock API failure and verify error display
    });

    it('should disable upload button during processing', () => {
        // Test loading states
    });
});
```

**Backend**:
```python
# backend/tests/test_evidence_classifier.py
def test_classification_without_fallback():
    """Ensure classifier fails clearly when it cannot classify"""
    classifier = EvidenceClassifier()
    with pytest.raises(HTTPException):
        await classifier.classify_document({})
```

#### 2. Integration Tests

**Test Flow**:
1. Upload a PDF file
2. Verify classification API is called (not fallback)
3. Verify correct category is returned
4. Verify duplicate upload is rejected
5. Test error handling when backend is unavailable

#### 3. Manual Testing Checklist

- [ ] Upload same file twice → Should show warning
- [ ] Upload different file types (PDF, PNG, URL)
- [ ] Force API failure (stop backend) → Should show error, not fallback
- [ ] Upload large file → Should show progress
- [ ] Upload invalid file → Should handle gracefully
- [ ] URL input validation
- [ ] Button states (disabled, loading, enabled)
- [ ] Visual design looks crisp and professional

#### 4. Linting & Type Checking

```bash
# Run before committing
npm run type-check
npm run lint
```

---

## Success Criteria

### Functional Requirements

✅ **No Mock Data**
- All data comes from real backend APIs
- No hardcoded responses anywhere in Step 1 or Step 2

✅ **No Graceful Fallbacks**
- System fails with clear error messages when backend is unavailable
- No local heuristics used as fallback

✅ **Real AI Classification**
- Evidence classifier uses Vertex AI
- Classification results are accurate and include confidence scores

✅ **Duplicate Detection**
- Users cannot upload the same file twice
- URLs are deduplicated

✅ **Working UI**
- All buttons work reliably
- Loading states show during processing
- Error states are clear and actionable

✅ **Crisp Design**
- Consistent spacing and typography
- Smooth animations
- Professional appearance

### Non-Functional Requirements

✅ **Performance**
- File uploads complete within 10 seconds
- Classification response < 3 seconds
- No UI freezing during processing

✅ **Reliability**
- Error rate < 1% for valid uploads
- Backend API uptime > 99%

✅ **Maintainability**
- Code is well-documented
- No dead code or unused files
- Clear separation of concerns

---

## Risk Assessment

### High Risk

🔴 **Backend API Unavailability**
- **Mitigation**: Implement retry logic (3 attempts with exponential backoff)
- **Fallback**: Clear error message directing user to support

### Medium Risk

🟡 **Evidence Classifier Returns Low Confidence**
- **Mitigation**: Set minimum confidence threshold (0.5)
- **Handling**: Mark as "unclassified" and allow manual categorization

🟡 **Large File Upload Timeout**
- **Mitigation**: Implement chunked upload for files > 10MB
- **User Feedback**: Show upload progress bar

### Low Risk

🟢 **Duplicate Detection False Positives**
- **Mitigation**: Use file hash instead of name+size
- **User Option**: Allow override with confirmation

---

## Dependencies

### External Services

- ✅ Google Vertex AI (for classification)
- ✅ Google Cloud Storage (for file storage)
- ✅ Supabase (for session/data persistence)
- ✅ Backend API (FastAPI server must be running)

### Internal Dependencies

- ✅ `backend/agents/specialists/evidence_classifier.py`
- ✅ `backend/agents/specialists/extraction_orchestrator.py`
- ✅ `backend/services/ocr_service.py`
- ✅ `src/stores/onboardingStore.ts`

---

## Implementation Timeline

### Estimated Time: 6-8 hours

1. **Cleanup (2-3 hours)**
   - Remove mocks and fallbacks
   - Delete unnecessary files
   - Update API endpoints

2. **Duplicate Detection (1-2 hours)**
   - Implement detection logic
   - Add UI feedback

3. **UI/UX Polish (2-3 hours)**
   - Loading states
   - Error handling
   - Design improvements

4. **Testing (1 hour)**
   - Manual testing
   - Fix bugs
   - Verify all criteria met

---

## Rollback Plan

If issues arise:

1. **Revert commits** to last stable state
2. **Re-enable fallbacks temporarily** (if critical)
3. **Deploy hotfix** for any breaking bugs
4. **Review logs** to identify root cause

**Git Strategy**: Create feature branch `feature/onboarding-step1-cleanup` for easy rollback

---

## Post-Implementation

### Documentation Updates

- Update `README.md` with new onboarding flow
- Document API endpoints in `docs/api/onboarding.md`
- Add troubleshooting guide for common errors

### Monitoring

- Add error tracking for classification failures
- Monitor API response times
- Track duplicate detection metrics

---

## Conclusion

This specification provides a complete blueprint for transforming Onboarding Step 1 from a prototype into production-ready code. The focus is on eliminating mocks, strengthening error handling, and creating a polished user experience.

**Key Principle**: Fail fast and clearly rather than masking issues with fallbacks.

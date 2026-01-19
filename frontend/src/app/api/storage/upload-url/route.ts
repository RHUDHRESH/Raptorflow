import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { user_id, file_name, file_type, file_size } = await request.json();

    // Validate input
    if (!user_id || !file_name || !file_type) {
      return NextResponse.json(
        { error: 'Missing required fields: user_id, file_name, file_type' },
        { status: 400 }
      );
    }

    // File size validation (max 100MB)
    const MAX_FILE_SIZE = 100 * 1024 * 1024;
    if (file_size > MAX_FILE_SIZE) {
      return NextResponse.json(
        { error: `File size exceeds maximum limit of ${MAX_FILE_SIZE / (1024 * 1024)}MB` },
        { status: 400 }
      );
    }

    // MIME type validation
    const ALLOWED_TYPES = {
      'avatar': ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
      'document': ['application/pdf', 'text/plain', 'application/json', 'text/csv'],
      'workspace': ['image/jpeg', 'image/png', 'application/pdf', 'text/csv', 'application/vnd.ms-excel']
    };

    const allowedTypes = ALLOWED_TYPES[file_type as keyof typeof ALLOWED_TYPES] || [];
    if (allowedTypes.length > 0) {
      // For now, we'll validate basic MIME types
      const mimeTypes = {
        'image/jpeg': 'image/jpeg',
        'image/png': 'image/png', 
        'image/webp': 'image/webp',
        'image/gif': 'image/gif',
        'application/pdf': 'application/pdf',
        'text/plain': 'text/plain',
        'application/json': 'application/json',
        'text/csv': 'text/csv'
      };

      // Extract MIME type from file name
      const fileExtension = file_name.split('.').pop()?.toLowerCase();
      
      // Map extensions to MIME types
      const extensionToMime: Record<string, string> = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'webp': 'image/webp',
        'gif': 'image/gif',
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'json': 'application/json',
        'csv': 'text/csv'
      };
      
      const mimeType = extensionToMime[fileExtension] || mimeTypes[fileExtension as keyof typeof mimeTypes];

      if (!mimeType || !allowedTypes.includes(mimeType)) {
        return NextResponse.json(
          { error: `File type not allowed for ${file_type}` },
          { status: 400 }
        );
      }
    }

    // Generate unique file path
    const timestamp = Date.now();
    const randomId = Math.random().toString(36).substring(2, 15);
    const file_extension = file_name.split('.').pop();
    const safe_file_name = file_name.replace(/[^a-zA-Z0-9.-]/g, '_');
    const file_path = `${user_id}/${file_type}/${timestamp}_${randomId}_${safe_file_name}`;

    // For now, return a mock response until backend GCS is ready
    // TODO: Integrate with backend GCS service
    const upload_url = `https://storage.googleapis.com/mock-bucket/${file_path}`;
    
    return NextResponse.json({
      upload_url,
      file_path,
      expires_in: 3600 // 1 hour
    });

  } catch (error: any) {
    console.error('Error generating upload URL:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}

import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { user_id, file_path } = await request.json();

    // Validate input
    if (!user_id || !file_path) {
      return NextResponse.json(
        { error: 'Missing required fields: user_id, file_path' },
        { status: 400 }
      );
    }

    // Security: Ensure user can only access their own files
    if (!file_path.startsWith(`${user_id}/`)) {
      return NextResponse.json(
        { error: 'Access denied: Invalid file path' },
        { status: 403 }
      );
    }

    // Extract file info from path
    const file_name = file_path.split('/').pop() || '';
    const file_extension = file_name.split('.').pop()?.toLowerCase();
    
    // Estimate file size based on type (mock for now)
    const sizeMap: Record<string, number> = {
      'pdf': 1024 * 1024, // 1MB
      'jpg': 500 * 1024,  // 500KB
      'jpeg': 500 * 1024, // 500KB
      'png': 800 * 1024,  // 800KB
      'txt': 10 * 1024,   // 10KB
      'csv': 100 * 1024,  // 100KB
      'json': 50 * 1024   // 50KB
    };

    const size = sizeMap[file_extension || ''] || 100 * 1024; // Default 100KB

    // TODO: Integrate with backend GCS service to get real file info
    return NextResponse.json({
      file_name,
      size,
      content_type: getContentType(file_extension || ''),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Error getting file info:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}

function getContentType(extension: string): string {
  const contentTypes: Record<string, string> = {
    'pdf': 'application/pdf',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp',
    'txt': 'text/plain',
    'csv': 'text/csv',
    'json': 'application/json',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  };
  
  return contentTypes[extension] || 'application/octet-stream';
}

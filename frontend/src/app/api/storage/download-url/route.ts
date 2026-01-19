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

    // For now, return a mock response until backend GCS is ready
    // TODO: Integrate with backend GCS service to generate signed URL
    const download_url = `https://storage.googleapis.com/mock-bucket/${file_path}?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mock&X-Goog-Date=mock&X-Goog-Expires=3600&X-Goog-SignedHeaders=host&X-Goog-Signature=mock`;
    
    return NextResponse.json({
      download_url,
      expires_in: 3600 // 1 hour
    });

  } catch (error: any) {
    console.error('Error generating download URL:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}

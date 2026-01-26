import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return handleProxy(request, params.path);
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return handleProxy(request, params.path);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return handleProxy(request, params.path);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return handleProxy(request, params.path);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return handleProxy(request, params.path);
}

async function handleProxy(request: NextRequest, pathSegments: string[]) {
  try {
    const path = pathSegments.join('/');
    const url = new URL(path, BACKEND_URL);

    // Copy query parameters
    request.nextUrl.searchParams.forEach((value, key) => {
      url.searchParams.set(key, value);
    });

    // Get request body
    let body: string | undefined;
    if (['POST', 'PUT', 'PATCH'].includes(request.method)) {
      body = await request.text();
    }

    // Get headers, excluding Next.js specific headers
    const headers = new Headers();
    request.headers.forEach((value, key) => {
      if (!key.startsWith('x-') && key !== 'host') {
        headers.set(key, value);
      }
    });

    // Add auth header if available
    const authHeader = request.headers.get('authorization');
    if (authHeader) {
      headers.set('authorization', authHeader);
    }

    // Make the request to backend
    const response = await fetch(url.toString(), {
      method: request.method,
      headers,
      body,
      cache: 'no-store',
    });

    // Create response
    const responseHeaders = new Headers();
    response.headers.forEach((value, key) => {
      if (!key.startsWith('x-') && key !== 'connection') {
        responseHeaders.set(key, value);
      }
    });

    const responseText = await response.text();

    return new NextResponse(responseText, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Internal server error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

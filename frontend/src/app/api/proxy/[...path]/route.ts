/**
 * API Proxy Route - Routes frontend API calls to backend server
 * This handles the cross-origin requests between Vercel frontend and backend
 */

import { NextRequest, NextResponse } from 'next/server';

// Backend server URL - update this to your actual backend URL
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://raptorflow-backend.onrender.com';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return handleProxyRequest(request, path);
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return handleProxyRequest(request, path);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return handleProxyRequest(request, path);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return handleProxyRequest(request, path);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return handleProxyRequest(request, path);
}

async function handleProxyRequest(request: NextRequest, pathSegments: string[]) {
  try {
    // Construct the backend URL
    const path = pathSegments.join('/');
    const backendUrl = `${BACKEND_URL}/api/${path}`;

    // Get the request body
    const body = request.method !== 'GET' && request.method !== 'HEAD'
      ? await request.text()
      : undefined;

    // Get headers from the original request
    const headers = new Headers();

    // Copy relevant headers
    const allowedHeaders = [
      'content-type',
      'authorization',
      'accept',
      'accept-language',
      'user-agent',
      'x-requested-with'
    ];

    allowedHeaders.forEach(header => {
      const value = request.headers.get(header);
      if (value) {
        headers.set(header, value);
      }
    });

    // Set required headers
    const clientIP = request.headers.get('x-forwarded-for') ||
      request.headers.get('x-real-ip') ||
      'unknown';
    headers.set('X-Forwarded-For', clientIP);
    headers.set('X-Forwarded-Host', request.headers.get('host') || 'unknown');
    headers.set('X-Forwarded-Proto', request.headers.get('x-forwarded-proto') || 'https');

    // Make the request to the backend
    const response = await fetch(backendUrl, {
      method: request.method,
      headers,
      body,
      // Don't follow redirects automatically
      redirect: 'manual',
    });

    // Handle redirects
    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get('location');
      if (location) {
        return NextResponse.redirect(location, response.status);
      }
    }

    // Create response with headers from backend
    const responseHeaders = new Headers();

    // Copy relevant response headers
    const responseAllowedHeaders = [
      'content-type',
      'content-length',
      'cache-control',
      'etag',
      'last-modified',
      'set-cookie'
    ];

    responseAllowedHeaders.forEach(header => {
      const value = response.headers.get(header);
      if (value) {
        responseHeaders.set(header, value);
      }
    });

    // Add CORS headers
    responseHeaders.set('Access-Control-Allow-Origin', '*');
    responseHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS');
    responseHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');
    responseHeaders.set('Access-Control-Allow-Credentials', 'true');

    // Get response body
    const responseBody = await response.text();

    // Return the response
    return new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });

  } catch (error) {
    console.error('Proxy request error:', error);

    // Return error response
    return NextResponse.json(
      {
        error: 'Proxy request failed',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      },
      {
        status: 500,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
          'Access-Control-Allow-Credentials': 'true',
        }
      }
    );
  }
}

// Handle OPTIONS requests for CORS
export async function OPTIONS(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
      'Access-Control-Allow-Credentials': 'true',
      'Access-Control-Max-Age': '86400',
    },
  });
}

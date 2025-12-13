/**
 * Figma Connector
 *
 * Integration with Figma API for design assets and collaboration.
 */

import { BaseConnector, ConnectorConfig, ConnectorResult } from './interface';

export interface FigmaFile {
  key: string;
  name: string;
  thumbnail_url: string;
  last_modified: string;
  version: string;
}

export interface FigmaImage {
  images: Record<string, string>; // node_id -> image_url
  err?: string;
}

export interface FigmaComment {
  id: string;
  message: string;
  user: {
    handle: string;
    img_url: string;
  };
  created_at: string;
  resolved_at?: string;
}

export class FigmaConnector extends BaseConnector {
  private baseUrl = 'https://api.figma.com/v1';

  constructor(config: ConnectorConfig) {
    super(config);

    if (!config.accessToken) {
      throw new Error('Figma access token required');
    }
  }

  async testConnection(): Promise<ConnectorResult<boolean>> {
    try {
      const response = await this.makeRequest('/me');
      return {
        success: true,
        data: true,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Figma connection failed: ${error.message}`,
      };
    }
  }

  async getFile(fileKey: string): Promise<ConnectorResult<FigmaFile>> {
    try {
      const response = await this.makeRequest(`/files/${fileKey}`);

      const file: FigmaFile = {
        key: response.key,
        name: response.name,
        thumbnail_url: response.thumbnail_url,
        last_modified: response.last_modified,
        version: response.version,
      };

      return {
        success: true,
        data: file,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to get Figma file: ${error.message}`,
      };
    }
  }

  async getFileImages(fileKey: string, nodeIds: string[]): Promise<ConnectorResult<FigmaImage>> {
    try {
      const nodeIdsParam = nodeIds.join(',');
      const response = await this.makeRequest(`/images/${fileKey}?ids=${nodeIdsParam}&format=png`);

      return {
        success: true,
        data: response,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to get file images: ${error.message}`,
      };
    }
  }

  async getComments(fileKey: string): Promise<ConnectorResult<FigmaComment[]>> {
    try {
      const response = await this.makeRequest(`/files/${fileKey}/comments`);

      const comments: FigmaComment[] = response.comments.map((comment: any) => ({
        id: comment.id,
        message: comment.message,
        user: comment.user,
        created_at: comment.created_at,
        resolved_at: comment.resolved_at,
      }));

      return {
        success: true,
        data: comments,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to get comments: ${error.message}`,
      };
    }
  }

  getMetadata() {
    return {
      name: 'Figma Design',
      description: 'Figma API integration for design assets and collaboration',
      capabilities: [
        'get_file',
        'get_images',
        'get_comments',
        'export_designs',
        'real_time_collaboration',
      ],
      rateLimits: {
        requests: 1000, // per hour for most endpoints
        period: 3600000,
      },
      costPerRequest: 0, // Free tier available
    };
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        'X-Figma-Token': this.config.accessToken!,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`Figma API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }
}

// Stub implementation
export class FigmaConnectorStub extends BaseConnector {
  private mockFiles: Map<string, FigmaFile> = new Map();

  constructor(config: ConnectorConfig) {
    super(config);

    // Initialize with mock data
    this.mockFiles.set('mock_file_1', {
      key: 'mock_file_1',
      name: 'Brand Guidelines',
      thumbnail_url: 'https://via.placeholder.com/400x300',
      last_modified: new Date().toISOString(),
      version: '1.0.0',
    });
  }

  async testConnection(): Promise<ConnectorResult<boolean>> {
    return {
      success: true,
      data: true,
    };
  }

  async getFile(fileKey: string): Promise<ConnectorResult<FigmaFile>> {
    const file = this.mockFiles.get(fileKey);

    if (!file) {
      return {
        success: false,
        error: 'File not found',
      };
    }

    console.log(`🎨 [STUB] Retrieved Figma file: ${file.name}`);

    return {
      success: true,
      data: file,
    };
  }

  async getFileImages(fileKey: string, nodeIds: string[]): Promise<ConnectorResult<FigmaImage>> {
    const images: Record<string, string> = {};
    nodeIds.forEach(nodeId => {
      images[nodeId] = `https://via.placeholder.com/800x600?text=Figma+Image+${nodeId}`;
    });

    console.log(`🖼️ [STUB] Generated ${nodeIds.length} mock images`);

    return {
      success: true,
      data: { images },
    };
  }

  async getComments(fileKey: string): Promise<ConnectorResult<FigmaComment[]>> {
    const mockComments: FigmaComment[] = [
      {
        id: 'comment_1',
        message: 'Great work on the brand colors!',
        user: {
          handle: 'designer',
          img_url: 'https://via.placeholder.com/40x40',
        },
        created_at: new Date(Date.now() - 86400000).toISOString(),
      },
    ];

    return {
      success: true,
      data: mockComments,
    };
  }

  getMetadata() {
    return {
      name: 'Figma Design (Stub)',
      description: 'Stub implementation for development and testing',
      capabilities: ['get_file', 'get_images', 'get_comments'],
      rateLimits: {
        requests: 1000,
        period: 3600000,
      },
    };
  }
}


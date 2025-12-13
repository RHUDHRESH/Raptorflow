/**
 * Google Drive Connector
 *
 * Integration with Google Drive API for file storage and collaboration.
 */

import { BaseConnector, ConnectorConfig, ConnectorResult } from './interface';

export interface DriveFile {
  id: string;
  name: string;
  mimeType: string;
  webViewLink: string;
  downloadUrl?: string;
  thumbnailLink?: string;
  size?: string;
  modifiedTime: string;
  owners: Array<{
    displayName: string;
    emailAddress: string;
  }>;
  shared: boolean;
}

export interface DriveFolder {
  id: string;
  name: string;
  mimeType: string;
  parents?: string[];
  createdTime: string;
  modifiedTime: string;
}

export class GoogleDriveConnector extends BaseConnector {
  private baseUrl = 'https://www.googleapis.com/drive/v3';

  constructor(config: ConnectorConfig) {
    super(config);

    if (!config.accessToken) {
      throw new Error('Google Drive access token required');
    }
  }

  async testConnection(): Promise<ConnectorResult<boolean>> {
    try {
      await this.makeRequest('/about?fields=user');
      return {
        success: true,
        data: true,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Google Drive connection failed: ${error.message}`,
      };
    }
  }

  async listFiles(folderId?: string, query?: string): Promise<ConnectorResult<DriveFile[]>> {
    try {
      let q = "trashed=false";
      if (folderId) {
        q += ` and '${folderId}' in parents`;
      }
      if (query) {
        q += ` and name contains '${query}'`;
      }

      const response = await this.makeRequest(`/files?q=${encodeURIComponent(q)}&fields=files(id,name,mimeType,webViewLink,thumbnailLink,size,modifiedTime,owners,shared)`);

      const files: DriveFile[] = response.files.map((file: any) => ({
        id: file.id,
        name: file.name,
        mimeType: file.mimeType,
        webViewLink: file.webViewLink,
        thumbnailLink: file.thumbnailLink,
        size: file.size,
        modifiedTime: file.modifiedTime,
        owners: file.owners || [],
        shared: file.shared || false,
      }));

      return {
        success: true,
        data: files,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to list files: ${error.message}`,
      };
    }
  }

  async createFolder(name: string, parentId?: string): Promise<ConnectorResult<string>> {
    try {
      const metadata = {
        name,
        mimeType: 'application/vnd.google-apps.folder',
        parents: parentId ? [parentId] : undefined,
      };

      const response = await this.makeRequest('/files', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(metadata),
      });

      return {
        success: true,
        data: response.id,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to create folder: ${error.message}`,
      };
    }
  }

  async uploadFile(
    filename: string,
    content: Buffer,
    mimeType: string,
    folderId?: string
  ): Promise<ConnectorResult<DriveFile>> {
    try {
      // Create multipart request
      const boundary = 'boundary_' + Math.random().toString(36).substr(2);
      const metadata = {
        name: filename,
        parents: folderId ? [folderId] : undefined,
      };

      const preRequest = `--${boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n${JSON.stringify(metadata)}\r\n--${boundary}\r\nContent-Type: ${mimeType}\r\n\r\n`;
      const postRequest = `\r\n--${boundary}--`;

      const requestBody = Buffer.concat([
        Buffer.from(preRequest),
        content,
        Buffer.from(postRequest),
      ]);

      const response = await this.makeRequest('/files?uploadType=multipart', {
        method: 'POST',
        headers: {
          'Content-Type': `multipart/related; boundary=${boundary}`,
        },
        body: requestBody,
      });

      const file: DriveFile = {
        id: response.id,
        name: response.name,
        mimeType: response.mimeType,
        webViewLink: response.webViewLink,
        size: response.size,
        modifiedTime: response.modifiedTime,
        owners: response.owners || [],
        shared: response.shared || false,
      };

      return {
        success: true,
        data: file,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to upload file: ${error.message}`,
      };
    }
  }

  async shareFile(fileId: string, emailAddress: string, role: 'reader' | 'writer' | 'owner' = 'reader'): Promise<ConnectorResult<boolean>> {
    try {
      await this.makeRequest(`/files/${fileId}/permissions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'user',
          role,
          emailAddress,
        }),
      });

      return {
        success: true,
        data: true,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to share file: ${error.message}`,
      };
    }
  }

  async downloadFile(fileId: string): Promise<ConnectorResult<Buffer>> {
    try {
      const response = await fetch(`${this.baseUrl}/files/${fileId}?alt=media`, {
        headers: {
          'Authorization': `Bearer ${this.config.accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Download failed: ${response.status} ${response.statusText}`);
      }

      const buffer = Buffer.from(await response.arrayBuffer());

      return {
        success: true,
        data: buffer,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `Failed to download file: ${error.message}`,
      };
    }
  }

  getMetadata() {
    return {
      name: 'Google Drive',
      description: 'Google Drive API integration for file storage and collaboration',
      capabilities: [
        'upload_files',
        'download_files',
        'create_folders',
        'share_files',
        'list_files',
        'collaborative_editing',
      ],
      rateLimits: {
        requests: 1000, // per 100 seconds
        period: 100000,
      },
      costPerRequest: 0, // Included in Google Workspace
    };
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.config.accessToken}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: { message: response.statusText } }));
      throw new Error(`Google Drive API error: ${response.status} - ${error.error?.message || response.statusText}`);
    }

    return response.json();
  }
}

// Stub implementation
export class GoogleDriveConnectorStub extends BaseConnector {
  private mockFiles: Map<string, DriveFile> = new Map();

  constructor(config: ConnectorConfig) {
    super(config);

    // Initialize with mock data
    this.mockFiles.set('file_1', {
      id: 'file_1',
      name: 'Brand Assets',
      mimeType: 'application/vnd.google-apps.folder',
      webViewLink: 'https://drive.google.com/drive/folders/mock',
      modifiedTime: new Date().toISOString(),
      owners: [{ displayName: 'User', emailAddress: 'user@example.com' }],
      shared: false,
    });
  }

  async testConnection(): Promise<ConnectorResult<boolean>> {
    return {
      success: true,
      data: true,
    };
  }

  async listFiles(folderId?: string): Promise<ConnectorResult<DriveFile[]>> {
    const files = Array.from(this.mockFiles.values());

    console.log(`📁 [STUB] Listed ${files.length} Drive files`);

    return {
      success: true,
      data: files,
    };
  }

  async createFolder(name: string): Promise<ConnectorResult<string>> {
    const folderId = `folder_${Date.now()}`;

    console.log(`📁 [STUB] Created Drive folder: ${name}`);

    return {
      success: true,
      data: folderId,
    };
  }

  async uploadFile(filename: string, content: Buffer): Promise<ConnectorResult<DriveFile>> {
    const fileId = `file_${Date.now()}`;

    const mockFile: DriveFile = {
      id: fileId,
      name: filename,
      mimeType: 'application/octet-stream',
      webViewLink: `https://drive.google.com/file/d/${fileId}`,
      size: content.length.toString(),
      modifiedTime: new Date().toISOString(),
      owners: [{ displayName: 'User', emailAddress: 'user@example.com' }],
      shared: false,
    };

    this.mockFiles.set(fileId, mockFile);

    console.log(`📤 [STUB] Uploaded file to Drive: ${filename} (${content.length} bytes)`);

    return {
      success: true,
      data: mockFile,
    };
  }

  async shareFile(fileId: string, emailAddress: string): Promise<ConnectorResult<boolean>> {
    console.log(`🔗 [STUB] Shared Drive file ${fileId} with ${emailAddress}`);

    return {
      success: true,
      data: true,
    };
  }

  async downloadFile(fileId: string): Promise<ConnectorResult<Buffer>> {
    const mockContent = Buffer.from('Mock file content for testing');

    console.log(`📥 [STUB] Downloaded file from Drive: ${fileId}`);

    return {
      success: true,
      data: mockContent,
    };
  }

  getMetadata() {
    return {
      name: 'Google Drive (Stub)',
      description: 'Stub implementation for development and testing',
      capabilities: ['upload_files', 'download_files', 'create_folders', 'share_files'],
      rateLimits: {
        requests: 1000,
        period: 100000,
      },
    };
  }
}


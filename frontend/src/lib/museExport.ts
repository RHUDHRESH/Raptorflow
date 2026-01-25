import jsPDF from 'jspdf';
import { Asset } from '@/stores/museStore';

export type ExportFormat = 'markdown' | 'pdf' | 'html' | 'csv';

interface ExportOptions {
  includeMetadata?: boolean;
  includeTimestamp?: boolean;
  template?: string;
}

export async function exportAssets(assets: Asset[], format: ExportFormat, options: ExportOptions = {}): Promise<void> {
  switch (format) {
    case 'markdown':
      await exportMarkdown(assets, options);
      break;
    case 'pdf':
      await exportPDF(assets, options);
      break;
    case 'html':
      await exportHTML(assets, options);
      break;
    case 'csv':
      await exportCSV(assets, options);
      break;
    default:
      throw new Error(`Unsupported export format: ${format}`);
  }
}

async function exportMarkdown(assets: Asset[], options: ExportOptions): Promise<void> {
  let markdown = '';
  
  assets.forEach((asset, index) => {
    markdown += `# ${asset.title}\n\n`;
    
    if (options.includeMetadata) {
      markdown += `**Type:** ${asset.type}\n`;
      markdown += `**Tags:** ${asset.tags.join(', ')}\n`;
      markdown += `**Created:** ${new Date(asset.createdAt).toLocaleDateString()}\n\n`;
    }
    
    markdown += `${asset.content}\n\n`;
    
    if (index < assets.length - 1) {
      markdown += '---\n\n';
    }
  });
  
  downloadFile(markdown, 'muse-export.md', 'text/markdown');
}

async function exportPDF(assets: Asset[], options: ExportOptions): Promise<void> {
  const pdf = new jsPDF();
  let yPosition = 20;
  const pageHeight = pdf.internal.pageSize.height;
  const lineHeight = 7;
  
  assets.forEach((asset, index) => {
    // Title
    pdf.setFontSize(18);
    pdf.text(asset.title, 20, yPosition);
    yPosition += lineHeight * 2;
    
    // Metadata
    if (options.includeMetadata) {
      pdf.setFontSize(10);
      pdf.text(`Type: ${asset.type}`, 20, yPosition);
      yPosition += lineHeight;
      pdf.text(`Tags: ${asset.tags.join(', ')}`, 20, yPosition);
      yPosition += lineHeight;
      pdf.text(`Created: ${new Date(asset.createdAt).toLocaleDateString()}`, 20, yPosition);
      yPosition += lineHeight * 2;
    }
    
    // Content
    pdf.setFontSize(12);
    const lines = pdf.splitTextToSize(asset.content, 170);
    
    lines.forEach((line: string) => {
      if (yPosition > pageHeight - 20) {
        pdf.addPage();
        yPosition = 20;
      }
      pdf.text(line, 20, yPosition);
      yPosition += lineHeight;
    });
    
    // Add separator between assets
    if (index < assets.length - 1) {
      yPosition += lineHeight;
      if (yPosition > pageHeight - 40) {
        pdf.addPage();
        yPosition = 20;
      }
      pdf.line(20, yPosition, 190, yPosition);
      yPosition += lineHeight * 2;
    }
  });
  
  pdf.save('muse-export.pdf');
}

async function exportHTML(assets: Asset[], options: ExportOptions): Promise<void> {
  const html = generateHTML(assets, options);
  downloadFile(html, 'muse-export.html', 'text/html');
}

export function generateHTML(assets: Asset[], options: ExportOptions = {}): string {
  const timestamp = options.includeTimestamp ? new Date().toISOString() : '';
  
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Muse Export</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            line-height: 1.6;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .metadata {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            font-size: 14px;
        }
        .metadata span {
            margin-right: 20px;
        }
        .content {
            white-space: pre-wrap;
            margin: 20px 0;
        }
        .separator {
            border-top: 1px solid #e0e0e0;
            margin: 40px 0;
        }
        .timestamp {
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 40px;
        }
        @media print {
            body { margin: 0; }
            .no-print { display: none; }
        }
    </style>
</head>
<body>
    ${timestamp ? `<div class="timestamp">Exported on ${new Date(timestamp).toLocaleString()}</div>` : ''}
    
    ${assets.map((asset, index) => `
        <div class="asset">
            <h1>${asset.title}</h1>
            
            ${options.includeMetadata ? `
                <div class="metadata">
                    <span><strong>Type:</strong> ${asset.type}</span>
                    <span><strong>Tags:</strong> ${asset.tags.join(', ')}</span>
                    <span><strong>Created:</strong> ${new Date(asset.createdAt).toLocaleDateString()}</span>
                </div>
            ` : ''}
            
            <div class="content">${asset.content}</div>
            
            ${index < assets.length - 1 ? '<div class="separator"></div>' : ''}
        </div>
    `).join('')}
    
    <script>
        // Auto-print functionality
        if (window.location.search.includes('autoPrint=true')) {
            window.print();
        }
    </script>
</body>
</html>`;
}

async function exportCSV(assets: Asset[], options: ExportOptions): Promise<void> {
  const headers = ['Title', 'Type', 'Content', 'Tags', 'Created At'];
  if (options.includeMetadata) {
    headers.push('ID', 'Updated At');
  }
  
  const rows = assets.map(asset => {
    const row = [
      `"${asset.title.replace(/"/g, '""')}"`,
      asset.type,
      `"${asset.content.replace(/"/g, '""').replace(/\n/g, '\\n')}"`,
      `"${asset.tags.join('; ')}"`,
      new Date(asset.createdAt).toISOString()
    ];
    
    if (options.includeMetadata) {
      row.push(asset.id, new Date(asset.updatedAt).toISOString());
    }
    
    return row.join(',');
  });
  
  const csv = [headers.join(','), ...rows].join('\n');
  downloadFile(csv, 'muse-export.csv', 'text/csv');
}

function downloadFile(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// Additional utility functions
export async function copyToClipboard(text: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(text);
    showToast('Copied to clipboard!');
  } catch (err) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    showToast('Copied to clipboard!');
  }
}

export function openInNewTab(content: string, title: string = 'Muse Content'): void {
  const html = generateHTML([{ 
    id: 'temp',
    title,
    content,
    type: 'preview',
    tags: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }], { includeMetadata: true });
  
  const newWindow = window.open();
  if (newWindow) {
    newWindow.document.write(html);
    newWindow.document.close();
  }
}

export function sendToEmail(title: string, content: string): void {
  const subject = encodeURIComponent(title);
  const body = encodeURIComponent(content);
  window.location.href = `mailto:?subject=${subject}&body=${body}`;
}

// Toast notification helper
function showToast(message: string): void {
  // Create toast element
  const toast = document.createElement('div');
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #333;
    color: white;
    padding: 12px 20px;
    border-radius: 4px;
    z-index: 10000;
    animation: slideInUp 0.3s ease;
  `;
  
  // Add animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideInUp {
      from { transform: translateY(100%); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
  
  document.body.appendChild(toast);
  
  // Remove after 3 seconds
  setTimeout(() => {
    toast.style.animation = 'slideInUp 0.3s ease reverse';
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, 3000);
}
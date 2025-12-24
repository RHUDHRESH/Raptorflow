'use client';

/**
 * Muse Export Utilities
 * Handles PDF, DOCX, and text export/download functionality
 */

// Download text content as a file
export function downloadAsText(content: string, filename: string): void {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    triggerDownload(blob, `${filename}.txt`);
}

// Download content as Markdown
export function downloadAsMarkdown(content: string, filename: string): void {
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    triggerDownload(blob, `${filename}.md`);
}

// Download content as HTML (can be opened in Word)
export function downloadAsHtml(content: string, title: string, filename: string): void {
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>${title}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            line-height: 1.6;
            color: #333;
        }
        h1 { font-size: 2em; margin-bottom: 0.5em; }
        h2 { font-size: 1.5em; margin-top: 1.5em; }
        p { margin: 1em 0; }
        blockquote {
            border-left: 3px solid #ccc;
            margin: 1em 0;
            padding-left: 1em;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>${title}</h1>
    ${markdownToHtml(content)}
</body>
</html>
    `.trim();

    const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
    triggerDownload(blob, `${filename}.html`);
}

// Download as DOCX-compatible HTML (opens cleanly in Word)
export function downloadAsDocx(content: string, title: string, filename: string): void {
    // Word can open HTML files directly
    const htmlContent = `
<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word'>
<head>
    <meta charset="utf-8">
    <title>${title}</title>
    <!--[if gte mso 9]>
    <xml>
        <w:WordDocument>
            <w:View>Print</w:View>
            <w:Zoom>100</w:Zoom>
        </w:WordDocument>
    </xml>
    <![endif]-->
    <style>
        body { font-family: Calibri, Arial, sans-serif; font-size: 11pt; line-height: 1.6; }
        h1 { font-size: 18pt; }
        h2 { font-size: 14pt; }
    </style>
</head>
<body>
    <h1>${title}</h1>
    ${markdownToHtml(content)}
</body>
</html>
    `.trim();

    const blob = new Blob([htmlContent], { type: 'application/msword' });
    triggerDownload(blob, `${filename}.doc`);
}

// Simple markdown to HTML converter
function markdownToHtml(markdown: string): string {
    return markdown
        // Headers
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        // Bold and italic
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        // Blockquotes
        .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
        // Line breaks
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        // Wrap in paragraph
        .replace(/^/, '<p>')
        .replace(/$/, '</p>');
}

// Copy content to clipboard
export async function copyToClipboard(content: string): Promise<boolean> {
    try {
        await navigator.clipboard.writeText(content);
        return true;
    } catch {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = content;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        const success = document.execCommand('copy');
        document.body.removeChild(textarea);
        return success;
    }
}

// Share content via Web Share API (mobile/desktop)
export async function shareContent(title: string, content: string): Promise<boolean> {
    if (navigator.share) {
        try {
            await navigator.share({
                title,
                text: content,
            });
            return true;
        } catch (err) {
            // User cancelled or error
            return false;
        }
    }
    // Fallback: copy to clipboard
    return copyToClipboard(content);
}

// Trigger browser download
function triggerDownload(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Generate a clean filename from title
export function sanitizeFilename(title: string): string {
    return title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, '')
        .substring(0, 50) || 'untitled';
}

// Export options for UI
export const EXPORT_OPTIONS = [
    { id: 'txt', label: 'Plain Text', extension: '.txt', icon: 'FileText' },
    { id: 'md', label: 'Markdown', extension: '.md', icon: 'FileCode' },
    { id: 'doc', label: 'Word Document', extension: '.doc', icon: 'FileEdit' },
    { id: 'html', label: 'HTML', extension: '.html', icon: 'Globe' },
] as const;

export type ExportFormat = typeof EXPORT_OPTIONS[number]['id'];

// Main export function
export function exportContent(
    content: string,
    title: string,
    format: ExportFormat
): void {
    const filename = sanitizeFilename(title);

    switch (format) {
        case 'txt':
            downloadAsText(content, filename);
            break;
        case 'md':
            downloadAsMarkdown(content, filename);
            break;
        case 'doc':
            downloadAsDocx(content, title, filename);
            break;
        case 'html':
            downloadAsHtml(content, title, filename);
            break;
    }
}

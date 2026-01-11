import { MuseAsset } from "@/stores/museStore";
import { format } from "date-fns";

export type ExportFormat = 'markdown' | 'pdf' | 'html' | 'csv' | 'json';

interface ExportOptions {
    includeMetadata?: boolean;
    includeTimestamp?: boolean;
}

export const exportAssets = async (
    assets: MuseAsset[],
    formatName: ExportFormat,
    options: ExportOptions = {}
): Promise<void> => {
    let content = "";
    const filename = `muse-export-${format(new Date(), "yyyy-MM-dd-HHmm")}`;

    switch (formatName) {
        case 'markdown':
            content = assets.map(asset => {
                let entry = `# ${asset.title}\n\n`;
                if (options.includeMetadata) {
                    entry += `**Type:** ${asset.type}\n`;
                    if (options.includeTimestamp) {
                        entry += `**Date:** ${format(new Date(asset.createdAt), "PPpp")}\n`;
                    }
                    entry += `**Tags:** ${asset.tags.join(", ")}\n\n`;
                }
                entry += `${asset.content}\n\n---\n\n`;
                return entry;
            }).join("");
            downloadFile(content, `${filename}.md`, "text/markdown");
            break;

        case 'json':
            content = JSON.stringify(assets, null, 2);
            downloadFile(content, `${filename}.json`, "application/json");
            break;

        case 'csv':
            // Basic CSV implementation
            const headers = ["ID", "Title", "Type", "Created At", "Content"];
            const rows = assets.map(a => [
                a.id,
                `"${a.title.replace(/"/g, '""')}"`,
                a.type,
                a.createdAt,
                `"${a.content.replace(/"/g, '""')}"`
            ]);
            content = [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
            downloadFile(content, `${filename}.csv`, "text/csv");
            break;

        case 'html':
            content = `
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }
.asset { border: 1px solid #eee; padding: 2rem; margin-bottom: 2rem; border-radius: 8px; }
h1 { margin-top: 0; }
.meta { color: #666; font-size: 0.9em; margin-bottom: 1rem; }
</style>
</head>
<body>
${assets.map(asset => `
<div class="asset">
  <h1>${asset.title}</h1>
  ${options.includeMetadata ? `
  <div class="meta">
    <div>Type: ${asset.type}</div>
    ${options.includeTimestamp ? `<div>Date: ${new Date(asset.createdAt).toLocaleString()}</div>` : ''}
    <div>Tags: ${asset.tags.join(", ")}</div>
  </div>
  ` : ''}
  <div class="content">${asset.content.replace(/\n/g, '<br/>')}</div>
</div>
`).join('')}
</body>
</html>`;
            downloadFile(content, `${filename}.html`, "text/html");
            break;

        case 'pdf':
            // For PDF, strictly we might need a library like jspdf.
            // For now, we'll just trigger a print on an HTML version or alert not supported.
            console.warn("Direct PDF export requires additional libraries. Opening print view.");
            const printWindow = window.open('', '_blank');
            if (printWindow) {
                printWindow.document.write(`<html><body>${assets.map(a => `<h1>${a.title}</h1><pre>${a.content}</pre><hr/>`).join('')}</body></html>`);
                printWindow.document.close();
                printWindow.print();
            }
            break;
    }
};

const downloadFile = (content: string, filename: string, contentType: string) => {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
};

export const copyToClipboard = async (text: string): Promise<void> => {
    try {
        await navigator.clipboard.writeText(text);
    } catch (err) {
        console.error('Failed to copy text: ', err);
    }
};

export const openInNewTab = (content: string): void => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
};

export const sendToEmail = (subject: string, body: string): void => {
    window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
};

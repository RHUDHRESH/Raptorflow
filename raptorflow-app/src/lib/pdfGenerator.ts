'use client';

import { FoundationData } from '@/lib/foundation';


/**
 * Generate a PDF of the Foundation Blueprint
 * Uses browser print functionality for simplicity
 */
export async function generateFoundationPDF(data: FoundationData): Promise<void> {
    // Create a new window with formatted content
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
        alert('Please allow popups to download the PDF');
        return;
    }

    const businessName = data.business?.name || 'Your Business';
    const today = new Date().toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    const html = `
<!DOCTYPE html>
<html>
<head>
    <title>${businessName} — Foundation Blueprint</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #2D3538;
            line-height: 1.6;
            padding: 48px;
            max-width: 800px;
            margin: 0 auto;
        }
        .header {
            border-bottom: 2px solid #2D3538;
            padding-bottom: 24px;
            margin-bottom: 32px;
        }
        .logo {
            font-size: 12px;
            letter-spacing: 3px;
            color: #5B5F61;
            margin-bottom: 8px;
        }
        h1 {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 36px;
            font-weight: 400;
            margin-bottom: 8px;
        }
        .date { font-size: 14px; color: #5B5F61; }
        .section {
            margin-bottom: 32px;
            padding-bottom: 24px;
            border-bottom: 1px solid #C0C1BE;
        }
        .section:last-child { border-bottom: none; }
        .section-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #2D3538;
        }
        .field { margin-bottom: 12px; }
        .field-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #5B5F61;
            margin-bottom: 4px;
        }
        .field-value { font-size: 15px; }
        .positioning-statement {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 18px;
            font-style: italic;
            padding: 16px;
            background: #F3F4EE;
            border-radius: 8px;
            margin-bottom: 16px;
        }
        .footer {
            margin-top: 48px;
            padding-top: 24px;
            border-top: 1px solid #C0C1BE;
            font-size: 12px;
            color: #5B5F61;
            text-align: center;
        }
        @media print {
            body { padding: 24px; }
            .section { page-break-inside: avoid; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">RAPTORFLOW</div>
        <h1>${businessName}</h1>
        <div class="date">Foundation Blueprint — ${today}</div>
    </div>

    <div class="section">
        <div class="section-title">Business Basics</div>
        <div class="field">
            <div class="field-label">Business Name</div>
            <div class="field-value">${data.business?.name || '—'}</div>
        </div>
        <div class="field">
            <div class="field-label">Industry</div>
            <div class="field-value">${data.business?.industry || '—'}</div>
        </div>
        <div class="field">
            <div class="field-label">Stage</div>
            <div class="field-value">${data.business?.stage || '—'}</div>
        </div>
        <div class="field">
            <div class="field-label">Revenue Model</div>
            <div class="field-value">${Array.isArray(data.business?.revenueModel) ? data.business.revenueModel.join(', ') : data.business?.revenueModel || '—'}</div>
        </div>
        <div class="field">
            <div class="field-label">Team Size</div>
            <div class="field-value">${data.business?.teamSize || '—'}</div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">The Confession</div>
        <div class="field">
            <div class="field-label">Expensive Problem</div>
            <div class="field-value">${data.confession?.expensiveProblem || '—'}</div>
        </div>
        <div class="field">
            <div class="field-label">Embarrassing Truth</div>
            <div class="field-value">${data.confession?.embarrassingTruth || '—'}</div>
        </div>
        <div class="field">
            <div class="field-label">Stupid Idea</div>
            <div class="field-value">${data.confession?.stupidIdea || '—'}</div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Cohorts</div>
        <div class="field">
            <div class="field-label">Customer Type</div>
            <div class="field-value">${Array.isArray(data.cohorts?.customerType) ? data.cohorts.customerType.join(', ') : data.cohorts?.customerType || '—'}</div>
        </div>
        <div class="field">
            <div class="field-label">Buyer Role</div>
            <div class="field-value">${data.cohorts?.buyerRole || '—'}</div>
        </div>
        <div class="field">
            <div class="field-label">Primary Drivers (SCARF)</div>
            <div class="field-value">${data.cohorts?.primaryDrivers?.join(', ') || '—'}</div>
        </div>
        <div class="field">
            <div class="field-label">Decision Style</div>
            <div class="field-value">${data.cohorts?.decisionStyle || '—'}</div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Positioning</div>
        <div class="positioning-statement">
            We are the <strong>${data.positioning?.category || '_____'}</strong>
            for <strong>${data.positioning?.targetAudience || '_____'}</strong>
            who want <strong>${data.positioning?.psychologicalOutcome || '_____'}</strong>.
        </div>
        <div class="field">
            <div class="field-label">Owned Position</div>
            <div class="field-value">${data.positioning?.ownedPosition || '—'}</div>
        </div>
        <div class="field">
            <div class="field-label">Reframed Weakness</div>
            <div class="field-value">${data.positioning?.reframedWeakness || '—'}</div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Messaging Pillars</div>
        <div class="field">
            <div class="field-label">Primary Heuristic</div>
            <div class="field-value">${data.messaging?.primaryHeuristic || '—'}</div>
        </div>
        <div class="field">
            <div class="field-label">Belief Pillar</div>
            <div class="field-value">${data.messaging?.beliefPillar || '—'}</div>
        </div>
        <div class="field">
            <div class="field-label">Promise Pillar</div>
            <div class="field-value">${data.messaging?.promisePillar || '—'}</div>
        </div>
        <div class="field">
            <div class="field-label">Proof Pillar</div>
            <div class="field-value">${data.messaging?.proofPillar || '—'}</div>
        </div>
    </div>

    <div class="footer">
        Generated by RaptorFlow — Marketing. Finally under control.
    </div>

    <script>
        window.onload = function() {
            window.print();
        };
    </script>
</body>
</html>
    `;

    printWindow.document.write(html);
    printWindow.document.close();
}

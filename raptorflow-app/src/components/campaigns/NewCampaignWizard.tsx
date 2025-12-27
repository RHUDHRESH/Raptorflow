'use client';

import React from 'react';

interface NewCampaignWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onComplete: (campaign: any) => void;
}

export default function NewCampaignWizard({ open, onOpenChange, onComplete }: NewCampaignWizardProps) {
  if (!open) return null;

  return (
    <div>
      <h1>New Campaign Wizard</h1>
      <p>Wizard is open: {open ? 'Yes' : 'No'}</p>
      <button onClick={() => onOpenChange(false)}>Close</button>
    </div>
  );
}

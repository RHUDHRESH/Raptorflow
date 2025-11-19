'use client';

import React, { useState, useEffect } from 'react';
import { StrategicInput } from '../StrategicInput';
import { LocationPicker } from '../LocationPicker';
import { useGroundwork } from '../GroundworkProvider';
import { BusinessIdentityData } from '@/lib/groundwork/types';

export function BusinessIdentitySection() {
  const { state, updateSectionData } = useGroundwork();
  const sectionData = state.sections['business-identity'].data as BusinessIdentityData | null;

  const [productDescription, setProductDescription] = useState(
    sectionData?.productDescription || ''
  );
  const [whoPays, setWhoPays] = useState(sectionData?.whoPays || '');
  const [whoUses, setWhoUses] = useState(sectionData?.whoUses || '');
  const [location, setLocation] = useState(sectionData?.location);
  const [legalName, setLegalName] = useState(sectionData?.legalName || '');
  const [gstNumber, setGstNumber] = useState(sectionData?.gstNumber || '');
  const [businessUrl, setBusinessUrl] = useState(sectionData?.businessUrl || '');

  useEffect(() => {
    const data: BusinessIdentityData = {
      productDescription,
      whoPays,
      whoUses,
      location,
      legalName: legalName || undefined,
      gstNumber: gstNumber || undefined,
      businessUrl: businessUrl || undefined,
    };
    updateSectionData('business-identity', data);
  }, [productDescription, whoPays, whoUses, location, legalName, gstNumber, businessUrl, updateSectionData]);

  return (
    <div className="space-y-6">
      <StrategicInput
        value={productDescription}
        onChange={setProductDescription}
        placeholder="Describe your product or service in 1-2 sentences..."
        contextHint="Be specific about what you offer and who it helps."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-rf-ink mb-2">
            Who pays for your product?
          </label>
          <input
            type="text"
            value={whoPays}
            onChange={(e) => setWhoPays(e.target.value)}
            placeholder="e.g., Marketing managers, Startup founders"
            className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-rf-ink mb-2">
            Who actually uses it?
          </label>
          <input
            type="text"
            value={whoUses}
            onChange={(e) => setWhoUses(e.target.value)}
            placeholder="e.g., Marketing team members, End users"
            className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-rf-ink mb-2">
          Where is your business located?
        </label>
        <p className="text-xs text-rf-subtle mb-3">
          Pin your location on the map or search for your address
        </p>
        <LocationPicker
          value={location}
          onChange={setLocation}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-rf-ink mb-2">
            Legal business name <span className="text-rf-subtle font-normal">(optional)</span>
          </label>
          <input
            type="text"
            value={legalName}
            onChange={(e) => setLegalName(e.target.value)}
            placeholder="Your registered business name"
            className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-rf-ink mb-2">
            GST number <span className="text-rf-subtle font-normal">(optional)</span>
          </label>
          <input
            type="text"
            value={gstNumber}
            onChange={(e) => setGstNumber(e.target.value)}
            placeholder="Your GST registration number"
            className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-rf-ink mb-2">
          Business website URL <span className="text-rf-subtle font-normal">(optional)</span>
        </label>
        <input
          type="url"
          value={businessUrl}
          onChange={(e) => setBusinessUrl(e.target.value)}
          placeholder="https://yourwebsite.com"
          className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
        />
      </div>
    </div>
  );
}


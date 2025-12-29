'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  CheckCircle2,
  AlertTriangle,
  FileText,
  Video,
  Briefcase,
  Users,
  Shield,
  Wallet,
  Scale,
  HelpCircle,
} from 'lucide-react';
import {
  BuyingJobTypeExtended,
  BuyingRole,
  BuyingJobsCoverageCell,
} from '@/lib/foundation';

interface BuyingJobsCoverageProps {
  roles: BuyingRole[];
  cells: BuyingJobsCoverageCell[];
  gaps: string[];
  onUpdateCell: (cell: BuyingJobsCoverageCell) => void;
  onFlagGap: (jobRole: string) => void;
}

const BUYING_JOBS: Array<{
  id: BuyingJobTypeExtended;
  label: string;
  description: string;
}> = [
  {
    id: 'problem-id',
    label: 'Problem ID',
    description: 'Recognize they have a problem worth solving',
  },
  {
    id: 'solution-explore',
    label: 'Solution Explore',
    description: 'Research what solutions exist',
  },
  {
    id: 'requirements',
    label: 'Requirements',
    description: 'Define what they need in a solution',
  },
  {
    id: 'supplier-select',
    label: 'Supplier Select',
    description: 'Choose which vendor to work with',
  },
  {
    id: 'validation',
    label: 'Validation',
    description: 'Confirm the solution works as expected',
  },
  {
    id: 'consensus',
    label: 'Consensus',
    description: 'Get buy-in from all stakeholders',
  },
];

const ROLE_ICONS: Record<string, React.ElementType> = {
  'Economic Buyer': Wallet,
  Champion: Users,
  Technical: Shield,
  'End User': Briefcase,
  Finance: Scale,
  Legal: Scale,
  default: Users,
};

function getAssetSuggestion(
  job: BuyingJobTypeExtended,
  roleType: string
): string {
  const suggestions: Record<string, Record<string, string>> = {
    'problem-id': {
      Economic: 'ROI calculator',
      Champion: 'Industry report',
      default: 'Problem awareness content',
    },
    'solution-explore': {
      Economic: 'Comparison guide',
      Champion: 'Feature demo',
      default: 'Solution overview',
    },
    requirements: {
      Economic: 'Requirements checklist',
      Champion: 'Implementation guide',
      default: 'Spec sheet',
    },
    'supplier-select': {
      Economic: 'Case studies',
      Champion: 'Reference calls',
      default: 'Customer testimonials',
    },
    validation: {
      Economic: 'Pilot program',
      Champion: 'Proof of concept',
      default: 'Trial / Demo',
    },
    consensus: {
      Economic: 'Executive summary',
      Champion: 'Team presentation',
      default: 'FAQ document',
    },
  };

  const jobSuggestions = suggestions[job] || suggestions['solution-explore'];
  return jobSuggestions[roleType] || jobSuggestions['default'] || 'Asset TBD';
}

function CoverageCell({
  job,
  role,
  cell,
  onUpdate,
  onFlagGap,
}: {
  job: BuyingJobTypeExtended;
  role: BuyingRole;
  cell?: BuyingJobsCoverageCell;
  onUpdate: (cell: BuyingJobsCoverageCell) => void;
  onFlagGap: () => void;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [belief, setBelief] = useState(cell?.beliefRequired || '');

  const hasGap = cell?.hasGap;
  const asset =
    cell?.assetSuggested || getAssetSuggestion(job, role.role.split(' ')[0]);

  return (
    <td className="border border-[#E5E6E3] p-0">
      <div
        className={`p-3 h-full min-h-[120px] cursor-pointer hover:bg-[#F3F4EE] transition-colors ${
          hasGap ? 'bg-red-50' : ''
        }`}
        onClick={() => setIsEditing(true)}
      >
        {isEditing ? (
          <div className="space-y-2" onClick={(e) => e.stopPropagation()}>
            <textarea
              value={belief}
              onChange={(e) => setBelief(e.target.value)}
              placeholder="What must they believe?"
              className="w-full h-16 text-xs border border-[#E5E6E3] rounded-lg px-2 py-1 resize-none focus:outline-none focus:border-[#2D3538]"
              autoFocus
              onBlur={() => {
                onUpdate({
                  buyingJob: job,
                  roleId: role.id,
                  beliefRequired: belief,
                  assetSuggested: asset,
                  hasGap: false,
                  coverage: cell?.coverage || 0,
                });
                setIsEditing(false);
              }}
            />
          </div>
        ) : (
          <div className="space-y-2">
            {/* Belief */}
            <div>
              <span className="text-[8px] font-mono uppercase text-[#9D9F9F]">
                Belief
              </span>
              <p className="text-[10px] text-[#2D3538] line-clamp-2">
                {cell?.beliefRequired || (
                  <span className="italic text-[#9D9F9F]">Click to add</span>
                )}
              </p>
            </div>

            {/* Asset */}
            <div>
              <span className="text-[8px] font-mono uppercase text-[#9D9F9F]">
                Asset
              </span>
              <p className="text-[10px] text-[#5B5F61] flex items-center gap-1">
                <FileText className="w-3 h-3" />
                {asset}
              </p>
            </div>

            {/* Gap Flag */}
            {hasGap && (
              <div className="flex items-center gap-1 text-red-600">
                <AlertTriangle className="w-3 h-3" />
                <span className="text-[9px]">Gap</span>
              </div>
            )}
          </div>
        )}
      </div>
    </td>
  );
}

export function BuyingJobsCoverage({
  roles,
  cells,
  gaps,
  onUpdateCell,
  onFlagGap,
}: BuyingJobsCoverageProps) {
  const activeRoles = roles.filter((r) => r.isActive);

  const getCell = (job: BuyingJobTypeExtended, roleId: string) => {
    return cells.find((c) => c.buyingJob === job && c.roleId === roleId);
  };

  return (
    <div className="space-y-6">
      {/* Intro */}
      <div className="flex items-start gap-3 p-4 bg-[#F3F4EE] rounded-xl">
        <HelpCircle className="w-5 h-5 text-[#2D3538] flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm text-[#5B5F61]">
            <strong className="text-[#2D3538]">Buying Jobs Coverage</strong> —
            Map what each role must believe at each stage of the buying process,
            and what asset resolves it.
          </p>
          <p className="text-xs text-[#9D9F9F] mt-1">
            Based on Gartner's B2B Buying Jobs framework. Click cells to edit.
          </p>
        </div>
      </div>

      {/* Coverage Grid */}
      <div className="bg-white border border-[#E5E6E3] rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-[#FAFAF8]">
                <th className="border border-[#E5E6E3] p-3 text-left w-40">
                  <span className="text-[10px] font-mono uppercase tracking-[0.1em] text-[#9D9F9F]">
                    Buying Job
                  </span>
                </th>
                {activeRoles.map((role) => {
                  const RoleIcon =
                    ROLE_ICONS[role.role.split(' (')[0]] || ROLE_ICONS.default;
                  return (
                    <th
                      key={role.id}
                      className="border border-[#E5E6E3] p-3 text-center"
                    >
                      <div className="flex flex-col items-center gap-1">
                        <RoleIcon className="w-4 h-4 text-[#9D9F9F]" />
                        <span className="text-[10px] font-medium text-[#2D3538]">
                          {role.role.split(' (')[0]}
                        </span>
                        <span
                          className={`text-[8px] font-mono uppercase px-1.5 py-0.5 rounded ${
                            role.influence === 'high'
                              ? 'bg-[#2D3538] text-white'
                              : role.influence === 'medium'
                                ? 'bg-[#9D9F9F] text-white'
                                : 'bg-[#E5E6E3] text-[#5B5F61]'
                          }`}
                        >
                          {role.influence}
                        </span>
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {BUYING_JOBS.map((job) => (
                <tr key={job.id}>
                  <td className="border border-[#E5E6E3] p-3 bg-[#FAFAF8]">
                    <div>
                      <span className="text-xs font-medium text-[#2D3538]">
                        {job.label}
                      </span>
                      <p className="text-[10px] text-[#9D9F9F] mt-0.5">
                        {job.description}
                      </p>
                    </div>
                  </td>
                  {activeRoles.map((role) => (
                    <CoverageCell
                      key={`${job.id}-${role.id}`}
                      job={job.id}
                      role={role}
                      cell={getCell(job.id, role.id)}
                      onUpdate={onUpdateCell}
                      onFlagGap={() => onFlagGap(`${job.id}:${role.id}`)}
                    />
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Gaps Summary */}
      {gaps.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-50 border border-red-200 rounded-2xl p-5"
        >
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <h4 className="font-medium text-red-800">
              {gaps.length} Gap{gaps.length > 1 ? 's' : ''} Identified
            </h4>
          </div>
          <p className="text-sm text-red-700">
            These gaps will be addressed in Phase 6 (Soundbite Forge) where
            we'll create the missing assets and messaging.
          </p>
        </motion.div>
      )}
    </div>
  );
}

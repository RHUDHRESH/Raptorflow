"use client";

import { useState, useMemo } from 'react';
import { Search, Filter, Copy, ExternalLink, Mail, Trash2, Calendar, MoreVertical, FileText, Linkedin, Mail as MailIcon, Globe, MessageSquare, Twitter, Hash, Edit3 } from 'lucide-react';
import { useMuseStore, MuseAsset } from '@/stores/museStore';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { BlueprintInput } from '@/components/ui/BlueprintInput';
import { BlueprintSelect } from '@/components/ui/BlueprintSelect';
import { ScheduleContentModal } from './ScheduleContentModal';
import { copyToClipboard, openInNewTab, sendToEmail } from '@/lib/museExport';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

export function MuseLibrary() {
  const { assets, deleteAsset } = useMuseStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [selectedAsset, setSelectedAsset] = useState<MuseAsset | null>(null);
  const [showScheduleModal, setShowScheduleModal] = useState(false);

  const filteredAssets = useMemo(() => {
    return assets.filter(asset => {
      const matchesSearch = asset.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           asset.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           asset.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      const matchesType = typeFilter === 'all' || asset.type === typeFilter;
      return matchesSearch && matchesType;
    });
  }, [assets, searchQuery, typeFilter]);

  const getIconForType = (type: string) => {
    switch (type) {
      case 'Email': return <MailIcon size={16} />;
      case 'LinkedIn': return <Linkedin size={16} />;
      case 'Blog': return <Globe size={16} />;
      case 'Tweet': return <Twitter size={16} />;
      case 'Social': return <Hash size={16} />;
      case 'Script': return <FileText size={16} />;
      default: return <FileText size={16} />;
    }
  };

  const handleCopy = (content: string) => {
    copyToClipboard(content);
    // Would ideally show a toast here
  };

  const handleSchedule = (asset: MuseAsset) => {
    setSelectedAsset(asset);
    setShowScheduleModal(true);
  };

  const onScheduleConfirm = (asset: MuseAsset, date: Date) => {
    console.log(`Scheduled ${asset.title} for ${date}`);
    // Update asset with scheduled status in real app
  };

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4 items-end">
        <div className="flex-1 w-full">
          <BlueprintInput
            label="Search Assets"
            code="LIB-SRC"
            placeholder="Search by title, content, or tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            startIcon={<Search size={16} />}
          />
        </div>
        <div className="w-full md:w-48">
          <BlueprintSelect
            label="Content Type"
            code="LIB-TYP"
            value={typeFilter}
            onChange={setTypeFilter}
            options={[
              { value: 'all', label: 'All Types' },
              { value: 'Email', label: 'Emails' },
              { value: 'LinkedIn', label: 'LinkedIn' },
              { value: 'Blog', label: 'Blog Posts' },
              { value: 'Tweet', label: 'Tweets' },
              { value: 'Social', label: 'Social' },
              { value: 'Script', label: 'Scripts' },
            ]}
          />
        </div>
      </div>

      {/* Assets Grid */}
      {filteredAssets.length === 0 ? (
        <div className="text-center py-20 bg-[var(--surface)] border border-dashed border-[var(--structure-subtle)] rounded-xl">
          <FileText className="w-12 h-12 text-[var(--ink-ghost)] mx-auto mb-4" />
          <h3 className="text-lg font-medium text-[var(--ink-muted)]">No assets found</h3>
          <p className="text-sm text-[var(--ink-ghost)] mt-1">Try adjusting your search or filters</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredAssets.map((asset) => (
            <BlueprintCard key={asset.id} className="group hover:border-[var(--blueprint)] transition-all">
              <div className="flex flex-col h-full">
                {/* Card Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-[var(--surface)] border border-[var(--structure-subtle)] rounded-lg flex items-center justify-center text-[var(--blueprint)]">
                      {getIconForType(asset.type)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-[var(--ink)] leading-none">{asset.title}</h3>
                      <p className="text-xs text-[var(--ink-ghost)] mt-1.5 font-technical uppercase">
                        {asset.type} • {format(new Date(asset.createdAt), 'MMM d, yyyy')}
                      </p>
                    </div>
                  </div>
                  <BlueprintBadge variant="default" size="xs">{asset.source || 'Muse'}</BlueprintBadge>
                </div>

                {/* Content Preview */}
                <div className="flex-1 bg-[var(--surface-hover)] p-4 rounded-lg border border-[var(--structure-subtle)] mb-4">
                  <p className="text-sm text-[var(--ink-muted)] line-clamp-4 whitespace-pre-wrap italic">
                    "{asset.content.slice(0, 250)}..."
                  </p>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-1.5 mb-6">
                  {asset.tags.map(tag => (
                    <span key={tag} className="text-[10px] px-2 py-0.5 bg-[var(--paper)] border border-[var(--structure-subtle)] text-[var(--ink-muted)] rounded uppercase tracking-wider font-technical">
                      {tag}
                    </span>
                  ))}
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between pt-4 border-t border-[var(--structure-subtle)]">
                  <div className="flex items-center gap-1">
                    <BlueprintButton
                      variant="ghost"
                      size="icon"
                      onClick={() => handleCopy(asset.content)}
                      title="Copy to Clipboard"
                    >
                      <Copy size={14} />
                    </BlueprintButton>
                    <BlueprintButton
                      variant="ghost"
                      size="icon"
                      onClick={() => openInNewTab(asset.content)}
                      title="Preview in New Tab"
                    >
                      <ExternalLink size={14} />
                    </BlueprintButton>
                    <BlueprintButton
                      variant="ghost"
                      size="icon"
                      onClick={() => sendToEmail(asset.title, asset.content)}
                      title="Send via Email"
                    >
                      <Mail size={14} />
                    </BlueprintButton>
                    <BlueprintButton
                      variant="ghost"
                      size="icon"
                      onClick={() => handleSchedule(asset)}
                      title="Schedule Content"
                    >
                      <Calendar size={14} />
                    </BlueprintButton>
                  </div>
                  <BlueprintButton
                    variant="ghost"
                    size="icon"
                    className="text-[var(--error)] hover:bg-[var(--error)]/10"
                    onClick={() => deleteAsset(asset.id)}
                    title="Delete Asset"
                  >
                    <Trash2 size={14} />
                  </BlueprintButton>
                </div>
              </div>
            </BlueprintCard>
          ))}
        </div>
      )}

      {/* Modals */}
      {showScheduleModal && selectedAsset && (
        <ScheduleContentModal
          asset={selectedAsset}
          onClose={() => setShowScheduleModal(false)}
          onSchedule={onScheduleConfirm}
        />
      )}
    </div>
  );
}

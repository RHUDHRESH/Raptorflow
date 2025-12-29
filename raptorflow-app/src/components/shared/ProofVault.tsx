'use client';

import React, { useState } from 'react';
import {
  Shield,
  MessageSquare,
  BarChart3,
  Users,
  Image,
  FileText,
  Plus,
  Search,
  Filter,
  Star,
  Clock,
  Tag,
  X,
  Edit,
  Trash2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';
import { ProofItem } from '@/lib/foundation';

interface ProofVaultProps {
  items: ProofItem[];
  onAddItem: (item: Omit<ProofItem, 'id'>) => void;
  onUpdateItem: (id: string, item: Partial<ProofItem>) => void;
  onDeleteItem: (id: string) => void;
  currentPhase?: number;
}

const proofTypes = [
  {
    value: 'testimonial',
    label: 'Testimonial',
    icon: MessageSquare,
    color: 'bg-blue-100 text-blue-700',
  },
  {
    value: 'case_study',
    label: 'Case Study',
    icon: FileText,
    color: 'bg-green-100 text-green-700',
  },
  {
    value: 'metric',
    label: 'Metric/Number',
    icon: BarChart3,
    color: 'bg-purple-100 text-purple-700',
  },
  {
    value: 'logo',
    label: 'Client Logo',
    icon: Users,
    color: 'bg-orange-100 text-orange-700',
  },
  {
    value: 'screenshot',
    label: 'Screenshot',
    icon: Image,
    color: 'bg-pink-100 text-pink-700',
  },
  {
    value: 'document',
    label: 'Document',
    icon: FileText,
    color: 'bg-gray-100 text-gray-700',
  },
];

function ProofCard({
  item,
  onEdit,
  onDelete,
  currentPhase,
}: {
  item: ProofItem;
  onEdit: (item: ProofItem) => void;
  onDelete: (id: string) => void;
  currentPhase?: number;
}) {
  const typeConfig = proofTypes.find((t) => t.value === item.type);
  const Icon = typeConfig?.icon || Shield;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={cn('p-2 rounded-lg', typeConfig?.color)}>
            <Icon className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-medium text-gray-900">{item.title}</h4>
            {item.source && (
              <p className="text-sm text-gray-500">Source: {item.source}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1">
          {item.verified && (
            <Badge variant="secondary" className="text-xs">
              <Shield className="w-3 h-3 mr-1" />
              Verified
            </Badge>
          )}
          <Button size="sm" variant="ghost" onClick={() => onEdit(item)}>
            <Edit className="w-3 h-3" />
          </Button>
          <Button size="sm" variant="ghost" onClick={() => onDelete(item.id)}>
            <Trash2 className="w-3 h-3" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <p className="text-sm text-gray-600 mb-3 line-clamp-3">{item.content}</p>

      {/* Tags */}
      {item.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {item.tags.map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              <Tag className="w-2 h-2 mr-1" />
              {tag}
            </Badge>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-2">
          {item.date && (
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {item.date}
            </span>
          )}
          {item.rating && (
            <span className="flex items-center gap-1">
              <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
              {item.rating}
            </span>
          )}
        </div>
        {item.linkedPhases && item.linkedPhases.length > 0 && (
          <div className="flex gap-1">
            {item.linkedPhases.map((phase) => (
              <Badge
                key={phase}
                variant={phase === currentPhase ? 'default' : 'outline'}
                className="text-xs"
              >
                Phase {phase}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function AddProofDialog({
  onAdd,
  currentPhase,
  trigger,
}: {
  onAdd: (item: Omit<ProofItem, 'id'>) => void;
  currentPhase?: number;
  trigger: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    type: 'testimonial' as ProofItem['type'],
    title: '',
    content: '',
    source: '',
    tags: '',
    rating: 5,
    verified: false,
  });

  const handleSubmit = () => {
    if (!formData.title || !formData.content) return;

    onAdd({
      ...formData,
      tags: formData.tags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean),
      linkedPhases: currentPhase ? [currentPhase] : [],
      date: new Date().toLocaleDateString(),
    });

    setFormData({
      type: 'testimonial',
      title: '',
      content: '',
      source: '',
      tags: '',
      rating: 5,
      verified: false,
    });
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Add Evidence to Proof Vault</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Type Selection */}
          <div>
            <label className="text-sm font-medium">Evidence Type</label>
            <Select
              value={formData.type}
              onValueChange={(value: ProofItem['type']) =>
                setFormData((prev) => ({ ...prev, type: value }))
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {proofTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    <div className="flex items-center gap-2">
                      <type.icon className="w-4 h-4" />
                      {type.label}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Title */}
          <div>
            <label className="text-sm font-medium">Title</label>
            <Input
              value={formData.title}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, title: e.target.value }))
              }
              placeholder="e.g., Customer Success Story - Q3 2024"
            />
          </div>

          {/* Content */}
          <div>
            <label className="text-sm font-medium">Content</label>
            <Textarea
              value={formData.content}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, content: e.target.value }))
              }
              placeholder="Detailed evidence content..."
              rows={4}
            />
          </div>

          {/* Source */}
          <div>
            <label className="text-sm font-medium">Source (Optional)</label>
            <Input
              value={formData.source}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, source: e.target.value }))
              }
              placeholder="e.g., Customer Name, Publication, Internal Report"
            />
          </div>

          {/* Tags */}
          <div>
            <label className="text-sm font-medium">
              Tags (comma-separated)
            </label>
            <Input
              value={formData.tags}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, tags: e.target.value }))
              }
              placeholder="e.g., revenue, retention, enterprise"
            />
          </div>

          {/* Rating and Verification */}
          <div className="flex gap-4">
            <div>
              <label className="text-sm font-medium">Rating</label>
              <Select
                value={formData.rating.toString()}
                onValueChange={(value) =>
                  setFormData((prev) => ({ ...prev, rating: parseInt(value) }))
                }
              >
                <SelectTrigger className="w-20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <SelectItem key={rating} value={rating.toString()}>
                      <div className="flex items-center gap-1">
                        <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                        {rating}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="verified"
                checked={formData.verified}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    verified: e.target.checked,
                  }))
                }
                className="rounded"
              />
              <label htmlFor="verified" className="text-sm font-medium">
                Verified Evidence
              </label>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={!formData.title || !formData.content}
            >
              Add to Vault
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export function ProofVault({
  items,
  onAddItem,
  onUpdateItem,
  onDeleteItem,
  currentPhase,
}: ProofVaultProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [editingItem, setEditingItem] = useState<ProofItem | null>(null);

  const filteredItems = items.filter((item) => {
    const matchesSearch =
      item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.tags.some((tag) =>
        tag.toLowerCase().includes(searchTerm.toLowerCase())
      );

    const matchesType = filterType === 'all' || item.type === filterType;

    return matchesSearch && matchesType;
  });

  const handleEdit = (item: ProofItem) => {
    setEditingItem(item);
  };

  const handleUpdate = (updatedItem: ProofItem) => {
    if (editingItem) {
      onUpdateItem(editingItem.id, updatedItem);
      setEditingItem(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            Evidence & Proof Vault
          </h2>
          <p className="text-sm text-gray-600">
            Centralized repository for all evidence and proof points
          </p>
        </div>

        <AddProofDialog
          onAdd={onAddItem}
          currentPhase={currentPhase}
          trigger={
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Evidence
            </Button>
          }
        />
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Search evidence..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-48">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {proofTypes.map((type) => (
              <SelectItem key={type.value} value={type.value}>
                <div className="flex items-center gap-2">
                  <type.icon className="w-4 h-4" />
                  {type.label}
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {proofTypes.map((type) => {
          const count = items.filter((item) => item.type === type.value).length;
          return (
            <div key={type.value} className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <div className={cn('p-2 rounded', type.color)}>
                  <type.icon className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{count}</p>
                  <p className="text-xs text-gray-600">{type.label}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Items Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredItems.map((item) => (
          <ProofCard
            key={item.id}
            item={item}
            onEdit={handleEdit}
            onDelete={onDeleteItem}
            currentPhase={currentPhase}
          />
        ))}
      </div>

      {filteredItems.length === 0 && (
        <div className="text-center py-12">
          <Shield className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No evidence found
          </h3>
          <p className="text-gray-600 mb-4">
            {searchTerm || filterType !== 'all'
              ? 'Try adjusting your search or filters'
              : 'Start building your proof vault by adding your first evidence'}
          </p>
          <AddProofDialog
            onAdd={onAddItem}
            currentPhase={currentPhase}
            trigger={
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Add Your First Evidence
              </Button>
            }
          />
        </div>
      )}

      {/* Edit Dialog */}
      {editingItem && (
        <Dialog open={!!editingItem} onOpenChange={() => setEditingItem(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Edit Evidence</DialogTitle>
            </DialogHeader>

            <div className="space-y-4">
              {/* Similar form fields as AddProofDialog but pre-filled */}
              <div>
                <label className="text-sm font-medium">Title</label>
                <Input
                  value={editingItem.title}
                  onChange={(e) =>
                    setEditingItem((prev) =>
                      prev ? { ...prev, title: e.target.value } : null
                    )
                  }
                />
              </div>

              <div>
                <label className="text-sm font-medium">Content</label>
                <Textarea
                  value={editingItem.content}
                  onChange={(e) =>
                    setEditingItem((prev) =>
                      prev ? { ...prev, content: e.target.value } : null
                    )
                  }
                  rows={4}
                />
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setEditingItem(null)}>
                  Cancel
                </Button>
                <Button
                  onClick={() => editingItem && handleUpdate(editingItem)}
                >
                  Save Changes
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}

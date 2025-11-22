/**
 * Asset Factory - Content and Creative Asset Management
 * Track and manage all marketing assets linked to moves and ICPs
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  FileText, Image, Video, Mail, Search, Filter, Plus, Eye, Edit2, Trash2, Download
} from 'lucide-react';
import { assetService, Asset } from '../lib/services/asset-service';

// Helper to get workspace ID (replace with actual implementation)
const getWorkspaceId = () => 'YOUR_WORKSPACE_ID';

export default function AssetFactory() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [statusCounts, setStatusCounts] = useState<Record<string, number>>({});

  // Load assets
  useEffect(() => {
    const loadAssets = async () => {
      try {
        setLoading(true);
        const [assetsData, counts] = await Promise.all([
          assetService.getAll(),
          assetService.getStatusCounts(),
        ]);
        setAssets(assetsData);
        setStatusCounts(counts);
      } catch (error) {
        console.error('Error loading assets:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAssets();
  }, []);

  // Filter assets
  const filteredAssets = assets.filter(asset => {
    const matchesSearch = !searchQuery || 
      asset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (asset.description || '').toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesType = selectedType === 'all' || asset.type === selectedType;
    const matchesStatus = selectedStatus === 'all' || asset.status === selectedStatus;
    
    return matchesSearch && matchesType && matchesStatus;
  });

  const getTypeIcon = (type: string) => {
    const icons: Record<string, any> = {
      'case_study': FileText,
      'whitepaper': FileText,
      'blog_post': FileText,
      'video': Video,
      'email': Mail,
      'social_post': Image,
      'landing_page': FileText,
      'creative': Image,
      'template': FileText,
      'other': FileText,
    };
    const Icon = icons[type] || FileText;
    return <Icon className="w-5 h-5" />;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'draft': 'bg-neutral-100 text-neutral-900 border-neutral-200',
      'review': 'bg-amber-100 text-amber-900 border-amber-200',
      'approved': 'bg-green-100 text-green-900 border-green-200',
      'published': 'bg-blue-100 text-blue-900 border-blue-200',
      'archived': 'bg-neutral-200 text-neutral-600 border-neutral-300',
    };
    return colors[status] || colors.draft;
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this asset?')) return;
    
    try {
      await assetService.delete(id);
      setAssets(prev => prev.filter(a => a.id !== id));
    } catch (error) {
      console.error('Error deleting asset:', error);
      alert('Failed to delete asset');
    }
  };

  const handleStatusChange = async (id: string, newStatus: Asset['status']) => {
    try {
      const updated = await assetService.updateStatus(id, newStatus);
      setAssets(prev => prev.map(a => a.id === id ? updated : a));
      
      // Update counts
      const counts = await assetService.getStatusCounts();
      setStatusCounts(counts);
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Failed to update status');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-neutral-200 border-t-neutral-900 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-neutral-600">Loading assets...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card relative overflow-hidden p-10"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white via-neutral-50 to-white" />
        <div className="relative z-10">
          <p className="micro-label mb-2">Asset Factory</p>
          <h1 className="font-serif text-4xl md:text-6xl text-black leading-tight mb-3">
            Content Arsenal
          </h1>
          <p className="text-base text-neutral-600 max-w-2xl">
            Manage all marketing assets, creative content, and collateral. Track production status and link to moves.
          </p>
        </div>
      </motion.div>

      {/* Status Overview */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {Object.entries(statusCounts).map(([status, count]) => (
          <div key={status} className="runway-card p-4">
            <div className="text-2xl font-bold text-neutral-900 mb-1">{count}</div>
            <div className="text-sm text-neutral-600 capitalize">{status}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="runway-card p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
            <input
              type="text"
              placeholder="Search assets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900"
            />
          </div>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900"
          >
            <option value="all">All Types</option>
            <option value="case_study">Case Study</option>
            <option value="whitepaper">Whitepaper</option>
            <option value="blog_post">Blog Post</option>
            <option value="video">Video</option>
            <option value="email">Email</option>
            <option value="social_post">Social Post</option>
            <option value="landing_page">Landing Page</option>
            <option value="creative">Creative</option>
          </select>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900"
          >
            <option value="all">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="review">Review</option>
            <option value="approved">Approved</option>
            <option value="published">Published</option>
            <option value="archived">Archived</option>
          </select>
          <button className="px-6 py-3 bg-neutral-900 text-white rounded-xl hover:bg-neutral-800 flex items-center gap-2">
            <Plus className="w-5 h-5" />
            New Asset
          </button>
        </div>
      </div>

      {/* Assets Grid */}
      {filteredAssets.length === 0 ? (
        <div className="runway-card p-12 text-center">
          <FileText className="w-16 h-16 text-neutral-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-neutral-900 mb-2">No Assets Found</h3>
          <p className="text-neutral-600 mb-6">
            {searchQuery || selectedType !== 'all' || selectedStatus !== 'all'
              ? 'Try adjusting your filters'
              : 'Create your first asset to get started'}
          </p>
          <button className="px-6 py-3 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800">
            Create Asset
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAssets.map(asset => (
            <motion.div
              key={asset.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="runway-card p-6 hover:shadow-xl transition-all group"
            >
              {/* Thumbnail or Icon */}
              <div className="mb-4 aspect-video bg-neutral-100 rounded-lg flex items-center justify-center overflow-hidden">
                {asset.thumbnail_url ? (
                  <img src={asset.thumbnail_url} alt={asset.name} className="w-full h-full object-cover" />
                ) : (
                  <div className="text-neutral-400">
                    {getTypeIcon(asset.type)}
                  </div>
                )}
              </div>

              {/* Asset Info */}
              <div className="mb-4">
                <h3 className="text-lg font-bold text-neutral-900 mb-2 line-clamp-2">
                  {asset.name}
                </h3>
                <p className="text-sm text-neutral-600 line-clamp-2 mb-3">
                  {asset.description || 'No description'}
                </p>
                <div className="flex flex-wrap gap-2">
                  <span className="px-2 py-1 text-[10px] font-mono uppercase tracking-wider bg-neutral-100 text-neutral-700 border border-neutral-200 rounded">
                    {asset.type.replace('_', ' ')}
                  </span>
                  <span className={`px-2 py-1 text-[10px] font-mono uppercase tracking-wider border rounded ${getStatusColor(asset.status)}`}>
                    {asset.status}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t border-neutral-200">
                {asset.url && (
                  <a
                    href={asset.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                    View
                  </a>
                )}
                <button className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors">
                  <Edit2 className="w-4 h-4" />
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(asset.id)}
                  className="flex items-center justify-center px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              {/* Status Actions */}
              {asset.status === 'draft' && (
                <button
                  onClick={() => handleStatusChange(asset.id, 'review')}
                  className="w-full mt-2 px-3 py-2 text-sm font-medium bg-amber-600 text-white rounded-lg hover:bg-amber-700"
                >
                  Submit for Review
                </button>
              )}
              {asset.status === 'review' && (
                <button
                  onClick={() => handleStatusChange(asset.id, 'approved')}
                  className="w-full mt-2 px-3 py-2 text-sm font-medium bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Approve
                </button>
              )}
              {asset.status === 'approved' && (
                <button
                  onClick={() => handleStatusChange(asset.id, 'published')}
                  className="w-full mt-2 px-3 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Publish
                </button>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}




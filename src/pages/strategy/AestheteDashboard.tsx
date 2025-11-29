// frontend/pages/strategy/AestheteDashboard.tsx
// Brand & Quality Dashboard

import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, Star, CheckCircle2, TrendingUp, Zap } from 'lucide-react';
import aestheteApi, { AssessQualityRequest, CheckBrandComplianceRequest, EvaluateVisualConsistencyRequest, ProvideFeedbackRequest } from '../../api/aesthete';
import useAestheteSocket from '../../hooks/useAestheteSocket';

interface MetricCard {
  title: string;
  value: string | number;
  description: string;
  icon: React.ReactNode;
  color: string;
}

interface QualityReview {
  review_id: string;
  content_id: string;
  content_type: string;
  overall_score: number;
  quality_level: string;
  feedback_items: string[];
  strengths: string[];
  improvements: string[];
  approved: boolean;
  timestamp: string;
}

interface ConsistencyReport {
  report_id: string;
  scope: string;
  scope_id: string;
  items_reviewed: number;
  consistent_items: number;
  consistency_percent: number;
  issues: string[];
  recommendations: string[];
}

interface BrandComplianceResult {
  content_id: string;
  compliance_score: number;
  compliant: boolean;
  violations: string[];
  suggestions: string[];
}

const AestheteDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('quality');
  const { status: wsStatus, messages: wsMessages } = useAestheteSocket();
  const [metrics, setMetrics] = useState<Record<string, any>>({
    reviews_conducted: 0,
    approval_rate: 0,
    average_quality_score: 0,
    brand_consistency_score: 0,
  });

  // Quality Assessment State
  const [qualityForm, setQualityForm] = useState({
    content_id: '',
    content_type: 'copy',
    guild_name: 'Content Guild',
    content_metrics: { clarity: 0.8, relevance: 0.8, engagement: 0.8, correctness: 0.8 },
  });
  const [qualityReviews, setQualityReviews] = useState<QualityReview[]>([]);
  const [qualityLoading, setQualityLoading] = useState(false);

  // Brand Compliance State
  const [complianceForm, setComplianceForm] = useState({
    content_id: '',
    guild_name: 'Brand Guild',
    content_elements: {
      tone: 'professional',
      colors: ['#1f2937', '#ffffff'],
      logos: ['logo_primary'],
    },
  });
  const [complianceResults, setComplianceResults] = useState<BrandComplianceResult[]>([]);

  // Consistency Evaluation State
  const [consistencyForm, setConsistencyForm] = useState({
    scope: 'campaign',
    scope_id: 'camp_001',
    items_count: 12,
    consistency_data: {},
  });
  const [consistencyReports, setConsistencyReports] = useState<ConsistencyReport[]>([]);

  // Design Feedback State
  const [feedbackForm, setFeedbackForm] = useState({
    content_id: '',
    content_type: 'visual',
    design_elements: {
      typography: 'sans-serif',
      color_palette: ['#1f2937', '#3b82f6'],
      spacing: 'comfortable',
      hierarchy: 'clear',
    },
    guild_name: 'Design Guild',
  });
  const [feedbackResults, setFeedbackResults] = useState<any[]>([]);

  // Handle WebSocket Messages
  useEffect(() => {
    if (wsMessages.length > 0) {
      const lastMessage = wsMessages[wsMessages.length - 1];
      if (lastMessage.type === 'status_update') {
        setMetrics(lastMessage.data?.metrics || {});
      }
    }
  }, [wsMessages]);

  // Initial Load
  useEffect(() => {
    const loadData = async () => {
      try {
        const status = await aestheteApi.getStatus();
        if (status?.performance) {
          // Update metrics
        }
      } catch (error) {
        console.error('Failed to load aesthete data', error);
      }
    };
    loadData();
  }, []);

  // Assess Quality
  const handleAssessQuality = useCallback(async () => {
    setQualityLoading(true);
    try {
      const requestData: AssessQualityRequest = {
        content_id: qualityForm.content_id,
        content_type: qualityForm.content_type,
        guild_name: qualityForm.guild_name,
        content_metrics: qualityForm.content_metrics,
      };

      const result = await aestheteApi.assessQuality(requestData);

      if (result.data && result.data.review_id) {
          const newReview: QualityReview = {
            review_id: result.data.review_id,
            content_id: qualityForm.content_id,
            content_type: qualityForm.content_type,
            overall_score: result.data.overall_score || 0,
            quality_level: result.data.quality_level || 'fair',
            feedback_items: result.data.feedback_items || [],
            strengths: result.data.strengths || [],
            improvements: result.data.improvements || [],
            approved: result.data.approved || false,
            timestamp: new Date().toISOString(),
          };
          setQualityReviews([newReview, ...qualityReviews]);
      }
    } catch (error) {
      console.error('Quality assessment error:', error);
    } finally {
      setQualityLoading(false);
    }
  }, [qualityForm, qualityReviews]);

  // Check Brand Compliance
  const handleCheckCompliance = useCallback(async () => {
    try {
      const requestData: CheckBrandComplianceRequest = {
        content_id: complianceForm.content_id,
        guild_name: complianceForm.guild_name,
        content_elements: complianceForm.content_elements,
      };

      const result = await aestheteApi.checkBrandCompliance(requestData);

      if (result.data) {
          setComplianceResults([result.data, ...complianceResults]);
      }
    } catch (error) {
      console.error('Compliance check error:', error);
    }
  }, [complianceForm, complianceResults]);

  // Evaluate Consistency
  const handleEvaluateConsistency = useCallback(async () => {
    try {
      const requestData: EvaluateVisualConsistencyRequest = {
        scope: consistencyForm.scope,
        scope_id: consistencyForm.scope_id,
        items_count: consistencyForm.items_count,
        consistency_data: consistencyForm.consistency_data,
      };

      const result = await aestheteApi.evaluateConsistency(requestData);

      if (result.data) {
          setConsistencyReports([result.data, ...consistencyReports]);
      }
    } catch (error) {
      console.error('Consistency evaluation error:', error);
    }
  }, [consistencyForm, consistencyReports]);

  // Provide Design Feedback
  const handleProvideFeedback = useCallback(async () => {
    try {
      const requestData: ProvideFeedbackRequest = {
        content_id: feedbackForm.content_id,
        content_type: feedbackForm.content_type,
        design_elements: feedbackForm.design_elements,
        guild_name: feedbackForm.guild_name,
      };

      const result = await aestheteApi.provideFeedback(requestData);

      if (result.data) {
          setFeedbackResults([result.data, ...feedbackResults]);
      }
    } catch (error) {
      console.error('Feedback provision error:', error);
    }
  }, [feedbackForm, feedbackResults]);

  const getQualityColor = (score: number): string => {
    if (score >= 85) return 'text-emerald-500';
    if (score >= 70) return 'text-blue-500';
    if (score >= 50) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getQualityBadge = (level: string): string => {
    switch (level) {
      case 'outstanding':
        return 'bg-emerald-900 text-emerald-200';
      case 'excellent':
        return 'bg-blue-900 text-blue-200';
      case 'good':
        return 'bg-cyan-900 text-cyan-200';
      case 'fair':
        return 'bg-yellow-900 text-yellow-200';
      case 'poor':
        return 'bg-red-900 text-red-200';
      default:
        return 'bg-slate-700 text-slate-200';
    }
  };

  const metricCards: MetricCard[] = [
    {
      title: 'Reviews Conducted',
      value: metrics.reviews_conducted || 0,
      description: 'Total quality assessments',
      icon: <CheckCircle2 className="w-6 h-6" />,
      color: 'from-blue-900 to-blue-700',
    },
    {
      title: 'Approval Rate',
      value: `${Math.round(metrics.approval_rate || 0)}%`,
      description: 'Content approved for publication',
      icon: <Star className="w-6 h-6" />,
      color: 'from-emerald-900 to-emerald-700',
    },
    {
      title: 'Avg Quality Score',
      value: `${(metrics.average_quality_score || 0).toFixed(1)}/100`,
      description: 'Average quality across reviews',
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'from-purple-900 to-purple-700',
    },
    {
      title: 'Brand Consistency',
      value: `${Math.round(metrics.brand_consistency_score || 0)}%`,
      description: 'Overall brand alignment',
      icon: <Zap className="w-6 h-6" />,
      color: 'from-amber-900 to-amber-700',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-400 bg-clip-text text-transparent mb-2">
                Brand & Quality
              </h1>
              <p className="text-slate-400">Content Quality & Design Consistency</p>
            </div>
            <div className="flex items-center gap-3">
              <div
                className={`w-3 h-3 rounded-full ${
                  wsStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'
                }`}
              />
              <span className="text-sm text-slate-400">
                {wsStatus === 'connected' ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          {/* Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {metricCards.map((card, index) => (
              <Card
                key={index}
                className={`bg-gradient-to-br ${card.color} border-0 text-white overflow-hidden`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
                    <div className="opacity-80">{card.icon}</div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold mb-2">{card.value}</div>
                  <p className="text-xs opacity-80">{card.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 bg-slate-800/50 border border-slate-700">
            <TabsTrigger value="quality" className="data-[state=active]:bg-slate-700">
              Quality Assessment
            </TabsTrigger>
            <TabsTrigger value="compliance" className="data-[state=active]:bg-slate-700">
              Brand Compliance
            </TabsTrigger>
            <TabsTrigger value="consistency" className="data-[state=active]:bg-slate-700">
              Consistency
            </TabsTrigger>
            <TabsTrigger value="feedback" className="data-[state=active]:bg-slate-700">
              Design Feedback
            </TabsTrigger>
          </TabsList>

          {/* Quality Assessment Tab */}
          <TabsContent value="quality" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-emerald-400">Quality Assessment Form</CardTitle>
                <CardDescription>Evaluate content against quality standards</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Content ID
                    </label>
                    <Input
                      value={qualityForm.content_id}
                      onChange={(e) =>
                        setQualityForm({ ...qualityForm, content_id: e.target.value })
                      }
                      placeholder="content_123"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Content Type
                    </label>
                    <select
                      value={qualityForm.content_type}
                      onChange={(e) =>
                        setQualityForm({ ...qualityForm, content_type: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option>copy</option>
                      <option>visual</option>
                      <option>design</option>
                      <option>messaging</option>
                      <option>branding</option>
                      <option>video</option>
                      <option>audio</option>
                      <option>interactive</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-3">
                    Content Metrics (0.0 - 1.0)
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {Object.entries(qualityForm.content_metrics).map(([key, value]) => (
                      <div key={key}>
                        <label className="block text-xs text-slate-400 mb-1 capitalize">
                          {key}
                        </label>
                        <Input
                          type="number"
                          min="0"
                          max="1"
                          step="0.1"
                          value={value}
                          onChange={(e) =>
                            setQualityForm({
                              ...qualityForm,
                              content_metrics: {
                                ...qualityForm.content_metrics,
                                [key]: parseFloat(e.target.value),
                              },
                            })
                          }
                          className="bg-slate-900 border-slate-700 text-white text-sm"
                        />
                      </div>
                    ))}
                  </div>
                </div>

                <Button
                  onClick={handleAssessQuality}
                  disabled={qualityLoading}
                  className="w-full bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white"
                >
                  {qualityLoading ? 'Assessing...' : 'Assess Quality'}
                </Button>
              </CardContent>
            </Card>

            {/* Quality Reviews List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-emerald-400">Recent Quality Reviews</h3>
              {qualityReviews.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No quality reviews yet</p>
                  </CardContent>
                </Card>
              ) : (
                qualityReviews.map((review) => (
                  <Card key={review.review_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">
                              Content: {review.content_id}
                            </p>
                            <p className="text-sm text-slate-400">{review.content_type}</p>
                          </div>
                          <div className="text-right">
                            <p className={`text-2xl font-bold ${getQualityColor(review.overall_score)}`}>
                              {review.overall_score}
                            </p>
                            <Badge className={getQualityBadge(review.quality_level)}>
                              {review.quality_level}
                            </Badge>
                          </div>
                        </div>

                        {review.strengths.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-emerald-400 mb-1">
                              Strengths
                            </p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {review.strengths.map((strength, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-emerald-500 mt-0.5">✓</span>
                                  <span>{strength}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {review.improvements.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-amber-400 mb-1">
                              Areas for Improvement
                            </p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {review.improvements.map((improvement, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-amber-500 mt-0.5">!</span>
                                  <span>{improvement}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        <div className="flex items-center justify-between pt-3 border-t border-slate-700">
                          <span className="text-xs text-slate-500">
                            {new Date(review.timestamp).toLocaleDateString()}
                          </span>
                          <Badge className={review.approved ? 'bg-emerald-900 text-emerald-200' : 'bg-slate-700 text-slate-200'}>
                            {review.approved ? 'Approved' : 'Pending'}
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Brand Compliance Tab */}
          <TabsContent value="compliance" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-blue-400">Brand Compliance Check</CardTitle>
                <CardDescription>Verify content compliance with brand guidelines</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Content ID
                    </label>
                    <Input
                      value={complianceForm.content_id}
                      onChange={(e) =>
                        setComplianceForm({ ...complianceForm, content_id: e.target.value })
                      }
                      placeholder="content_123"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Guild Name
                    </label>
                    <Input
                      value={complianceForm.guild_name}
                      onChange={(e) =>
                        setComplianceForm({ ...complianceForm, guild_name: e.target.value })
                      }
                      placeholder="Brand Guild"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Tone</label>
                  <Input
                    value={complianceForm.content_elements.tone}
                    onChange={(e) =>
                      setComplianceForm({
                        ...complianceForm,
                        content_elements: {
                          ...complianceForm.content_elements,
                          tone: e.target.value,
                        },
                      })
                    }
                    placeholder="e.g., professional, casual, formal"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <Button
                  onClick={handleCheckCompliance}
                  className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white"
                >
                  Check Compliance
                </Button>
              </CardContent>
            </Card>

            {/* Compliance Results */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-blue-400">Compliance Results</h3>
              {complianceResults.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No compliance checks yet</p>
                  </CardContent>
                </Card>
              ) : (
                complianceResults.map((result) => (
                  <Card key={result.content_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-semibold text-white">Content: {result.content_id}</p>
                          </div>
                          <div className="text-right">
                            <p className={`text-2xl font-bold ${
                              result.compliance_score >= 80 ? 'text-emerald-500' : 'text-yellow-500'
                            }`}>
                              {result.compliance_score}%
                            </p>
                            <Badge className={result.compliant ? 'bg-emerald-900 text-emerald-200' : 'bg-red-900 text-red-200'}>
                              {result.compliant ? 'Compliant' : 'Non-Compliant'}
                            </Badge>
                          </div>
                        </div>

                        {result.violations && result.violations.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-red-400 mb-1">Violations</p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {result.violations.map((violation: string, idx: number) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                                  <span>{violation}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {result.suggestions && result.suggestions.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-blue-400 mb-1">Suggestions</p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {result.suggestions.map((suggestion: string, idx: number) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-blue-500 mt-0.5">→</span>
                                  <span>{suggestion}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Consistency Tab */}
          <TabsContent value="consistency" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-cyan-400">Evaluate Visual Consistency</CardTitle>
                <CardDescription>Analyze design consistency across items</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Scope
                    </label>
                    <select
                      value={consistencyForm.scope}
                      onChange={(e) =>
                        setConsistencyForm({ ...consistencyForm, scope: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option>campaign</option>
                      <option>guild</option>
                      <option>organization</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Scope ID
                    </label>
                    <Input
                      value={consistencyForm.scope_id}
                      onChange={(e) =>
                        setConsistencyForm({ ...consistencyForm, scope_id: e.target.value })
                      }
                      placeholder="camp_001"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Items Count
                    </label>
                    <Input
                      type="number"
                      value={consistencyForm.items_count}
                      onChange={(e) =>
                        setConsistencyForm({
                          ...consistencyForm,
                          items_count: parseInt(e.target.value),
                        })
                      }
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <Button
                  onClick={handleEvaluateConsistency}
                  className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white"
                >
                  Evaluate Consistency
                </Button>
              </CardContent>
            </Card>

            {/* Consistency Reports */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-cyan-400">Consistency Reports</h3>
              {consistencyReports.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No consistency evaluations yet</p>
                  </CardContent>
                </Card>
              ) : (
                consistencyReports.map((report) => (
                  <Card key={report.report_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-semibold text-white">
                              {report.scope} - {report.scope_id}
                            </p>
                            <p className="text-sm text-slate-400">
                              {report.consistent_items}/{report.items_reviewed} items consistent
                            </p>
                          </div>
                          <div className="text-right">
                            <p className={`text-2xl font-bold ${
                              report.consistency_percent >= 85 ? 'text-emerald-500' : 'text-yellow-500'
                            }`}>
                              {report.consistency_percent}%
                            </p>
                          </div>
                        </div>

                        {report.issues && report.issues.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-amber-400 mb-1">
                              Issues Found
                            </p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {report.issues.map((issue: string, idx: number) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-amber-500 mt-0.5">⚠</span>
                                  <span>{issue}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {report.recommendations && report.recommendations.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-green-400 mb-1">
                              Recommendations
                            </p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {report.recommendations.map((rec: string, idx: number) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-green-500 mt-0.5">✓</span>
                                  <span>{rec}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Design Feedback Tab */}
          <TabsContent value="feedback" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-purple-400">Provide Design Feedback</CardTitle>
                <CardDescription>Generate constructive design feedback</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Content ID
                    </label>
                    <Input
                      value={feedbackForm.content_id}
                      onChange={(e) =>
                        setFeedbackForm({ ...feedbackForm, content_id: e.target.value })
                      }
                      placeholder="content_123"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Content Type
                    </label>
                    <select
                      value={feedbackForm.content_type}
                      onChange={(e) =>
                        setFeedbackForm({ ...feedbackForm, content_type: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option>visual</option>
                      <option>design</option>
                      <option>copy</option>
                      <option>messaging</option>
                      <option>branding</option>
                      <option>interactive</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Guild Name
                  </label>
                  <Input
                    value={feedbackForm.guild_name}
                    onChange={(e) =>
                      setFeedbackForm({ ...feedbackForm, guild_name: e.target.value })
                    }
                    placeholder="Design Guild"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Design Elements
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">Typography</label>
                      <Input
                        value={feedbackForm.design_elements.typography}
                        onChange={(e) =>
                          setFeedbackForm({
                            ...feedbackForm,
                            design_elements: {
                              ...feedbackForm.design_elements,
                              typography: e.target.value,
                            },
                          })
                        }
                        placeholder="sans-serif"
                        className="bg-slate-900 border-slate-700 text-white text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">Spacing</label>
                      <Input
                        value={feedbackForm.design_elements.spacing}
                        onChange={(e) =>
                          setFeedbackForm({
                            ...feedbackForm,
                            design_elements: {
                              ...feedbackForm.design_elements,
                              spacing: e.target.value,
                            },
                          })
                        }
                        placeholder="comfortable"
                        className="bg-slate-900 border-slate-700 text-white text-sm"
                      />
                    </div>
                  </div>
                </div>

                <Button
                  onClick={handleProvideFeedback}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white"
                >
                  Provide Feedback
                </Button>
              </CardContent>
            </Card>

            {/* Feedback Results */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-purple-400">Design Feedback Results</h3>
              {feedbackResults.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No feedback generated yet</p>
                  </CardContent>
                </Card>
              ) : (
                feedbackResults.map((feedback, idx) => (
                  <Card key={idx} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        <p className="font-semibold text-white">Content: {feedback.content_id}</p>

                        {feedback.strengths && feedback.strengths.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-emerald-400 mb-1">
                              Design Strengths
                            </p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {feedback.strengths.map((strength: string, i: number) => (
                                <li key={i} className="flex items-start gap-2">
                                  <span className="text-emerald-500 mt-0.5">✓</span>
                                  <span>{strength}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {feedback.improvements && feedback.improvements.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-yellow-400 mb-1">
                              Design Improvements
                            </p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {feedback.improvements.map((improvement: string, i: number) => (
                                <li key={i} className="flex items-start gap-2">
                                  <span className="text-yellow-500 mt-0.5">→</span>
                                  <span>{improvement}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {feedback.recommendations && feedback.recommendations.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-blue-400 mb-1">
                              Design Recommendations
                            </p>
                            <ul className="text-sm text-slate-300 space-y-1">
                              {feedback.recommendations.map((rec: string, i: number) => (
                                <li key={i} className="flex items-start gap-2">
                                  <span className="text-blue-500 mt-0.5">💡</span>
                                  <span>{rec}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AestheteDashboard;

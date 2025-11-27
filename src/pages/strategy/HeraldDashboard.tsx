// frontend/pages/strategy/HeraldDashboard.tsx
// RaptorFlow Codex - Herald Lord Dashboard
// Phase 2A Week 7 - Communications & Announcements

import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Send, Megaphone, FileText, BarChart3 } from 'lucide-react';

interface MetricCard {
  title: string;
  value: string | number;
  description: string;
  icon: React.ReactNode;
  color: string;
}

interface Message {
  message_id: string;
  channel: string;
  recipient: string;
  subject: string;
  content: string;
  priority: string;
  status: string;
  created_at: string;
}

interface Announcement {
  announcement_id: string;
  title: string;
  content: string;
  scope: string;
  channels: string[];
  scheduled_at: string;
  status: string;
  delivery_rate: number;
  open_rate: number;
}

interface Template {
  template_id: string;
  name: string;
  template_type: string;
  variables: string[];
}

interface DeliveryMetrics {
  report_id: string;
  total_messages: number;
  delivery_rate: number;
  failure_rate: number;
  open_rate: number;
}

const HeraldDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('messages');
  const [wsConnected, setWsConnected] = useState(false);
  const [metrics, setMetrics] = useState<Record<string, any>>({
    messages_sent: 0,
    messages_delivered: 0,
    announcements_created: 0,
    average_delivery_rate: 0,
  });

  // Message State
  const [messageForm, setMessageForm] = useState({
    channel: 'email',
    recipient: '',
    subject: '',
    content: '',
    priority: 'normal',
  });
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageSending, setMessageSending] = useState(false);

  // Announcement State
  const [announcementForm, setAnnouncementForm] = useState({
    title: '',
    content: '',
    scope: 'organization',
    scope_id: '',
    channels: ['email'],
    scheduled_at: new Date().toISOString().slice(0, 16),
  });
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);

  // Template State
  const [templateForm, setTemplateForm] = useState({
    name: '',
    template_type: 'campaign_announcement',
    subject_template: '',
    content_template: '',
    variables: [],
  });
  const [templates, setTemplates] = useState<Template[]>([]);

  // Delivery Report State
  const [deliveryMetrics, setDeliveryMetrics] = useState<DeliveryMetrics | null>(null);

  // WebSocket Connection
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/lords/herald`);

    ws.onopen = () => {
      console.log('✅ Connected to Herald WebSocket');
      setWsConnected(true);
      ws.send(JSON.stringify({ type: 'subscribe', lord: 'herald' }));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'status_update') {
          setMetrics(message.data?.metrics || {});
        }
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    };

    ws.onclose = () => {
      console.log('❌ Disconnected from Herald WebSocket');
      setWsConnected(false);
    };

    return () => ws.close();
  }, []);

  // Send Message
  const handleSendMessage = useCallback(async () => {
    setMessageSending(true);
    try {
      const response = await fetch('/lords/herald/messages/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(messageForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newMessage: Message = {
            message_id: result.data.message_id,
            channel: messageForm.channel,
            recipient: messageForm.recipient,
            subject: messageForm.subject,
            content: messageForm.content,
            priority: messageForm.priority,
            status: result.data.status,
            created_at: new Date().toISOString(),
          };
          setMessages([newMessage, ...messages]);
          setMessageForm({
            channel: 'email',
            recipient: '',
            subject: '',
            content: '',
            priority: 'normal',
          });
        }
      }
    } catch (error) {
      console.error('Message sending error:', error);
    } finally {
      setMessageSending(false);
    }
  }, [messageForm, messages]);

  // Schedule Announcement
  const handleScheduleAnnouncement = useCallback(async () => {
    try {
      const response = await fetch('/lords/herald/announcements/schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(announcementForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newAnnouncement: Announcement = {
            announcement_id: result.data.announcement_id,
            title: announcementForm.title,
            content: announcementForm.content,
            scope: announcementForm.scope,
            channels: announcementForm.channels,
            scheduled_at: announcementForm.scheduled_at,
            status: result.data.status,
            delivery_rate: 0,
            open_rate: 0,
          };
          setAnnouncements([newAnnouncement, ...announcements]);
          setAnnouncementForm({
            title: '',
            content: '',
            scope: 'organization',
            scope_id: '',
            channels: ['email'],
            scheduled_at: new Date().toISOString().slice(0, 16),
          });
        }
      }
    } catch (error) {
      console.error('Announcement scheduling error:', error);
    }
  }, [announcementForm, announcements]);

  // Create Template
  const handleCreateTemplate = useCallback(async () => {
    try {
      const response = await fetch('/lords/herald/templates/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(templateForm),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          const newTemplate: Template = {
            template_id: result.data.template_id,
            name: templateForm.name,
            template_type: templateForm.template_type,
            variables: templateForm.variables,
          };
          setTemplates([newTemplate, ...templates]);
          setTemplateForm({
            name: '',
            template_type: 'campaign_announcement',
            subject_template: '',
            content_template: '',
            variables: [],
          });
        }
      }
    } catch (error) {
      console.error('Template creation error:', error);
    }
  }, [templateForm, templates]);

  // Get Delivery Report
  const handleGetReport = useCallback(async () => {
    try {
      const response = await fetch('/lords/herald/reporting/communication-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ period_days: 30 }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          setDeliveryMetrics(result.data);
        }
      }
    } catch (error) {
      console.error('Report generation error:', error);
    }
  }, []);

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'critical':
        return 'bg-red-900 text-red-200';
      case 'high':
        return 'bg-orange-900 text-orange-200';
      case 'normal':
        return 'bg-blue-900 text-blue-200';
      case 'low':
        return 'bg-green-900 text-green-200';
      default:
        return 'bg-slate-700 text-slate-200';
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'sent':
      case 'delivered':
        return 'text-emerald-400';
      case 'failed':
        return 'text-red-400';
      case 'queued':
        return 'text-yellow-400';
      default:
        return 'text-slate-400';
    }
  };

  const metricCards: MetricCard[] = [
    {
      title: 'Messages Sent',
      value: metrics.messages_sent || 0,
      description: 'Total messages sent',
      icon: <Send className="w-6 h-6" />,
      color: 'from-cyan-900 to-cyan-700',
    },
    {
      title: 'Delivered',
      value: metrics.messages_delivered || 0,
      description: 'Successfully delivered',
      icon: <BarChart3 className="w-6 h-6" />,
      color: 'from-emerald-900 to-emerald-700',
    },
    {
      title: 'Announcements',
      value: metrics.announcements_created || 0,
      description: 'Scheduled announcements',
      icon: <Megaphone className="w-6 h-6" />,
      color: 'from-amber-900 to-amber-700',
    },
    {
      title: 'Delivery Rate',
      value: `${(metrics.average_delivery_rate || 0).toFixed(0)}%`,
      description: 'Average success rate',
      icon: <FileText className="w-6 h-6" />,
      color: 'from-indigo-900 to-indigo-700',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent mb-2">
                📢 Herald Lord
              </h1>
              <p className="text-slate-400">Communications & Announcements</p>
            </div>
            <div className="flex items-center gap-3">
              <div
                className={`w-3 h-3 rounded-full ${
                  wsConnected ? 'bg-cyan-500 animate-pulse' : 'bg-red-500'
                }`}
              />
              <span className="text-sm text-slate-400">
                {wsConnected ? 'Connected' : 'Disconnected'}
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
            <TabsTrigger value="messages" className="data-[state=active]:bg-slate-700">
              Messages
            </TabsTrigger>
            <TabsTrigger value="announcements" className="data-[state=active]:bg-slate-700">
              Announcements
            </TabsTrigger>
            <TabsTrigger value="templates" className="data-[state=active]:bg-slate-700">
              Templates
            </TabsTrigger>
            <TabsTrigger value="reports" className="data-[state=active]:bg-slate-700">
              Reports
            </TabsTrigger>
          </TabsList>

          {/* Messages Tab */}
          <TabsContent value="messages" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-cyan-400">Send Message</CardTitle>
                <CardDescription>Send messages through multiple channels</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Channel
                    </label>
                    <select
                      value={messageForm.channel}
                      onChange={(e) =>
                        setMessageForm({ ...messageForm, channel: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option>email</option>
                      <option>sms</option>
                      <option>push_notification</option>
                      <option>in_app</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Recipient
                    </label>
                    <Input
                      value={messageForm.recipient}
                      onChange={(e) =>
                        setMessageForm({ ...messageForm, recipient: e.target.value })
                      }
                      placeholder="recipient@example.com"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Subject
                  </label>
                  <Input
                    value={messageForm.subject}
                    onChange={(e) =>
                      setMessageForm({ ...messageForm, subject: e.target.value })
                    }
                    placeholder="Message subject"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Content
                  </label>
                  <textarea
                    value={messageForm.content}
                    onChange={(e) =>
                      setMessageForm({ ...messageForm, content: e.target.value })
                    }
                    placeholder="Message content"
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <Button
                  onClick={handleSendMessage}
                  disabled={messageSending}
                  className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white"
                >
                  {messageSending ? 'Sending...' : 'Send Message'}
                </Button>
              </CardContent>
            </Card>

            {/* Messages List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-cyan-400">Recent Messages</h3>
              {messages.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No messages sent yet</p>
                  </CardContent>
                </Card>
              ) : (
                messages.map((msg) => (
                  <Card key={msg.message_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">{msg.subject}</p>
                            <p className="text-sm text-slate-400">{msg.recipient}</p>
                          </div>
                          <div className="flex gap-2">
                            <Badge className={getPriorityColor(msg.priority)}>
                              {msg.priority}
                            </Badge>
                            <Badge className={getStatusColor(msg.status)}>
                              {msg.status}
                            </Badge>
                          </div>
                        </div>
                        <p className="text-sm text-slate-300">{msg.content}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Announcements Tab */}
          <TabsContent value="announcements" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-amber-400">Schedule Announcement</CardTitle>
                <CardDescription>Schedule org-wide or scoped announcements</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Title
                  </label>
                  <Input
                    value={announcementForm.title}
                    onChange={(e) =>
                      setAnnouncementForm({ ...announcementForm, title: e.target.value })
                    }
                    placeholder="Announcement title"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Content
                  </label>
                  <textarea
                    value={announcementForm.content}
                    onChange={(e) =>
                      setAnnouncementForm({ ...announcementForm, content: e.target.value })
                    }
                    placeholder="Announcement content"
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Scope
                    </label>
                    <select
                      value={announcementForm.scope}
                      onChange={(e) =>
                        setAnnouncementForm({ ...announcementForm, scope: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option>organization</option>
                      <option>guild</option>
                      <option>campaign</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Schedule
                    </label>
                    <Input
                      type="datetime-local"
                      value={announcementForm.scheduled_at}
                      onChange={(e) =>
                        setAnnouncementForm({ ...announcementForm, scheduled_at: e.target.value })
                      }
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <Button
                  onClick={handleScheduleAnnouncement}
                  className="w-full bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white"
                >
                  Schedule Announcement
                </Button>
              </CardContent>
            </Card>

            {/* Announcements List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-amber-400">Announcements</h3>
              {announcements.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No announcements scheduled</p>
                  </CardContent>
                </Card>
              ) : (
                announcements.map((ann) => (
                  <Card key={ann.announcement_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="space-y-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-white">{ann.title}</p>
                            <p className="text-sm text-slate-400">{ann.scope}</p>
                          </div>
                          <Badge className={getStatusColor(ann.status)}>{ann.status}</Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <p className="text-xs text-slate-400">Delivery Rate</p>
                            <p className="text-sm font-semibold text-emerald-400">
                              {ann.delivery_rate.toFixed(0)}%
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400">Open Rate</p>
                            <p className="text-sm font-semibold text-blue-400">
                              {ann.open_rate.toFixed(0)}%
                            </p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Templates Tab */}
          <TabsContent value="templates" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-indigo-400">Create Template</CardTitle>
                <CardDescription>Create reusable message templates</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Template Name
                  </label>
                  <Input
                    value={templateForm.name}
                    onChange={(e) =>
                      setTemplateForm({ ...templateForm, name: e.target.value })
                    }
                    placeholder="Template name"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Type
                  </label>
                  <select
                    value={templateForm.template_type}
                    onChange={(e) =>
                      setTemplateForm({ ...templateForm, template_type: e.target.value })
                    }
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  >
                    <option>campaign_announcement</option>
                    <option>system_alert</option>
                    <option>user_invitation</option>
                    <option>performance_report</option>
                    <option>reminder</option>
                  </select>
                </div>

                <Button
                  onClick={handleCreateTemplate}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white"
                >
                  Create Template
                </Button>
              </CardContent>
            </Card>

            {/* Templates List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-indigo-400">Message Templates</h3>
              {templates.length === 0 ? (
                <Card className="bg-slate-800/30 border-slate-700">
                  <CardContent className="pt-6">
                    <p className="text-slate-400 text-center">No custom templates created</p>
                  </CardContent>
                </Card>
              ) : (
                templates.map((tpl) => (
                  <Card key={tpl.template_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <p className="font-semibold text-white mb-1">{tpl.name}</p>
                      <p className="text-sm text-slate-400">{tpl.template_type}</p>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Reports Tab */}
          <TabsContent value="reports" className="space-y-6 mt-6">
            <Button
              onClick={handleGetReport}
              className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white"
            >
              Generate 30-Day Report
            </Button>

            {deliveryMetrics && (
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-violet-400">Communication Report</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Total Messages</p>
                      <p className="text-2xl font-bold text-white">
                        {deliveryMetrics.total_messages}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Delivery Rate</p>
                      <p className="text-2xl font-bold text-emerald-400">
                        {deliveryMetrics.delivery_rate.toFixed(0)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Failure Rate</p>
                      <p className="text-2xl font-bold text-red-400">
                        {deliveryMetrics.failure_rate.toFixed(0)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Open Rate</p>
                      <p className="text-2xl font-bold text-blue-400">
                        {deliveryMetrics.open_rate.toFixed(0)}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default HeraldDashboard;

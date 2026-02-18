"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import gsap from "gsap";
import { Layout } from "@/components/raptor/shell/Layout";
import { Button } from "@/components/raptor/ui/Button";
import { Badge } from "@/components/raptor/ui/Badge";
import { Card } from "@/components/raptor/ui/Card";
import {
  Send,
  Sparkles,
  Zap,
  Copy,
  Check,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  Lock,
  MessageSquare,
  Wand2,
  PenTool,
  Highlighter,
  ChevronDown,
  ChevronUp,
  FileText,
  Target,
  Lightbulb,
  X,
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════════════════════
// MUSE PAGE — AI Content Assistant
// "AI content assistant for the Learn loop"
// ═══════════════════════════════════════════════════════════════════════════════

type ChatMode = "chat" | "generate" | "refine";
type ConfidenceLevel = "high" | "medium" | "low";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  isGenerating?: boolean;
  confidence?: ConfidenceLevel;
  sources?: string[];
  assumptions?: string[];
  suggestions?: string[];
}

interface MuseContext {
  topic?: string;
  angle?: string;
  hook?: string;
  outline?: string[];
  platform?: string;
}

// Quick action prompts
const quickActions = [
  { icon: PenTool, label: "Write a headline", prompt: "Help me write a headline for" },
  { icon: Highlighter, label: "Refine this copy", prompt: "Refine this copy:" },
  { icon: FileText, label: "Generate email", prompt: "Write an email about" },
  { icon: MessageSquare, label: "Create social post", prompt: "Create a social media post for" },
];

// Mock conversation
const mockMuseConversation: Message[] = [
  {
    id: "msg-1",
    role: "user",
    content: "Help me write a headline for our landing page. We're launching the new workflow automation feature.",
    timestamp: new Date("2024-01-15T10:30:00"),
  },
  {
    id: "msg-2",
    role: "assistant",
    content: `Here are 3 headline options based on your positioning:

1. "Eliminate 10 Hours of Busywork Every Week"
2. "The Automation Platform That Actually Works"
3. "Stop Doing Work Your Computer Should Handle"

Which direction resonates? I can refine any of these.`,
    timestamp: new Date("2024-01-15T10:31:00"),
    confidence: "high",
    sources: ["Foundation: Value Prop", "Move: Q1 Content"],
    assumptions: ["Time savings is primary benefit"],
    suggestions: ["Use option 1", "Use option 2", "Refine option 3"],
  },
];

// Mode badge config
const modeConfig: Record<ChatMode, { label: string; icon: React.ElementType; color: string }> = {
  chat: { label: "Chat", icon: MessageSquare, color: "bg-[var(--bg-canvas)]" },
  generate: { label: "Generate", icon: Wand2, color: "bg-[var(--status-success-bg)]" },
  refine: { label: "Refine", icon: PenTool, color: "bg-[var(--status-warning-bg)]" },
};

// Message Bubble Component
function MessageBubble({
  message,
  onCopy,
  onSuggestion,
}: {
  message: Message;
  onCopy: () => void;
  onSuggestion?: (suggestion: string) => void;
}) {
  const [copied, setCopied] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const isAssistant = message.role === "assistant";
  const isSystem = message.role === "system";

  const handleCopy = () => {
    onCopy();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (isSystem) {
    return (
      <div className="flex items-center justify-center my-4">
        <span className="rf-mono-xs px-3 py-1 bg-[var(--bg-canvas)] rounded-full text-[var(--ink-3)]">
          {message.content}
        </span>
      </div>
    );
  }

  return (
    <div
      className={`flex items-start gap-4 ${
        isAssistant ? "" : "flex-row-reverse"
      }`}
    >
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isAssistant
            ? "bg-[var(--ink-1)] text-[var(--ink-inverse)]"
            : "bg-[var(--bg-canvas)] border border-[var(--border-1)] text-[var(--ink-1)]"
        }`}
      >
        {isAssistant ? <Sparkles size={14} /> : <span className="text-[12px] font-semibold">You</span>}
      </div>

      {/* Content */}
      <div className={`flex-1 ${isAssistant ? "" : "flex justify-end"}`}>
        <div
          className={`max-w-[85%] p-4 rounded-[var(--radius-md)] ${
            isAssistant
              ? "bg-[var(--bg-surface)] border border-[var(--border-1)]"
              : "bg-[var(--ink-1)] text-[var(--ink-inverse)]"
          }`}
        >
          {/* Message content */}
          <div
            className={`rf-body whitespace-pre-wrap ${
              isAssistant ? "" : "text-[var(--ink-inverse)]"
            }`}
          >
            {message.content}
          </div>

          {/* Assistant metadata */}
          {isAssistant && (
            <div className="mt-4 pt-3 border-t border-[var(--border-1)]">
              {/* Confidence & Expand */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {message.confidence && (
                    <span
                      className={`rf-mono-xs ${
                        message.confidence === "high"
                          ? "text-[var(--status-success)]"
                          : message.confidence === "medium"
                          ? "text-[var(--status-warning)]"
                          : "text-[var(--status-error)]"
                      }`}
                    >
                      {message.confidence} confidence
                    </span>
                  )}
                </div>

                <button
                  onClick={() => setShowDetails(!showDetails)}
                  className="flex items-center gap-1 text-[var(--ink-3)] hover:text-[var(--ink-1)] transition-colors"
                >
                  <span className="rf-mono-xs">Details</span>
                  {showDetails ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                </button>
              </div>

              {/* Expanded details */}
              {showDetails && (
                <div className="mt-3 space-y-2 pt-3 border-t border-[var(--border-1)]">
                  {message.sources && message.sources.length > 0 && (
                    <div className="flex items-start gap-2">
                      <Target size={12} className="text-[var(--ink-3)] mt-1 flex-shrink-0" />
                      <div>
                        <span className="rf-mono-xs text-[var(--ink-3)]">Sources:</span>
                        <p className="rf-body-sm text-[var(--ink-2)]">{message.sources.join(", ")}</p>
                      </div>
                    </div>
                  )}
                  {message.assumptions && message.assumptions.length > 0 && (
                    <div className="flex items-start gap-2">
                      <Lightbulb size={12} className="text-[var(--ink-3)] mt-1 flex-shrink-0" />
                      <div>
                        <span className="rf-mono-xs text-[var(--ink-3)]">Assumptions:</span>
                        <p className="rf-body-sm text-[var(--ink-2)]">{message.assumptions.join(", ")}</p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Suggestion chips */}
              {message.suggestions && message.suggestions.length > 0 && (
                <div className="mt-3 pt-3 border-t border-[var(--border-1)]">
                  <div className="flex flex-wrap gap-2">
                    {message.suggestions.map((suggestion, i) => (
                      <button
                        key={i}
                        onClick={() => onSuggestion?.(suggestion)}
                        className="px-3 py-1.5 bg-[var(--bg-canvas)] hover:bg-[var(--state-hover)] rounded-[var(--radius-sm)] text-[12px] font-medium text-[var(--ink-2)] hover:text-[var(--ink-1)] transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-end gap-1 mt-3 pt-3 border-t border-[var(--border-1)]">
                <button
                  onClick={handleCopy}
                  className="p-1.5 rounded-[var(--radius-sm)] hover:bg-[var(--state-hover)] transition-colors"
                  title="Copy to clipboard"
                >
                  {copied ? (
                    <Check size={14} className="text-[var(--status-success)]" />
                  ) : (
                    <Copy size={14} className="text-[var(--ink-3)]" />
                  )}
                </button>
                <button className="p-1.5 rounded-[var(--radius-sm)] hover:bg-[var(--state-hover)] transition-colors">
                  <ThumbsUp size={14} className="text-[var(--ink-3)]" />
                </button>
                <button className="p-1.5 rounded-[var(--radius-sm)] hover:bg-[var(--state-hover)] transition-colors">
                  <ThumbsDown size={14} className="text-[var(--ink-3)]" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Timestamp */}
        <div
          className={`mt-1 rf-mono-xs text-[var(--ink-3)] ${
            isAssistant ? "" : "text-right"
          }`}
        >
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </div>
    </div>
  );
}

// Context Panel Component
function ContextPanel({
  mode,
  onClose,
}: {
  mode: ChatMode;
  onClose: () => void;
}) {
  return (
    <div className="w-[320px] h-full bg-[var(--bg-surface)] border-l border-[var(--border-1)] p-6 overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <h3 className="rf-h4">Context</h3>
        <button
          onClick={onClose}
          className="p-1.5 rounded-[var(--radius-sm)] hover:bg-[var(--state-hover)] text-[var(--ink-3)]"
        >
          <X size={18} />
        </button>
      </div>

      {/* Current Context */}
      <div className="space-y-4">
        <Card className="bg-[var(--bg-canvas)]">
          <div className="flex items-center gap-2 mb-2">
            <Target size={16} className="text-[var(--ink-3)]" />
            <span className="rf-label text-[var(--ink-3)]">Current Move</span>
          </div>
          <p className="rf-body-sm font-medium">Q1 Content Sprint</p>
          <p className="rf-body-sm text-[var(--ink-2)] mt-1">Enterprise positioning campaign</p>
        </Card>

        <Card className="bg-[var(--bg-canvas)]">
          <div className="flex items-center gap-2 mb-2">
            <FileText size={16} className="text-[var(--ink-3)]" />
            <span className="rf-label text-[var(--ink-3)]">Selected Text</span>
          </div>
          <p className="rf-body-sm text-[var(--ink-2)] italic">
            &ldquo;Workflow automation for enterprise teams...&rdquo;
          </p>
        </Card>

        {/* Mode-specific options */}
        <div className="pt-4 border-t border-[var(--border-1)]">
          <span className="rf-label text-[var(--ink-3)] mb-3 block">
            {mode === "generate" ? "Generation Options" : mode === "refine" ? "Refine Options" : "Chat Options"}
          </span>
          <div className="space-y-2">
            {["Use brand voice", "Include CTA", "SEO optimized", "Short form"].map((option) => (
              <label key={option} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  className="w-4 h-4 rounded border-[var(--border-1)] text-[var(--ink-1)] focus:ring-[var(--ink-1)]"
                />
                <span className="rf-body-sm text-[var(--ink-2)]">{option}</span>
              </label>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Main Muse Page
export default function MusePage() {
  const searchParams = useSearchParams();
  const pageRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Message[]>(mockMuseConversation);
  const [inputValue, setInputValue] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [mode, setMode] = useState<ChatMode>("chat");
  const [showContext, setShowContext] = useState(true);
  const [showWelcome, setShowWelcome] = useState(true);

  // Parse context from URL if provided
  const initialContext = useMemo(() => {
    if (!searchParams) return null;
    const contextParam = searchParams.get("context");
    if (!contextParam) return null;

    try {
      const parsed = JSON.parse(decodeURIComponent(contextParam)) as MuseContext;
      return parsed;
    } catch {
      return null;
    }
  }, [searchParams]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // GSAP Entrance Animation
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".muse-container",
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }
      );

      gsap.fromTo(
        ".message-item",
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.3, stagger: 0.1, ease: "power2.out", delay: 0.3 }
      );
    }, pageRef);

    return () => ctx.revert();
  }, []);

  // Animate new messages
  useEffect(() => {
    if (messages.length > mockMuseConversation.length) {
      gsap.fromTo(
        ".message-item:last-child",
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.3, ease: "power2.out" }
      );
    }
  }, [messages.length]);

  const handleSend = async () => {
    if (!inputValue.trim() || isGenerating) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsGenerating(true);
    setShowWelcome(false);

    // Simulate AI response
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: generateMockResponse(inputValue, mode),
      timestamp: new Date(),
      confidence: "high",
      sources: ["Foundation: Core Messaging", "ICP: Primary Audience"],
      assumptions: ["Time savings is primary benefit"],
      suggestions: ["Apply this version", "Make it shorter", "Try different angle"],
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setIsGenerating(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const handleSuggestion = (suggestion: string) => {
    setInputValue(suggestion);
  };

  const handleQuickAction = (prompt: string) => {
    setInputValue(prompt + " ");
  };

  const ModeIcon = modeConfig[mode].icon;

  return (
    <Layout
      mode="draft"
      showDrawer={showContext}
      drawerContent={showContext ? <ContextPanel mode={mode} onClose={() => setShowContext(false)} /> : null}
      activeNavItem="muse"
    >
      <div ref={pageRef} className="muse-container h-full flex flex-col">
        {/* Header */}
        <header className="flex items-center justify-between mb-6 px-6 pt-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-[var(--radius-md)] bg-[var(--ink-1)] flex items-center justify-center">
              <Sparkles size={20} className="text-[var(--ink-inverse)]" />
            </div>
            <div>
              <h1 className="rf-h3">Muse</h1>
              <p className="rf-body-sm text-[var(--ink-2)]">AI content assistant</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Mode Toggle */}
            <div className="flex items-center bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[var(--radius-sm)] p-1">
              {( ["chat", "generate", "refine"] as ChatMode[]).map((m) => {
                const Icon = modeConfig[m].icon;
                return (
                  <button
                    key={m}
                    onClick={() => setMode(m)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-sm)] text-[12px] font-medium transition-colors ${
                      mode === m
                        ? "bg-[var(--ink-1)] text-[var(--ink-inverse)]"
                        : "text-[var(--ink-2)] hover:text-[var(--ink-1)]"
                    }`}
                  >
                    <Icon size={14} />
                    {modeConfig[m].label}
                  </button>
                );
              })}
            </div>

            <Badge variant="info" size="sm">GPT-4</Badge>
            <Button variant="ghost" size="sm" onClick={() => setShowContext(!showContext)}>
              <Lock size={14} />
            </Button>
          </div>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 space-y-6">
          {/* Welcome State */}
          {showWelcome && messages.length <= mockMuseConversation.length && (
            <div className="welcome-section flex flex-col items-center justify-center py-12 text-center">
              <div className="w-16 h-16 rounded-full bg-[var(--bg-surface)] border border-[var(--border-1)] flex items-center justify-center mb-4">
                <Sparkles size={28} className="text-[var(--ink-1)]" />
              </div>
              <h2 className="rf-h3 mb-2">What would you like to create?</h2>
              <p className="rf-body text-[var(--ink-2)] max-w-md mb-8">
                Muse can help you draft content, refine messaging, and generate ideas based on your foundation.
              </p>

              {/* Quick Actions */}
              <div className="grid grid-cols-2 gap-3 max-w-lg">
                {quickActions.map((action) => {
                  const Icon = action.icon;
                  return (
                    <button
                      key={action.label}
                      onClick={() => handleQuickAction(action.prompt)}
                      className="flex items-center gap-3 p-4 bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[var(--radius-md)] hover:border-[var(--border-2)] transition-colors text-left"
                    >
                      <div className="w-8 h-8 rounded-[var(--radius-sm)] bg-[var(--bg-canvas)] flex items-center justify-center">
                        <Icon size={16} className="text-[var(--ink-2)]" />
                      </div>
                      <span className="rf-body-sm font-medium">{action.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.map((message) => (
            <div key={message.id} className="message-item">
              <MessageBubble
                message={message}
                onCopy={() => handleCopy(message.content)}
                onSuggestion={handleSuggestion}
              />
            </div>
          ))}

          {/* Typing Indicator */}
          {isGenerating && (
            <div className="flex items-start gap-4 message-item">
              <div className="w-8 h-8 rounded-full bg-[var(--ink-1)] flex items-center justify-center flex-shrink-0">
                <Sparkles size={14} className="text-[var(--ink-inverse)]" />
              </div>
              <div className="p-4 bg-[var(--bg-canvas)] rounded-[var(--radius-md)]">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-[var(--ink-3)] rounded-full animate-bounce" />
                  <div
                    className="w-2 h-2 bg-[var(--ink-3)] rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  />
                  <div
                    className="w-2 h-2 bg-[var(--ink-3)] rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-6 border-t border-[var(--border-1)]">
          {/* Quick Action Chips */}
          <div className="flex items-center gap-2 mb-3 overflow-x-auto">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <button
                  key={action.label}
                  onClick={() => handleQuickAction(action.prompt)}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-full text-[12px] text-[var(--ink-2)] hover:border-[var(--border-2)] hover:text-[var(--ink-1)] transition-colors whitespace-nowrap"
                >
                  <Icon size={12} />
                  {action.label}
                </button>
              );
            })}
          </div>

          <div className="relative">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask Muse to ${mode === "generate" ? "generate" : mode === "refine" ? "refine" : "help with"} content...`}
              className="w-full min-h-[100px] p-4 pr-14 bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[var(--radius-md)] resize-none focus:outline-none focus:border-[var(--ink-1)] transition-colors rf-body"
              disabled={isGenerating}
            />
            <button
              onClick={handleSend}
              disabled={!inputValue.trim() || isGenerating}
              className="absolute right-3 bottom-3 w-10 h-10 bg-[var(--ink-1)] text-[var(--ink-inverse)] rounded-[var(--radius-sm)] flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[var(--ink-2)] transition-colors"
            >
              <Send size={18} />
            </button>
          </div>

          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center gap-4">
              <span className="rf-mono-xs text-[var(--ink-3)]">
                Press Enter to send, Shift+Enter for new line
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="tertiary" size="sm">
                <RefreshCw size={14} />
                Regenerate
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// MOCK RESPONSE GENERATOR
// ═══════════════════════════════════════════════════════════════════════════════

function generateMockResponse(input: string, mode: ChatMode): string {
  const lowercase = input.toLowerCase();

  if (mode === "generate" || lowercase.includes("write") || lowercase.includes("create")) {
    if (lowercase.includes("headline")) {
      return `Here are 5 headline options:

1. "The Workflow Automation That Saves 10 Hours Every Week"
2. "Stop Doing Work Your Computer Should Handle"
3. "Finally: Automation That Actually Works for Enterprise"
4. "Eliminate Busywork Without Losing Control"
5. "Your Team's Time Is Too Valuable to Waste on Manual Tasks"

Each emphasizes a different angle: time savings, relief, trust, control, and value respectively. Which direction feels right for this campaign?`;
    }

    if (lowercase.includes("email")) {
      return `Here's a draft email:

Subject: The $50K mistake I see enterprise teams making

Hi [First Name],

I was reviewing our Q4 data and noticed something concerning.

78% of enterprise operations teams we surveyed are losing an average of 12 hours per week to manual workflow tasks. At $150/hour fully loaded, that's $93,600 annually in lost productivity.

The kicker? Most don't realize it's happening.

The tasks feel "quick" individually—5 minutes here, 10 minutes there. But they compound into a full day every week.

We've built something to fix this without the typical automation trade-offs (rigid workflows, months of implementation, IT dependency).

Worth a 15-minute conversation?

[CTA: Book a brief call]

Best,
[Name]

P.S. If you're skeptical (you should be), I'll share the full survey data on the call. No pitch deck.`;
    }

    return `I'd be happy to help you generate that content. To make it most effective, could you share:

1. **Target platform** - Where will this live?
2. **Desired length** - Short-form or long-form?
3. **Key message** - What's the one thing you want them to remember?
4. **Call to action** - What should they do after reading?

Or, if you have existing content you'd like me to work from, paste it here and I can adapt it.`;
  }

  if (mode === "refine" || lowercase.includes("refine") || lowercase.includes("improve")) {
    return `Here's the refined version with improvements:

**Changes made:**
- Strengthened the hook (first 2 lines now create curiosity gap)
- Removed 3 instances of passive voice
- Tightened from 127 words to 94 (26% reduction)
- Added specific number for credibility
- Ended with open loop instead of closed statement

**Before:** [Your original text]
**After:** [Refined text]

The refined version should feel more direct and urgent while maintaining your brand voice. Want me to try a different angle or adjust the tone?`;
  }

  if (lowercase.includes("launch") || lowercase.includes("product")) {
    return `Here's a launch sequence draft:

**Week 1: Tease**
- Day 1-2: Problem agitation ("Tired of...?")
- Day 3-4: Solution hint without naming
- Day 5-7: Behind-the-scenes building tension

**Week 2: Reveal**
- Day 8: Official announcement
- Day 9-10: Feature deep-dives
- Day 11-12: Social proof injection
- Day 13-14: Urgency + CTA

Each post should reference your core value prop: solving [specific pain point] for [ICP].

Want me to draft the actual posts for any of these days?`;
  }

  return `I can help you with that. A few clarifying questions:

1. **Platform**: Where will this content live? (LinkedIn, email, blog, ads)
2. **Stage**: What sophistication level is your audience at?
3. **Goal**: Awareness, consideration, or conversion?
4. **Format**: Long-form, thread, carousel, video script?

Once you give me these, I'll draft something specific to your foundation and ICPs.

Or if you want, I can propose 3 different angles based on your current positioning.`;
}

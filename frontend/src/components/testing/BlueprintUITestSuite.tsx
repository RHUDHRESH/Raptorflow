"use client";

import React, { useState } from "react";
import {
  User,
  Mail,
  Lock,
  Search,
  Bell,
  Settings,
  Plus,
  Edit,
  Trash2,
  Download,
  Upload,
  Filter,
  Calendar,
  TrendingUp,
  Target,
  Zap,
  Compass,
  Inbox,
  Check,
  X,
  ChevronDown,
  ChevronRight,
  Menu,
  Home,
  BarChart3,
  Users,
  FileText,
  HelpCircle,
  LayoutGrid
} from "lucide-react";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { BlueprintInput } from "@/components/ui/BlueprintInput";
import { BlueprintEmptyState } from "@/components/ui/BlueprintEmptyState";
import { BlueprintLoader } from "@/components/ui/BlueprintLoader";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT UI TEST SUITE
   Comprehensive testing component for UI consistency and validation
   ══════════════════════════════════════════════════════════════════════════════ */

export function BlueprintUITestSuite() {
  const [activeSection, setActiveSection] = useState("components");
  const [testResults, setTestResults] = useState<Record<string, boolean>>({});

  const sections = [
    { id: "components", name: "Components", icon: Plus },
    { id: "forms", name: "Forms", icon: Edit },
    { id: "navigation", name: "Navigation", icon: Menu },
    { id: "states", name: "States", icon: Bell },
    { id: "layout", name: "Layout", icon: LayoutGrid },
  ];

  const runTest = (testName: string) => {
    // Simulate test execution
    setTestResults(prev => ({ ...prev, [testName]: true }));
    setTimeout(() => {
      setTestResults(prev => ({ ...prev, [testName]: false }));
    }, 2000);
  };

  const renderComponents = () => (
    <div className="space-y-8">
      <BlueprintCard figure="COMP" code="TEST-01" padding="lg">
        <h3 className="font-serif text-xl text-[var(--ink)] mb-4">Button Components</h3>
        <div className="space-y-4">
          <div className="flex flex-wrap gap-4">
            <BlueprintButton size="sm">Small</BlueprintButton>
            <BlueprintButton size="md">Medium</BlueprintButton>
            <BlueprintButton size="lg">Large</BlueprintButton>
          </div>
          <div className="flex flex-wrap gap-4">
            <BlueprintButton variant="primary">Primary</BlueprintButton>
            <BlueprintButton variant="secondary">Secondary</BlueprintButton>
            <BlueprintButton variant="ghost">Ghost</BlueprintButton>
          </div>
          <div className="flex flex-wrap gap-4">
            <BlueprintButton disabled>Disabled</BlueprintButton>
            <BlueprintButton>
              <BlueprintLoader size="sm" />
              Loading
            </BlueprintButton>
          </div>
        </div>
      </BlueprintCard>

      <BlueprintCard figure="CARD" code="TEST-02" padding="lg">
        <h3 className="font-serif text-xl text-[var(--ink)] mb-4">Card Components</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <BlueprintCard variant="default" padding="md">
            <h4 className="font-semibold text-[var(--ink)]">Default Card</h4>
            <p className="text-sm text-[var(--ink-secondary)] mt-2">Standard card variant</p>
          </BlueprintCard>
          <BlueprintCard variant="elevated" padding="md" showCorners>
            <h4 className="font-semibold text-[var(--ink)]">Elevated Card</h4>
            <p className="text-sm text-[var(--ink-secondary)] mt-2">With elevation</p>
          </BlueprintCard>
          <BlueprintCard variant="default" padding="md" showGrid>
            <h4 className="font-semibold text-[var(--ink)]">Grid Card</h4>
            <p className="text-sm text-[var(--ink-secondary)] mt-2">With grid background</p>
          </BlueprintCard>
        </div>
      </BlueprintCard>

      <BlueprintCard figure="BADGE" code="TEST-03" padding="lg">
        <h3 className="font-serif text-xl text-[var(--ink)] mb-4">Badge Components</h3>
        <div className="flex flex-wrap gap-4">
          <BlueprintBadge variant="default">Default</BlueprintBadge>
          <BlueprintBadge variant="blueprint">Blueprint</BlueprintBadge>
          <BlueprintBadge variant="success">Success</BlueprintBadge>
          <BlueprintBadge variant="warning">Warning</BlueprintBadge>
          <BlueprintBadge variant="error">Error</BlueprintBadge>
          <BlueprintBadge variant="info">Info</BlueprintBadge>
        </div>
      </BlueprintCard>
    </div>
  );

  const renderForms = () => (
    <div className="space-y-8">
      <BlueprintCard figure="FORM" code="TEST-04" padding="lg">
        <h3 className="font-serif text-xl text-[var(--ink)] mb-4">Input Components</h3>
        <div className="space-y-6 max-w-md">
          <BlueprintInput
            label="Name"
            placeholder="Enter your name"
            startIcon={<User size={16} />}
          />
          <BlueprintInput
            label="Email"
            type="email"
            placeholder="Enter your email"
            startIcon={<Mail size={16} />}
          />
          <BlueprintInput
            label="Password"
            type="password"
            placeholder="Enter your password"
            startIcon={<Lock size={16} />}
          />
          <BlueprintInput
            label="Search"
            placeholder="Search..."
            startIcon={<Search size={16} />}
            endIcon={<Filter size={16} />}
          />
          <BlueprintInput
            label="Disabled Input"
            placeholder="This is disabled"
            disabled
          />
          <BlueprintInput
            label="Error Input"
            placeholder="This has an error"
            error="This field is required"
          />
        </div>
      </BlueprintCard>

      <BlueprintCard figure="FORM" code="TEST-05" padding="lg">
        <h3 className="font-serif text-xl text-[var(--ink)] mb-4">Form Layouts</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <BlueprintInput
              label="First Name"
              placeholder="John"
            />
            <BlueprintInput
              label="Last Name"
              placeholder="Doe"
            />
          </div>
          <div className="space-y-4">
            <BlueprintInput
              label="Email"
              type="email"
              placeholder="john@example.com"
            />
            <BlueprintInput
              label="Phone"
              placeholder="+1 (555) 123-4567"
            />
          </div>
        </div>
      </BlueprintCard>
    </div>
  );

  const renderNavigation = () => (
    <div className="space-y-8">
      <BlueprintCard figure="NAV" code="TEST-06" padding="lg">
        <h3 className="font-serif text-xl text-[var(--ink)] mb-4">Navigation Components</h3>
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <BlueprintButton variant="ghost" size="sm">
              <Home size={14} />
              Dashboard
            </BlueprintButton>
            <BlueprintButton variant="ghost" size="sm">
              <BarChart3 size={14} />
              Analytics
            </BlueprintButton>
            <BlueprintButton variant="ghost" size="sm">
              <Users size={14} />
              Teams
            </BlueprintButton>
            <BlueprintButton variant="ghost" size="sm">
              <FileText size={14} />
              Documents
            </BlueprintButton>
            <BlueprintButton variant="ghost" size="sm">
              <HelpCircle size={14} />
              Help
            </BlueprintButton>
          </div>
        </div>
      </BlueprintCard>

      <BlueprintCard figure="NAV" code="TEST-07" padding="lg">
        <h3 className="font-serif text-xl text-[var(--ink)] mb-4">Action Buttons</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <BlueprintButton size="sm">
            <Plus size={14} />
            New
          </BlueprintButton>
          <BlueprintButton size="sm" variant="secondary">
            <Edit size={14} />
            Edit
          </BlueprintButton>
          <BlueprintButton size="sm" variant="ghost">
            <Trash2 size={14} />
            Delete
          </BlueprintButton>
          <BlueprintButton size="sm" variant="ghost">
            <Download size={14} />
            Export
          </BlueprintButton>
        </div>
      </BlueprintCard>
    </div>
  );

  const renderStates = () => (
    <div className="space-y-8">
      <BlueprintCard figure="STATE" code="TEST-08" padding="lg">
        <h3 className="font-serif text-xl text-[var(--ink)] mb-4">Loading States</h3>
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <BlueprintLoader size="sm" />
            <span className="text-sm text-[var(--ink-secondary)]">Small loader</span>
          </div>
          <div className="flex items-center gap-4">
            <BlueprintLoader size="md" />
            <span className="text-sm text-[var(--ink-secondary)]">Medium loader</span>
          </div>
          <div className="flex items-center gap-4">
            <BlueprintLoader size="lg" />
            <span className="text-sm text-[var(--ink-secondary)]">Large loader</span>
          </div>
          <div className="space-y-2">
            <BlueprintLoader variant="skeleton" />
            <BlueprintLoader variant="pulse" />
          </div>
        </div>
      </BlueprintCard>

      <BlueprintCard figure="STATE" code="TEST-09" padding="lg">
        <h3 className="font-serif text-xl text-[var(--ink)] mb-4">Empty States</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <BlueprintEmptyState
            title="No Data"
            description="There's nothing to show here yet"
            code="EMPTY-01"
            action={{
              label: "Add Item",
              onClick: () => {}
            }}
          />
          <BlueprintEmptyState
            title="Search Results"
            description="No results found for your search"
            code="EMPTY-02"
            variant="search"
            action={{
              label: "Clear Search",
              onClick: () => {}
            }}
          />
        </div>
      </BlueprintCard>
    </div>
  );

  const renderLayout = () => (
    <div className="space-y-8">
      <BlueprintCard figure="LAYOUT" code="TEST-10" padding="lg">
        <h3 className="font-serif text-xl text-[var(--ink)] mb-4">Grid Layouts</h3>
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <div key={i} className="bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] p-4 text-center">
                <span className="text-sm text-[var(--ink)]">Item {i}</span>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <BlueprintCard key={i} padding="md">
                <h4 className="font-semibold text-[var(--ink)]">Card {i}</h4>
                <p className="text-sm text-[var(--ink-secondary)] mt-2">Grid item content</p>
              </BlueprintCard>
            ))}
          </div>
        </div>
      </BlueprintCard>

      <BlueprintCard figure="LAYOUT" code="TEST-11" padding="lg">
        <h3 className="font-serif text-xl text-[var(--ink)] mb-4">Responsive Layout</h3>
        <div className="space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] p-4">
              <span className="text-sm text-[var(--ink)]">Main Content</span>
            </div>
            <div className="w-full md:w-64 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] p-4">
              <span className="text-sm text-[var(--ink)]">Sidebar</span>
            </div>
          </div>
        </div>
      </BlueprintCard>
    </div>
  );

  const renderContent = () => {
    switch (activeSection) {
      case "components":
        return renderComponents();
      case "forms":
        return renderForms();
      case "navigation":
        return renderNavigation();
      case "states":
        return renderStates();
      case "layout":
        return renderLayout();
      default:
        return renderComponents();
    }
  };

  return (
    <div className="min-h-screen bg-[var(--canvas)] p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="font-serif text-4xl text-[var(--ink)] mb-2">
            Blueprint UI Test Suite
          </h1>
          <p className="text-[var(--ink-secondary)]">
            Comprehensive testing for Blueprint design system components
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:w-64">
            <BlueprintCard padding="md" className="lg:sticky lg:top-8">
              <nav className="space-y-2">
                {sections.map((section) => {
                  const Icon = section.icon;
                  return (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-[var(--radius-sm)] transition-colors ${
                        activeSection === section.id
                          ? "bg-[var(--blueprint)] text-[var(--paper)]"
                          : "hover:bg-[var(--canvas)] text-[var(--ink)]"
                      }`}
                    >
                      <Icon size={16} />
                      <span className="text-sm font-medium">{section.name}</span>
                    </button>
                  );
                })}
              </nav>
            </BlueprintCard>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default BlueprintUITestSuite;

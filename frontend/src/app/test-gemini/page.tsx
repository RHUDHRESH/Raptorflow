'use client';

import React, { useState } from 'react';
import { vertexAI } from '@/lib/vertex-ai';
import { AI_CONFIG, getUniversalModel, validateModelUsage } from '@/lib/ai-config';

export default function GeminiTestPage() {
  const [prompt, setPrompt] = useState('Write a short poem about artificial intelligence');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [useDirectAPI, setUseDirectAPI] = useState(false);
  const [attemptedModel, setAttemptedModel] = useState('gemini-1.5-flash');

  const testGemini = async () => {
    setLoading(true);
    setResponse('');
    setError('');

    try {
      // Test universal model enforcement
      const validatedModel = validateModelUsage(attemptedModel);

      const result = await vertexAI.generateContent({
        prompt,
        model: attemptedModel, // This will be overridden to universal model
        temperature: 0.7,
        max_tokens: 500,
        useDirectAPI
      });

      setResponse(result.content);
      console.log('Universal Gemini Response:', result);
      console.log('Model used:', result.model);
      console.log('Universal model enforced:', result.model === getUniversalModel());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      console.error('Universal Gemini Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const testModelOverride = () => {
    // Test attempting to use different models
    const testModels = ['gpt-4', 'claude-3', 'gemini-pro', 'gemini-1.5-flash'];
    const randomModel = testModels[Math.floor(Math.random() * testModels.length)];
    setAttemptedModel(randomModel);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🚨 UNIVERSAL GEMINI 1.5 FLASH TEST 🚨</h1>
          <p className="text-lg text-gray-600">This app ONLY uses Gemini 1.5 Flash - all other models are blocked</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Test Prompt
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
              placeholder="Enter your test prompt..."
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Attempted Model (Will Be Overridden)
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={attemptedModel}
                onChange={(e) => setAttemptedModel(e.target.value)}
                className="flex-1 p-2 border border-gray-300 rounded-md"
                placeholder="Try any model name..."
              />
              <button
                onClick={testModelOverride}
                className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
              >
                Random Model
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              This will be overridden to: <code className="bg-gray-100 px-1">{getUniversalModel()}</code>
            </p>
          </div>

          <div className="mb-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={useDirectAPI}
                onChange={(e) => setUseDirectAPI(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">
                Use Direct API (requires NEXT_PUBLIC_VERTEX_AI_API_KEY in .env)
              </span>
            </label>
          </div>

          <button
            onClick={testGemini}
            disabled={loading || !prompt.trim()}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating...' : 'Test Universal Gemini 1.5 Flash'}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <h3 className="text-red-800 font-medium mb-2">❌ Error</h3>
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        {response && (
          <div className="bg-green-50 border border-green-200 rounded-md p-6 mb-6">
            <h3 className="text-green-800 font-medium mb-2">✅ Universal Gemini 1.5 Flash Response</h3>
            <div className="text-gray-700 whitespace-pre-wrap mb-4">{response}</div>
            <div className="text-xs text-gray-500">
              <p>✨ Model enforced: {getUniversalModel()}</p>
              <p>🔒 Universal configuration active</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-100 rounded-md p-4">
            <h3 className="text-gray-800 font-medium mb-2">🔧 Universal Configuration</h3>
            <div className="text-sm text-gray-600 space-y-1">
              <p><strong>Universal Model:</strong> {AI_CONFIG.MODEL}</p>
              <p><strong>Cost per Token:</strong> ${AI_CONFIG.COST_PER_TOKEN}</p>
              <p><strong>Context Window:</strong> {AI_CONFIG.MAX_CONTEXT_LENGTH.toLocaleString()} tokens</p>
              <p><strong>Enforcement:</strong> {AI_CONFIG.ENABLE_GEMINI_1_5_FLASH_ONLY ? '✅ Active' : '❌ Inactive'}</p>
            </div>
          </div>

          <div className="bg-gray-100 rounded-md p-4">
            <h3 className="text-gray-800 font-medium mb-2">🌍 Environment Check</h3>
            <div className="text-sm text-gray-600 space-y-1">
              <p>Backend URL: {process.env.NEXT_PUBLIC_API_URL || 'Not set'}</p>
              <p>Supabase URL: {process.env.NEXT_PUBLIC_SUPABASE_URL ? '✅ Set' : '❌ Not set'}</p>
              <p>Vertex AI Key: {process.env.NEXT_PUBLIC_VERTEX_AI_API_KEY ? '✅ Set' : '❌ Not set'}</p>
              <p>Universal Mode: ✅ ENFORCED</p>
            </div>
          </div>
        </div>

        <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <h3 className="text-yellow-800 font-medium mb-2">⚠️ Universal Model Enforcement</h3>
          <ul className="text-sm text-yellow-700 space-y-1">
            <li>• ALL AI requests use Gemini 1.5 Flash - NO exceptions</li>
            <li>• Any attempt to use other models will be automatically overridden</li>
            <li>• Backend enforces universal model usage</li>
            <li>• Frontend validates and corrects model selection</li>
            <li>• Configuration is runtime-enforced and cannot be bypassed</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

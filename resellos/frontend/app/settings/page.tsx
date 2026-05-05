'use client';

import { useState } from 'react';
import { Save, RefreshCw } from 'lucide-react';

export default function SettingsPage() {
  const [saving, setSaving] = useState(false);

  return (
    <div className="p-6 max-w-2xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-white">Settings</h1>
        <p className="text-sm text-[#71717a] mt-1">Configure your ResellOS preferences</p>
      </div>

      <div className="space-y-6">
        {/* Business Defaults */}
        <section className="bg-[#111111] border border-[#1a1a1a] rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white mb-4">Business Defaults</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-xs text-[#71717a] mb-1.5">Marketplace Fee %</label>
              <input
                type="number"
                defaultValue="13"
                className="w-full px-3 py-2 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-[#71717a] mb-1.5">Packaging Cost $</label>
              <input
                type="number"
                step="0.01"
                defaultValue="0.50"
                className="w-full px-3 py-2 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-[#71717a] mb-1.5">Return Allowance $</label>
              <input
                type="number"
                step="0.01"
                defaultValue="0.50"
                className="w-full px-3 py-2 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white"
              />
            </div>
          </div>
        </section>

        {/* AI Settings */}
        <section className="bg-[#111111] border border-[#1a1a1a] rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white mb-4">AI Settings</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-xs text-[#71717a] mb-1.5">LLM Provider</label>
              <select
                defaultValue="minimax"
                className="w-full px-3 py-2 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white"
              >
                <option value="minimax">MiniMax (default)</option>
                <option value="openai">OpenAI</option>
                <option value="ollama">Ollama (local)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-[#71717a] mb-1.5">Min Acceptable Profit $</label>
              <input
                type="number"
                step="0.01"
                defaultValue="3.00"
                className="w-full px-3 py-2 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white"
              />
            </div>
          </div>
        </section>

        {/* Save Button */}
        <div className="flex justify-end">
          <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors">
            {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}

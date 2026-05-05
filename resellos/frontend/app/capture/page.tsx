'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Camera, Upload, Send, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { captureManualEvidence } from '@/lib/api';
import type { CaptureType } from '@/lib/types';

const CAPTURE_TYPES: { value: CaptureType; label: string }[] = [
  { value: 'MARKETPLACE_SCREENSHOT', label: 'Marketplace screenshot' },
  { value: 'SUPPLIER_SCREENSHOT', label: 'Supplier screenshot' },
  { value: 'COMPETITOR_SCREENSHOT', label: 'Competitor screenshot' },
  { value: 'VISUAL_RISK', label: 'Visual risk' },
];

export default function CapturePage() {
  const [captureType, setCaptureType] = useState<CaptureType>('MARKETPLACE_SCREENSHOT');
  const [url, setUrl] = useState('');
  const [pastedText, setPastedText] = useState('');
  const [notes, setNotes] = useState('');
  const [screenshot, setScreenshot] = useState<File | null>(null);
  const [ideaId, setIdeaId] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ candidate: { id: string; title: string; review_status: string } } | null>(null);
  const [error, setError] = useState('');

  const handleCapture = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await captureManualEvidence({
        idea_id: ideaId || undefined,
        capture_type: captureType,
        url: url || undefined,
        pasted_text: pastedText || undefined,
        notes: notes || undefined,
        screenshot: screenshot || undefined,
      });
      setResult(res as { candidate: { id: string; title: string; review_status: string } });
      setUrl('');
      setPastedText('');
      setNotes('');
      setScreenshot(null);
    } catch (e: any) {
      setError(e.message || 'Capture failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl">
      <div className="flex items-center gap-4 mb-6">
        <Link href="/discovery" className="p-2 rounded-lg text-[#71717a] hover:text-white hover:bg-[#1a1a1a] transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-semibold text-white">Capture Evidence</h1>
          <p className="text-sm text-[#71717a] mt-0.5">Manually capture marketplace data, screenshots, or text</p>
        </div>
      </div>

      <div className="space-y-5">
        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        {result && (
          <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
            <p className="text-green-400 text-sm font-medium mb-1 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              Evidence captured successfully
            </p>
            <p className="text-[#71717a] text-xs">Candidate created. Review and approve in the Discovery page.</p>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-white mb-1.5">Idea ID (optional)</label>
          <input
            type="text"
            value={ideaId}
            onChange={(e) => setIdeaId(e.target.value)}
            placeholder="Paste a discovery idea ID to link this capture..."
            className="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white placeholder:text-[#71717a] focus:outline-none focus:border-indigo-500/50"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-1.5">Capture Type</label>
          <select
            value={captureType}
            onChange={(e) => setCaptureType(e.target.value as CaptureType)}
            className="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500/50"
          >
            {CAPTURE_TYPES.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-1.5">Source URL (optional)</label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.ebay.com/itm/..."
            className="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white placeholder:text-[#71717a] focus:outline-none focus:border-indigo-500/50"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-1.5">Screenshot (optional)</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setScreenshot(e.target.files?.[0] ?? null)}
            className="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-zinc-300 focus:outline-none focus:border-indigo-500/50 file:mr-3 file:rounded-lg file:border-0 file:bg-indigo-600/20 file:px-3 file:py-1.5 file:text-xs file:text-indigo-300"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-1.5">Pasted Text / Raw Data</label>
          <textarea
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
            placeholder="Paste listing text, competitor data, or any raw evidence here..."
            rows={6}
            className="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white placeholder:text-[#71717a] focus:outline-none focus:border-indigo-500/50 resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-1.5">Notes</label>
          <input
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Any observations, context, or risk flags..."
            className="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white placeholder:text-[#71717a] focus:outline-none focus:border-indigo-500/50"
          />
        </div>

        <button
          onClick={handleCapture}
          disabled={loading || (!url && !pastedText && !screenshot)}
          className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 text-white text-sm font-medium rounded-lg transition-colors"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Camera className="w-4 h-4" />}
          Capture Evidence
        </button>
      </div>
    </div>
  );
}

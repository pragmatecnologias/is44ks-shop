'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Camera, FileText, Upload, Send, Loader2, AlertCircle } from 'lucide-react';
import { captureManualEvidence } from '@/lib/api';

type CaptureType = 'marketplace_listing' | 'marketplace_screenshot' | 'competitor_listing' | 'supplier_screenshot' | 'manual_text';

export default function CapturePage() {
  const [captureType, setCaptureType] = useState<CaptureType>('marketplace_listing');
  const [marketplace, setMarketplace] = useState('ebay');
  const [url, setUrl] = useState('');
  const [pastedText, setPastedText] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleCapture = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await captureManualEvidence({
        capture_type: captureType,
        marketplace,
        url: url || undefined,
        pasted_text: pastedText || undefined,
        notes: notes || undefined,
      });
      setResult(res);
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
        {/* Error */}
        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
            <p className="text-green-400 text-sm font-medium mb-2">Evidence captured successfully</p>
            <p className="text-[#71717a] text-xs">Candidate created. Review and approve in the Discovery page.</p>
          </div>
        )}

        {/* Capture Type */}
        <div>
          <label className="block text-sm font-medium text-white mb-1.5">Capture Type</label>
          <select
            value={captureType}
            onChange={(e) => setCaptureType(e.target.value as CaptureType)}
            className="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500/50"
          >
            <option value="marketplace_listing">Marketplace Listing</option>
            <option value="marketplace_screenshot">Marketplace Screenshot</option>
            <option value="competitor_listing">Competitor Listing</option>
            <option value="supplier_screenshot">Supplier Screenshot</option>
            <option value="manual_text">Manual Text</option>
          </select>
        </div>

        {/* Marketplace */}
        <div>
          <label className="block text-sm font-medium text-white mb-1.5">Marketplace</label>
          <select
            value={marketplace}
            onChange={(e) => setMarketplace(e.target.value)}
            className="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500/50"
          >
            <option value="ebay">eBay</option>
            <option value="mercari">Mercari</option>
            <option value="facebook">Facebook Marketplace</option>
            <option value="amazon">Amazon</option>
            <option value="other">Other</option>
          </select>
        </div>

        {/* URL */}
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

        {/* Pasted Text */}
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

        {/* Notes */}
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

        {/* Submit */}
        <button
          onClick={handleCapture}
          disabled={loading || (!url && !pastedText)}
          className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 text-white text-sm font-medium rounded-lg transition-colors"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Camera className="w-4 h-4" />}
          Capture Evidence
        </button>
      </div>
    </div>
  );
}

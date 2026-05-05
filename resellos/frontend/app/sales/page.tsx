'use client';

import { useEffect, useState } from 'react';
import { DollarSign, Plus, RefreshCw } from 'lucide-react';

export default function SalesPage() {
  const [sales, setSales] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      setSales([]);
      setLoading(false);
    }, 500);
  }, []);

  return (
    <div className="p-6 max-w-[1400px]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-white">Sales</h1>
          <p className="text-sm text-[#71717a] mt-1">Track your sales and profits</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors">
          <Plus className="w-4 h-4" />
          Record Sale
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <RefreshCw className="w-5 h-5 animate-spin text-[#71717a]" />
        </div>
      ) : sales.length === 0 ? (
        <div className="bg-[#111111] border border-[#1a1a1a] rounded-xl p-12 text-center">
          <DollarSign className="w-12 h-12 text-[#27272a] mx-auto mb-4" />
          <h3 className="text-white font-medium mb-2">No sales yet</h3>
          <p className="text-sm text-[#71717a]">
            Sales records will appear here after you list products and make your first sale.
          </p>
        </div>
      ) : null}
    </div>
  );
}

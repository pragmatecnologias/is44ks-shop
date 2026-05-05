'use client';

import { useEffect, useState } from 'react';
import { Boxes, Plus, RefreshCw } from 'lucide-react';

export default function InventoryPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      setItems([]);
      setLoading(false);
    }, 500);
  }, []);

  return (
    <div className="p-6 max-w-[1400px]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-white">Inventory</h1>
          <p className="text-sm text-[#71717a] mt-1">Track your physical inventory</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors">
          <Plus className="w-4 h-4" />
          Add Inventory
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <RefreshCw className="w-5 h-5 animate-spin text-[#71717a]" />
        </div>
      ) : items.length === 0 ? (
        <div className="bg-[#111111] border border-[#1a1a1a] rounded-xl p-12 text-center">
          <Boxes className="w-12 h-12 text-[#27272a] mx-auto mb-4" />
          <h3 className="text-white font-medium mb-2">No inventory yet</h3>
          <p className="text-sm text-[#71717a]">
            Inventory items will appear here after you receive samples and create purchase orders.
          </p>
        </div>
      ) : null}
    </div>
  );
}

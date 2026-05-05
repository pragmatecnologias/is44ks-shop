'use client';

import { useEffect, useState } from 'react';
import { Package, Plus, RefreshCw } from 'lucide-react';

export default function ListingsPage() {
  const [listings, setListings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock data for now - would call GET /api/listings
    setTimeout(() => {
      setListings([]);
      setLoading(false);
    }, 500);
  }, []);

  return (
    <div className="p-6 max-w-[1400px]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-white">Listings</h1>
          <p className="text-sm text-[#71717a] mt-1">Manage your marketplace listings</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors">
          <Plus className="w-4 h-4" />
          New Listing
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <RefreshCw className="w-5 h-5 animate-spin text-[#71717a]" />
        </div>
      ) : listings.length === 0 ? (
        <div className="bg-[#111111] border border-[#1a1a1a] rounded-xl p-12 text-center">
          <Package className="w-12 h-12 text-[#27272a] mx-auto mb-4" />
          <h3 className="text-white font-medium mb-2">No listings yet</h3>
          <p className="text-sm text-[#71717a]">
            Listings will appear here after you approve products and generate listing content.
          </p>
        </div>
      ) : null}
    </div>
  );
}

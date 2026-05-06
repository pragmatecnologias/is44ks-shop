'use client';

import { useEffect, useState } from 'react';
import { WifiOff } from 'lucide-react';

export default function OfflineBanner() {
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
    // Check status on mount and periodically
    const checkStatus = async () => {
      try {
        const res = await fetch('/api/health', { cache: 'no-store' });
        setIsOffline(!res.ok);
      } catch {
        setIsOffline(true);
      }
    };
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  if (!isOffline) return null;

  return (
    <div className="bg-amber-900/30 border-b border-amber-700/50 px-4 py-2 flex items-center gap-2 text-amber-400 text-sm">
      <WifiOff className="w-4 h-4" />
      <span>
        <strong>Offline —</strong> Demo data is shown. Connect the backend for real data.
      </span>
    </div>
  );
}

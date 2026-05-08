import type { Metadata } from 'next';
import './globals.css';
import Link from 'next/link';
import {
  LayoutDashboard,
  Package,
  ListOrdered,
  Warehouse,
  TrendingUp,
  Settings,
  Lightbulb,
  ListChecks,
  ChevronRight,
  Zap,
  Cog,
} from 'lucide-react';
import OfflineBanner from '@/components/shared/OfflineBanner';

export const metadata: Metadata = {
  title: 'ResellOS',
  description: 'AI-Powered Reselling Command Center',
};

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/products', label: 'Products', icon: Package },
  { href: '/discovery', label: 'Product Discovery', icon: Lightbulb },
  { href: '/production', label: 'Production', icon: Cog },
  { href: '/ideas', label: 'Ideas', icon: ListChecks },
  { href: '/opportunities', label: 'Opportunities', icon: TrendingUp },
  { href: '/listings', label: 'Listings', icon: ListOrdered },
  { href: '/inventory', label: 'Inventory', icon: Warehouse },
  { href: '/sales', label: 'Sales', icon: TrendingUp },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <OfflineBanner />
        <div className="flex min-h-screen bg-[#0a0a0a]">
          {/* Sidebar */}
          <aside className="w-64 shrink-0 flex flex-col border-r border-[#1a1a1a] bg-[#0d0d0d]">
        {/* Logo */}
        <div className="flex items-center gap-2 px-5 py-5 border-b border-[#1a1a1a]">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center">
            <Zap className="w-4 h-4 text-indigo-400" />
          </div>
          <span className="text-white font-semibold text-lg tracking-tight">
            ResellOS
          </span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {navItems.map((item) => (
            <NavLink key={item.href} href={item.href} icon={item.icon} label={item.label} />
          ))}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-[#1a1a1a]">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-[#71717a]">System Operational</span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 min-w-0 overflow-auto">{children}</main>
        </div>
      </body>
    </html>
  );
}

function NavLink({
  href,
  icon: Icon,
  label,
}: {
  href: string;
  icon: React.ElementType;
  label: string;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-[#a1a1aa] hover:text-white hover:bg-[#1a1a1a] transition-colors group"
    >
      <Icon className="w-4 h-4 shrink-0" />
      <span className="flex-1">{label}</span>
      <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-50 transition-opacity" />
    </Link>
  );
}

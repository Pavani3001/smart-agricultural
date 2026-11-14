'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { NAV_LINKS } from '@/lib/constants';

const pageTitles = {
  '/': 'Dashboard',
  '/farmers': 'Farmers',
  '/fields': 'Fields',
  '/crops': 'Crops',
  '/sensors': 'Sensors',
  '/weather': 'Weather',
};

export default function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const currentPage = pageTitles[pathname] || 'Dashboard';

  const isActive = (href) => {
    if (href === '/') return pathname === '/';
    return pathname.startsWith(href);
  };

  return (
    <>
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div className="flex items-center justify-between px-4 py-3 md:px-6">
          {/* Mobile: logo + menu toggle */}
          <div className="flex items-center gap-3 md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
            <span className="text-lg">🌾</span>
          </div>

          {/* Page title + breadcrumb */}
          <div>
            <h1 className="text-lg font-bold text-slate-800 md:text-xl">{currentPage}</h1>
            <div className="hidden md:flex items-center gap-1 text-sm text-slate-500">
              <Link href="/" className="hover:text-primary-600 transition-colors">Home</Link>
              {pathname !== '/' && (
                <>
                  <span>/</span>
                  <span className="text-slate-700 font-medium">{currentPage}</span>
                </>
              )}
            </div>
          </div>

          {/* Right side: status indicator */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="hidden sm:inline">System Active</span>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile navigation drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setMobileMenuOpen(false)} />
          <div className="absolute left-0 top-0 bottom-0 w-72 bg-white shadow-xl">
            {/* Mobile logo */}
            <div className="flex items-center gap-3 px-4 py-5 border-b border-slate-100">
              <span className="text-2xl">🌾</span>
              <div>
                <h1 className="text-base font-bold text-primary-700 leading-tight">Smart Irrigation</h1>
                <p className="text-xs text-slate-500">Farm Dashboard</p>
              </div>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="ml-auto p-1 text-slate-400 hover:text-slate-600"
              >
                ✕
              </button>
            </div>

            {/* Mobile nav links */}
            <nav className="py-4 px-2 space-y-1">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`
                    flex items-center gap-3 px-3 py-3 rounded-lg text-base font-medium
                    transition-colors duration-200
                    ${isActive(link.href)
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-800'}
                  `}
                >
                  <span className="text-lg">{link.icon}</span>
                  <span>{link.label}</span>
                </Link>
              ))}
            </nav>
          </div>
        </div>
      )}
    </>
  );
}

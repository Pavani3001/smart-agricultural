import './globals.css';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';

export const metadata = {
  title: 'Smart Irrigation System — Predictive Water & Crop Management',
  description: 'AI-Powered Smart Irrigation System for Predictive Water Management and Crop Optimization (Milestone 1)',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 min-h-screen flex flex-col antialiased">
        <div className="flex flex-1 min-h-screen">
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0">
            <Header />
            <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto">
              {children}
            </main>
            <footer className="py-4 px-6 border-t border-slate-200 text-center text-xs text-slate-500 bg-white">
              AI-Powered Smart Irrigation System &bull; Milestone 1: Sensor Data Ingestion &amp; Weather API Integration
            </footer>
          </div>
        </div>
      </body>
    </html>
  );
}


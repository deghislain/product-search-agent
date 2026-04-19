import { type ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  
  // Helper function to check if link is active
  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Product Search Agent
          </h1>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            <Link 
              to="/" 
              className={`py-4 px-2 border-b-2 ${
                isActive('/') 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent hover:border-blue-500'
              }`}
            >
              Dashboard
            </Link>
            <Link 
              to="/matches" 
              className={`py-4 px-2 border-b-2 ${
                isActive('/matches') 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent hover:border-blue-500'
              }`}
            >
              Matches
            </Link>
            <Link 
              to="/settings" 
              className={`py-4 px-2 border-b-2 ${
                isActive('/settings') 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent hover:border-blue-500'
              }`}
            >
              Settings
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-4 text-center text-gray-600">
          <p>© 2026 Product Search Agent</p>
        </div>
      </footer>
    </div>
  );
}

// Made with Bob

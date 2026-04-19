import { useEffect, useState } from 'react';

interface ConnectionStatusProps {
  isConnected: boolean;
}

export function ConnectionStatus({ isConnected }: ConnectionStatusProps) {
  const [showStatus, setShowStatus] = useState(true);

  // Auto-hide after 3 seconds if connected
  useEffect(() => {
    if (isConnected) {
      const timer = setTimeout(() => setShowStatus(false), 3000);
      return () => clearTimeout(timer);
    } else {
      setShowStatus(true);
    }
  }, [isConnected]);

  if (!showStatus) return null;

  return (
    <div className={`
      fixed bottom-4 right-4 z-50 
      px-4 py-2 rounded-lg shadow-lg
      transition-all duration-300
      ${isConnected 
        ? 'bg-green-500 text-white' 
        : 'bg-red-500 text-white animate-pulse'
      }
    `}>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-white' : 'bg-white'}`} />
        <span className="text-sm font-medium">
          {isConnected ? 'Connected' : 'Reconnecting...'}
        </span>
      </div>
    </div>
  );
}
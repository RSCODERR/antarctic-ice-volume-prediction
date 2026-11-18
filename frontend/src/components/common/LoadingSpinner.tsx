import React from 'react';

export const LoadingSpinner: React.FC<{ message?: string; className?: string }> = ({
  message = 'Loading verified cryosphere telemetry...',
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-12 text-center ${className}`}>
      <div className="relative w-10 h-10 mb-4">
        <div className="absolute inset-0 rounded-full border-2 border-cryo-border border-t-cryo-cyan animate-spin" />
        <div className="absolute inset-2 rounded-full border-2 border-transparent border-b-sky-300 animate-spin animate-reverse" />
      </div>
      <p className="text-sm font-mono text-cryo-muted animate-pulse">{message}</p>
    </div>
  );
};

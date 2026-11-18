import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  title = 'Telemetry Transmission Error',
  message,
  onRetry,
  className = '',
}) => {
  return (
    <div className={`p-5 rounded-lg border border-rose-800/40 bg-rose-950/20 text-rose-200 ${className}`}>
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h4 className="text-sm font-semibold uppercase tracking-wider text-rose-300 font-mono">{title}</h4>
          <p className="text-xs text-rose-300/80 mt-1 font-mono leading-relaxed">{message}</p>
          {onRetry && (
            <div className="mt-3">
              <Button size="sm" variant="danger" onClick={onRetry} icon={<RefreshCw className="w-3.5 h-3.5" />}>
                Retry Query
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

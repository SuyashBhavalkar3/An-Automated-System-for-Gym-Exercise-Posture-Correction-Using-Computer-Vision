import { Wifi, WifiOff, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ConnectionStatus as Status } from '@/hooks/useWebSocket';

interface ConnectionStatusProps {
  status: Status;
}

export function ConnectionStatus({ status }: ConnectionStatusProps) {
  const config = {
    disconnected: {
      icon: <WifiOff className="h-4 w-4" />,
      label: 'Disconnected',
      className: 'bg-muted text-muted-foreground',
    },
    connecting: {
      icon: <Loader2 className="h-4 w-4 animate-spin" />,
      label: 'Connecting...',
      className: 'bg-warning/20 text-warning',
    },
    connected: {
      icon: <Wifi className="h-4 w-4" />,
      label: 'Connected',
      className: 'bg-success/20 text-success',
    },
    error: {
      icon: <WifiOff className="h-4 w-4" />,
      label: 'Error',
      className: 'bg-destructive/20 text-destructive',
    },
  }[status];

  return (
    <div className={cn(
      'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium',
      config.className
    )}>
      {config.icon}
      <span>{config.label}</span>
    </div>
  );
}

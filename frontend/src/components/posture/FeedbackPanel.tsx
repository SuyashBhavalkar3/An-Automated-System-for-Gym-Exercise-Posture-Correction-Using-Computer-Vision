import { CheckCircle, AlertTriangle, XCircle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { PoseResponse, ConnectionStatus } from '@/hooks/useWebSocket';

interface FeedbackPanelProps {
  feedback: PoseResponse | null;
  connectionStatus: ConnectionStatus;
  error: string | null;
}

export function FeedbackPanel({ feedback, connectionStatus, error }: FeedbackPanelProps) {
  const getStatusConfig = () => {
    if (connectionStatus === 'connecting') {
      return {
        icon: <Loader2 className="h-8 w-8 animate-spin" />,
        title: 'Connecting...',
        message: 'Establishing connection to posture detection server',
        className: 'border-muted-foreground/30 bg-muted/20',
        iconColor: 'text-muted-foreground',
      };
    }

    if (connectionStatus === 'error' || error) {
      return {
        icon: <XCircle className="h-8 w-8" />,
        title: 'Connection Error',
        message: error || 'Failed to connect to server',
        className: 'status-error border',
        iconColor: 'text-destructive',
      };
    }

    if (connectionStatus === 'disconnected') {
      return {
        icon: <AlertTriangle className="h-8 w-8" />,
        title: 'Not Connected',
        message: 'Start the session to begin posture analysis',
        className: 'border-muted-foreground/30 bg-muted/20',
        iconColor: 'text-muted-foreground',
      };
    }

    if (!feedback) {
      return {
        icon: <Loader2 className="h-8 w-8 animate-spin" />,
        title: 'Waiting for Pose',
        message: 'Position yourself in front of the camera',
        className: 'border-primary/30 bg-primary/10',
        iconColor: 'text-primary',
      };
    }

    switch (feedback.status) {
      case 'ok':
        return {
          icon: <CheckCircle className="h-8 w-8" />,
          title: 'Great Form!',
          message: feedback.feedback,
          className: 'status-ok border',
          iconColor: 'text-success',
        };
      case 'no_pose':
        return {
          icon: <AlertTriangle className="h-8 w-8" />,
          title: 'No Pose Detected',
          message: feedback.feedback || 'Make sure your full body is visible',
          className: 'status-warning border',
          iconColor: 'text-warning',
        };
      case 'incorrect':
        return {
          icon: <XCircle className="h-8 w-8" />,
          title: 'Form Needs Adjustment',
          message: feedback.feedback,
          className: 'status-error border',
          iconColor: 'text-destructive',
        };
      default:
        return {
          icon: <AlertTriangle className="h-8 w-8" />,
          title: 'Unknown Status',
          message: 'Unable to determine posture status',
          className: 'border-muted-foreground/30 bg-muted/20',
          iconColor: 'text-muted-foreground',
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className={cn(
      'rounded-xl p-6 transition-all duration-300',
      config.className
    )}>
      <div className="flex items-start gap-4">
        <div className={cn('flex-shrink-0', config.iconColor)}>
          {config.icon}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-lg text-foreground mb-1">
            {config.title}
          </h3>
          <p className="text-muted-foreground">
            {config.message}
          </p>
          {feedback?.confidence !== undefined && (
            <div className="mt-3">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-muted-foreground">Confidence</span>
                <span className="font-medium">{Math.round(feedback.confidence * 100)}%</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary rounded-full transition-all duration-300"
                  style={{ width: `${feedback.confidence * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

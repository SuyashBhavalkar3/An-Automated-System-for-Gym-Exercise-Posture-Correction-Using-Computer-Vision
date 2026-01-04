import { useState, useCallback } from 'react';
import { Play, Square, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Navbar } from '@/components/layout/Navbar';
import { CameraFeed } from '@/components/posture/CameraFeed';
import { ExerciseSelector, ExerciseType } from '@/components/posture/ExerciseSelector';
import { FeedbackPanel } from '@/components/posture/FeedbackPanel';
import { ConnectionStatus } from '@/components/posture/ConnectionStatus';
import { useWebSocket } from '@/hooks/useWebSocket';

export default function DashboardPage() {
  const [selectedExercise, setSelectedExercise] = useState<ExerciseType>('bicep_curl');
  const [isSessionActive, setIsSessionActive] = useState(false);
  
  const { status, feedback, connect, disconnect, sendFrame, error } = useWebSocket();

  const handleStartSession = () => {
    connect();
    setIsSessionActive(true);
  };

  const handleStopSession = () => {
    disconnect();
    setIsSessionActive(false);
  };

  const handleFrame = useCallback((base64Image: string) => {
    sendFrame(base64Image, selectedExercise);
  }, [sendFrame, selectedExercise]);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="container py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              Live Posture Detection
            </h1>
            <p className="text-muted-foreground mt-1">
              Get real-time feedback on your exercise form
            </p>
          </div>
          <div className="flex items-center gap-3">
            <ConnectionStatus status={status} />
            {!isSessionActive ? (
              <Button onClick={handleStartSession} variant="glow" size="lg">
                <Play className="mr-2 h-5 w-5" />
                Start Session
              </Button>
            ) : (
              <Button onClick={handleStopSession} variant="destructive" size="lg">
                <Square className="mr-2 h-5 w-5" />
                Stop Session
              </Button>
            )}
          </div>
        </div>

        {/* Main content grid */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Camera feed - takes 2 columns */}
          <div className="lg:col-span-2 space-y-6">
            <CameraFeed
              onFrame={handleFrame}
              isCapturing={isSessionActive && status === 'connected'}
            />
            
            {/* Feedback panel below camera */}
            <FeedbackPanel
              feedback={feedback}
              connectionStatus={status}
              error={error}
            />
          </div>

          {/* Sidebar - exercise selection */}
          <div className="space-y-6">
            <div className="glass-card rounded-xl p-6">
              <ExerciseSelector
                selected={selectedExercise}
                onSelect={setSelectedExercise}
                disabled={isSessionActive}
              />
            </div>

            {/* Tips card */}
            <div className="glass-card rounded-xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Settings className="h-5 w-5 text-primary" />
                <h3 className="font-semibold">Quick Tips</h3>
              </div>
              <ul className="space-y-3 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                  Position camera at chest height for best results
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                  Ensure good lighting on your body
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                  Wear fitted clothing for accurate detection
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                  Stand 3-6 feet from the camera
                </li>
              </ul>
            </div>

            {/* Stats card */}
            <div className="glass-card rounded-xl p-6">
              <h3 className="font-semibold mb-4">Session Info</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-secondary/50 rounded-lg">
                  <p className="text-2xl font-bold text-primary">
                    {selectedExercise.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase()).join('')}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">Exercise</p>
                </div>
                <div className="text-center p-3 bg-secondary/50 rounded-lg">
                  <p className="text-2xl font-bold text-foreground">
                    {isSessionActive ? 'Active' : 'Idle'}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">Status</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

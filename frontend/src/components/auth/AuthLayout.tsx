import { ReactNode } from 'react';
import { Activity } from 'lucide-react';

interface AuthLayoutProps {
  children: ReactNode;
  title: string;
  subtitle: string;
}

export function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-secondary via-background to-card">
        {/* Background glow effect */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_hsl(174_72%_56%_/_0.15)_0%,_transparent_70%)]" />
        
        <div className="relative z-10 flex flex-col justify-center px-16">
          <div className="flex items-center gap-3 mb-8">
            <div className="p-3 rounded-xl bg-primary/20 glow-primary">
              <Activity className="h-8 w-8 text-primary" />
            </div>
            <span className="text-2xl font-bold gradient-text">PostureAI</span>
          </div>
          
          <h1 className="text-4xl font-bold mb-4 text-foreground">
            Perfect Your Form with
            <span className="gradient-text block">AI-Powered Feedback</span>
          </h1>
          
          <p className="text-muted-foreground text-lg max-w-md">
            Get real-time posture correction and form analysis for your workouts. 
            Train smarter, prevent injuries, and maximize your results.
          </p>

          <div className="mt-12 grid grid-cols-3 gap-6">
            {['Real-time Analysis', 'Multiple Exercises', 'Smart Feedback'].map((feature) => (
              <div key={feature} className="text-center">
                <div className="w-12 h-12 mx-auto mb-2 rounded-lg bg-primary/10 flex items-center justify-center">
                  <div className="w-3 h-3 rounded-full bg-primary" />
                </div>
                <p className="text-sm text-muted-foreground">{feature}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right side - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-2 mb-8 justify-center">
            <div className="p-2 rounded-lg bg-primary/20">
              <Activity className="h-6 w-6 text-primary" />
            </div>
            <span className="text-xl font-bold gradient-text">PostureAI</span>
          </div>

          <div className="glass-card rounded-2xl p-8 animate-fade-in">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-foreground">{title}</h2>
              <p className="text-muted-foreground mt-2">{subtitle}</p>
            </div>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

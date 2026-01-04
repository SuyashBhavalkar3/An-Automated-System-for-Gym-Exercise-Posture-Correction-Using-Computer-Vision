import { Dumbbell, ArrowDown, ArrowUp, Repeat, Weight, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

export type ExerciseType = 'bicep_curl' | 'squat' | 'pushup' | 'lunge' | 'deadlift' | 'shoulder_press';

interface Exercise {
  id: ExerciseType;
  name: string;
  icon: React.ReactNode;
  description: string;
}

const exercises: Exercise[] = [
  {
    id: 'bicep_curl',
    name: 'Bicep Curl',
    icon: <Dumbbell className="h-5 w-5" />,
    description: 'Arm curling motion',
  },
  {
    id: 'squat',
    name: 'Squat',
    icon: <ArrowDown className="h-5 w-5" />,
    description: 'Lower body compound',
  },
  {
    id: 'pushup',
    name: 'Push Up',
    icon: <ArrowUp className="h-5 w-5" />,
    description: 'Upper body press',
  },
  {
    id: 'lunge',
    name: 'Lunge',
    icon: <Repeat className="h-5 w-5" />,
    description: 'Single leg movement',
  },
  {
    id: 'deadlift',
    name: 'Deadlift',
    icon: <Weight className="h-5 w-5" />,
    description: 'Hip hinge pattern',
  },
  {
    id: 'shoulder_press',
    name: 'Shoulder Press',
    icon: <Sparkles className="h-5 w-5" />,
    description: 'Overhead pressing',
  },
];

interface ExerciseSelectorProps {
  selected: ExerciseType;
  onSelect: (exercise: ExerciseType) => void;
  disabled?: boolean;
}

export function ExerciseSelector({ selected, onSelect, disabled }: ExerciseSelectorProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
        Select Exercise
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {exercises.map((exercise) => (
          <button
            key={exercise.id}
            onClick={() => onSelect(exercise.id)}
            disabled={disabled}
            className={cn(
              'group relative p-4 rounded-xl border transition-all duration-200 text-left',
              'hover:border-primary/50 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background',
              selected === exercise.id
                ? 'border-primary bg-primary/10 shadow-lg glow-primary'
                : 'border-border bg-card hover:bg-card/80',
              disabled && 'opacity-50 cursor-not-allowed'
            )}
          >
            <div className={cn(
              'flex items-center gap-3 mb-2',
              selected === exercise.id ? 'text-primary' : 'text-foreground'
            )}>
              {exercise.icon}
              <span className="font-medium">{exercise.name}</span>
            </div>
            <p className="text-xs text-muted-foreground">{exercise.description}</p>
            
            {selected === exercise.id && (
              <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary animate-pulse" />
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

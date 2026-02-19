import { useState } from 'react';
import { GameMode, api } from '@/services/api';
import { useSnakeGame } from '@/hooks/useSnakeGame';
import { useAuth } from '@/hooks/useAuth';
import { GameBoard } from './GameBoard';
import { Button } from '@/components/ui/button';
import { Trophy, RotateCcw, Play, Pause } from 'lucide-react';

interface SnakeGameProps {
  onBack: () => void;
}

export function SnakeGame({ onBack }: SnakeGameProps) {
  const [mode, setMode] = useState<GameMode>('pass-through');
  const [gameStarted, setGameStarted] = useState(false);
  const [lastScore, setLastScore] = useState<number | null>(null);
  const { user } = useAuth();

  const { gameState, resetGame, togglePause, startGame } = useSnakeGame({
    mode,
    onGameOver: async (score) => {
      setLastScore(score);
      if (user) {
        try {
          await api.leaderboard.submitScore(score, mode);
        } catch { /* ignore */ }
      }
    },
  });

  const handleStart = () => {
    setGameStarted(true);
    setLastScore(null);
    resetGame();
    startGame();
  };

  const handleModeSelect = (m: GameMode) => {
    setMode(m);
    setGameStarted(false);
    setLastScore(null);
  };

  return (
    <div className="flex flex-col items-center gap-6">
      {/* Mode selector */}
      <div className="flex gap-3">
        <button
          onClick={() => handleModeSelect('pass-through')}
          className={`px-4 py-2 rounded-md font-pixel text-xs transition-all ${
            mode === 'pass-through'
              ? 'bg-primary text-primary-foreground neon-glow'
              : 'bg-muted text-muted-foreground hover:text-foreground'
          }`}
        >
          PASS-THROUGH
        </button>
        <button
          onClick={() => handleModeSelect('walls')}
          className={`px-4 py-2 rounded-md font-pixel text-xs transition-all ${
            mode === 'walls'
              ? 'bg-destructive text-destructive-foreground'
              : 'bg-muted text-muted-foreground hover:text-foreground'
          }`}
          style={mode === 'walls' ? { boxShadow: '0 0 15px hsl(0 80% 55% / 0.4)' } : undefined}
        >
          WALLS
        </button>
      </div>

      {/* Score */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Trophy className="w-4 h-4 text-accent" />
          <span className="font-pixel text-sm text-foreground neon-text">{gameState.score}</span>
        </div>
        <span className="text-xs text-muted-foreground font-mono">
          {mode === 'pass-through' ? '∞ No walls' : '⚠ Hit wall = death'}
        </span>
      </div>

      {/* Game Board */}
      <div className="relative">
        <GameBoard gameState={gameState} />

        {/* Overlays */}
        {!gameStarted && !gameState.isGameOver && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/80 rounded-sm">
            <h2 className="font-pixel text-lg text-primary neon-text mb-4">SNAKE</h2>
            <p className="text-muted-foreground text-sm mb-6 font-mono">
              {mode === 'pass-through' ? 'Walls wrap around' : 'Avoid the walls!'}
            </p>
            <Button onClick={handleStart} className="font-pixel text-xs gap-2">
              <Play className="w-4 h-4" /> START
            </Button>
          </div>
        )}

        {gameState.isGameOver && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/85 rounded-sm">
            <h2 className="font-pixel text-lg text-destructive mb-2">GAME OVER</h2>
            <p className="font-pixel text-sm text-foreground neon-text mb-1">SCORE: {gameState.score}</p>
            {lastScore !== null && user && (
              <p className="text-xs text-muted-foreground mb-4 font-mono">Score submitted!</p>
            )}
            {lastScore !== null && !user && (
              <p className="text-xs text-accent mb-4 font-mono">Log in to save your score</p>
            )}
            <Button onClick={handleStart} className="font-pixel text-xs gap-2">
              <RotateCcw className="w-4 h-4" /> RETRY
            </Button>
          </div>
        )}

        {gameState.isPaused && gameStarted && !gameState.isGameOver && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/80 rounded-sm">
            <h2 className="font-pixel text-lg text-secondary neon-text mb-4">PAUSED</h2>
            <Button onClick={togglePause} variant="outline" className="font-pixel text-xs gap-2">
              <Play className="w-4 h-4" /> RESUME
            </Button>
          </div>
        )}
      </div>

      {/* Controls hint */}
      {gameStarted && !gameState.isGameOver && (
        <div className="flex gap-4 text-xs text-muted-foreground font-mono">
          <span>↑↓←→ or WASD to move</span>
          <span>SPACE to pause</span>
          <button onClick={togglePause} className="hover:text-foreground transition-colors">
            {gameState.isPaused ? <Play className="w-3 h-3 inline" /> : <Pause className="w-3 h-3 inline" />}
          </button>
        </div>
      )}

      <Button variant="ghost" onClick={onBack} className="text-muted-foreground font-mono text-xs">
        ← Back to menu
      </Button>
    </div>
  );
}

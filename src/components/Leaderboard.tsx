import { useState, useEffect } from 'react';
import { api, LeaderboardEntry, GameMode } from '@/services/api';
import { Trophy, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface LeaderboardProps {
  onBack: () => void;
}

export function Leaderboard({ onBack }: LeaderboardProps) {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [filterMode, setFilterMode] = useState<GameMode | 'all'>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.leaderboard
      .getAll(filterMode === 'all' ? undefined : filterMode)
      .then(setEntries)
      .finally(() => setLoading(false));
  }, [filterMode]);

  return (
    <div className="w-full max-w-lg mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Trophy className="w-6 h-6 text-accent" />
        <h2 className="font-pixel text-lg text-foreground neon-text">LEADERBOARD</h2>
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-6">
        {(['all', 'pass-through', 'walls'] as const).map(m => (
          <button
            key={m}
            onClick={() => setFilterMode(m)}
            className={`px-3 py-1.5 rounded-md font-mono text-xs transition-all ${
              filterMode === m
                ? 'bg-primary text-primary-foreground neon-glow'
                : 'bg-muted text-muted-foreground hover:text-foreground'
            }`}
          >
            {m === 'all' ? 'ALL' : m.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="border border-border rounded-md overflow-hidden">
        <div className="grid grid-cols-[40px_1fr_80px_100px] gap-2 px-4 py-2 bg-muted/50 text-xs text-muted-foreground font-mono">
          <span>#</span>
          <span>PLAYER</span>
          <span>SCORE</span>
          <span>MODE</span>
        </div>
        {loading ? (
          <div className="px-4 py-8 text-center text-muted-foreground font-mono text-sm">Loading...</div>
        ) : (
          entries.map((entry, i) => (
            <div
              key={entry.id}
              className={`grid grid-cols-[40px_1fr_80px_100px] gap-2 px-4 py-3 border-t border-border/50 text-sm font-mono transition-colors hover:bg-muted/30 ${
                i < 3 ? 'text-foreground' : 'text-muted-foreground'
              }`}
            >
              <span className={i === 0 ? 'text-accent neon-text-accent font-bold' : i < 3 ? 'text-primary' : ''}>
                {i + 1}
              </span>
              <span className={i === 0 ? 'text-accent' : ''}>{entry.username}</span>
              <span className="text-foreground neon-text">{entry.score}</span>
              <span className={`text-xs ${entry.mode === 'walls' ? 'text-destructive' : 'text-secondary'}`}>
                {entry.mode === 'walls' ? '⚠ WALLS' : '∞ PASS'}
              </span>
            </div>
          ))
        )}
      </div>

      <Button variant="ghost" onClick={onBack} className="mt-6 text-muted-foreground font-mono text-xs gap-2">
        <ArrowLeft className="w-3 h-3" /> Back to menu
      </Button>
    </div>
  );
}

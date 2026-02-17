import { useState, useEffect } from 'react';
import { api, LiveGame } from '@/services/api';
import { useSnakeGame } from '@/hooks/useSnakeGame';
import { GameBoard } from './GameBoard';
import { Button } from '@/components/ui/button';
import { Eye, ArrowLeft, Radio } from 'lucide-react';

interface WatchGameProps {
  onBack: () => void;
}

export function WatchGame({ onBack }: WatchGameProps) {
  const [liveGames, setLiveGames] = useState<LiveGame[]>([]);
  const [selectedGame, setSelectedGame] = useState<LiveGame | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.liveGames.getAll().then(games => {
      setLiveGames(games);
      setLoading(false);
    });
  }, []);

  if (selectedGame) {
    return <WatchGameView game={selectedGame} onBack={() => setSelectedGame(null)} />;
  }

  return (
    <div className="w-full max-w-lg mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Eye className="w-6 h-6 text-secondary" />
        <h2 className="font-pixel text-lg text-foreground neon-text">LIVE GAMES</h2>
        <Radio className="w-4 h-4 text-destructive animate-pulse-neon" />
      </div>

      {loading ? (
        <div className="text-center text-muted-foreground font-mono py-8">Loading...</div>
      ) : liveGames.length === 0 ? (
        <div className="text-center text-muted-foreground font-mono py-8">No live games right now</div>
      ) : (
        <div className="space-y-3">
          {liveGames.map(game => (
            <button
              key={game.id}
              onClick={() => setSelectedGame(game)}
              className="w-full flex items-center justify-between p-4 rounded-md border border-border bg-card hover:bg-muted/30 transition-all group"
            >
              <div className="flex items-center gap-3">
                <Radio className="w-3 h-3 text-destructive animate-pulse-neon" />
                <span className="font-mono text-sm text-foreground">{game.username}</span>
                <span className={`text-xs px-2 py-0.5 rounded ${
                  game.mode === 'walls' ? 'bg-destructive/20 text-destructive' : 'bg-secondary/20 text-secondary'
                }`}>
                  {game.mode === 'walls' ? 'WALLS' : 'PASS-THROUGH'}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-pixel text-xs text-foreground">{game.score}</span>
                <Eye className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
              </div>
            </button>
          ))}
        </div>
      )}

      <Button variant="ghost" onClick={onBack} className="mt-6 text-muted-foreground font-mono text-xs gap-2">
        <ArrowLeft className="w-3 h-3" /> Back to menu
      </Button>
    </div>
  );
}

function WatchGameView({ game, onBack }: { game: LiveGame; onBack: () => void }) {
  const { gameState, resetGame } = useSnakeGame({
    mode: game.mode,
    autoPlay: true,
    onGameOver: () => {
      // Auto-restart after 2 seconds
      setTimeout(resetGame, 2000);
    },
  });

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="flex items-center gap-3">
        <Radio className="w-3 h-3 text-destructive animate-pulse-neon" />
        <span className="font-pixel text-sm text-foreground">{game.username}</span>
        <span className={`text-xs px-2 py-0.5 rounded ${
          game.mode === 'walls' ? 'bg-destructive/20 text-destructive' : 'bg-secondary/20 text-secondary'
        }`}>
          {game.mode.toUpperCase()}
        </span>
      </div>

      <div className="font-pixel text-lg text-foreground neon-text">{gameState.score}</div>

      <GameBoard gameState={gameState} />

      {gameState.isGameOver && (
        <p className="font-mono text-xs text-muted-foreground">Restarting...</p>
      )}

      <Button variant="ghost" onClick={onBack} className="text-muted-foreground font-mono text-xs gap-2">
        <ArrowLeft className="w-3 h-3" /> Back to live games
      </Button>
    </div>
  );
}

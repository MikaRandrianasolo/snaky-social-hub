import { useState } from 'react';
import { Header } from '@/components/Header';
import { SnakeGame } from '@/components/SnakeGame';
import { Leaderboard } from '@/components/Leaderboard';
import { WatchGame } from '@/components/WatchGame';
import { Gamepad2, Trophy, Eye } from 'lucide-react';

type View = 'menu' | 'play' | 'leaderboard' | 'watch';

const Index = () => {
  const [view, setView] = useState<View>('menu');

  return (
    <div className="min-h-screen bg-background scanline">
      <Header />
      <main className="pt-20 pb-12 px-4 flex flex-col items-center">
        {view === 'menu' && (
          <div className="flex flex-col items-center gap-8 mt-16">
            <div className="text-center">
              <h1 className="font-pixel text-3xl text-primary neon-text mb-3">SNAKE</h1>
              <p className="font-pixel text-xs text-accent neon-text-accent">ARENA</p>
            </div>

            <div className="flex flex-col gap-3 w-64">
              <MenuButton icon={<Gamepad2 className="w-5 h-5" />} label="PLAY" onClick={() => setView('play')} />
              <MenuButton icon={<Trophy className="w-5 h-5" />} label="LEADERBOARD" onClick={() => setView('leaderboard')} />
              <MenuButton icon={<Eye className="w-5 h-5" />} label="WATCH LIVE" onClick={() => setView('watch')} />
            </div>

            <div className="mt-8 text-center">
              <p className="font-mono text-xs text-muted-foreground">Two modes: <span className="text-secondary">Pass-Through</span> or <span className="text-destructive">Walls</span></p>
              <p className="font-mono text-xs text-muted-foreground mt-1">Log in to save scores & compete</p>
            </div>
          </div>
        )}

        {view === 'play' && <SnakeGame onBack={() => setView('menu')} />}
        {view === 'leaderboard' && <Leaderboard onBack={() => setView('menu')} />}
        {view === 'watch' && <WatchGame onBack={() => setView('menu')} />}
      </main>
    </div>
  );
};

function MenuButton({ icon, label, onClick }: { icon: React.ReactNode; label: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-3 px-6 py-4 rounded-md border border-border bg-card hover:bg-muted/30 hover:border-primary/50 hover:neon-glow transition-all group"
    >
      <span className="text-primary group-hover:text-primary">{icon}</span>
      <span className="font-pixel text-xs text-foreground">{label}</span>
    </button>
  );
}

export default Index;

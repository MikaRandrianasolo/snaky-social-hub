import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { AuthModal } from './AuthModal';
import { Button } from '@/components/ui/button';
import { User, LogOut } from 'lucide-react';

export function Header() {
  const { user, logout } = useAuth();
  const [showAuth, setShowAuth] = useState(false);

  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-40 flex items-center justify-between px-6 py-3 border-b border-border bg-background/90 backdrop-blur-sm">
        <h1 className="font-pixel text-sm text-primary neon-text">🐍 SNAKE ARENA</h1>

        <div className="flex items-center gap-3">
          {user ? (
            <>
              <span className="font-mono text-xs text-foreground flex items-center gap-1.5">
                <User className="w-3 h-3 text-primary" />
                {user.username}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={logout}
                className="text-muted-foreground hover:text-foreground font-mono text-xs gap-1"
              >
                <LogOut className="w-3 h-3" /> Logout
              </Button>
            </>
          ) : (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAuth(true)}
              className="font-pixel text-xs border-primary/40 hover:border-primary hover:neon-glow"
            >
              LOG IN
            </Button>
          )}
        </div>
      </header>
      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  );
}

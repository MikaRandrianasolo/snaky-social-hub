import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { X } from 'lucide-react';

interface AuthModalProps {
  onClose: () => void;
}

export function AuthModal({ onClose }: AuthModalProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, signup } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isLogin) {
        await login(email, password);
      } else {
        if (!username.trim()) { setError('Username is required'); setLoading(false); return; }
        await signup(username, email, password);
      }
      onClose();
    } catch (err: any) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm" onClick={onClose}>
      <div
        className="w-full max-w-sm p-6 rounded-lg border border-border bg-card neon-glow"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-pixel text-sm text-foreground neon-text">
            {isLogin ? 'LOG IN' : 'SIGN UP'}
          </h2>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="font-mono text-xs text-muted-foreground mb-1 block">Username</label>
              <Input
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder="PixelViper"
                className="font-mono bg-muted border-border"
              />
            </div>
          )}
          <div>
            <label className="font-mono text-xs text-muted-foreground mb-1 block">Email</label>
            <Input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="snake@arcade.com"
              className="font-mono bg-muted border-border"
              required
            />
          </div>
          <div>
            <label className="font-mono text-xs text-muted-foreground mb-1 block">Password</label>
            <Input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              className="font-mono bg-muted border-border"
              required
            />
          </div>

          {error && <p className="text-destructive text-xs font-mono">{error}</p>}

          <Button type="submit" className="w-full font-pixel text-xs" disabled={loading}>
            {loading ? 'LOADING...' : isLogin ? 'LOG IN' : 'SIGN UP'}
          </Button>
        </form>

        <button
          onClick={() => { setIsLogin(!isLogin); setError(''); }}
          className="mt-4 w-full text-center text-xs text-muted-foreground hover:text-foreground font-mono transition-colors"
        >
          {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Log in'}
        </button>
      </div>
    </div>
  );
}

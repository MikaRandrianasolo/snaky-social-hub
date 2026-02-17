// Centralized mock API service - all backend calls go through here
// Replace these with real API calls when backend is ready

export interface User {
  id: string;
  username: string;
  email: string;
}

export interface LeaderboardEntry {
  id: string;
  username: string;
  score: number;
  mode: GameMode;
  date: string;
}

export interface LiveGame {
  id: string;
  username: string;
  score: number;
  mode: GameMode;
  startedAt: string;
}

export type GameMode = 'pass-through' | 'walls';

// Simulated delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Mock data store
let currentUser: User | null = null;
const users: Map<string, User & { password: string }> = new Map();

const mockLeaderboard: LeaderboardEntry[] = [
  { id: '1', username: 'PixelViper', score: 2450, mode: 'walls', date: '2026-02-17' },
  { id: '2', username: 'NeonByte', score: 2100, mode: 'pass-through', date: '2026-02-16' },
  { id: '3', username: 'RetroGlitch', score: 1890, mode: 'walls', date: '2026-02-17' },
  { id: '4', username: 'CyberSnake', score: 1750, mode: 'pass-through', date: '2026-02-15' },
  { id: '5', username: 'ArcadeKing', score: 1620, mode: 'walls', date: '2026-02-16' },
  { id: '6', username: 'GlowWorm', score: 1500, mode: 'pass-through', date: '2026-02-14' },
  { id: '7', username: 'BitCrusher', score: 1380, mode: 'walls', date: '2026-02-17' },
  { id: '8', username: 'SnakeEyes', score: 1200, mode: 'pass-through', date: '2026-02-13' },
  { id: '9', username: 'VoidRunner', score: 1050, mode: 'walls', date: '2026-02-16' },
  { id: '10', username: 'PhosphorGlow', score: 900, mode: 'pass-through', date: '2026-02-15' },
];

const mockLiveGames: LiveGame[] = [
  { id: 'live1', username: 'PixelViper', score: 340, mode: 'walls', startedAt: '2026-02-17T14:30:00Z' },
  { id: 'live2', username: 'NeonByte', score: 120, mode: 'pass-through', startedAt: '2026-02-17T14:45:00Z' },
  { id: 'live3', username: 'RetroGlitch', score: 560, mode: 'walls', startedAt: '2026-02-17T14:20:00Z' },
];

// Auth API
export const api = {
  auth: {
    async login(email: string, password: string): Promise<User> {
      await delay(500);
      const user = Array.from(users.values()).find(u => u.email === email && u.password === password);
      if (!user) throw new Error('Invalid email or password');
      const { password: _, ...userData } = user;
      currentUser = userData;
      return userData;
    },

    async signup(username: string, email: string, password: string): Promise<User> {
      await delay(500);
      if (Array.from(users.values()).some(u => u.email === email)) {
        throw new Error('Email already exists');
      }
      const id = crypto.randomUUID();
      const user = { id, username, email, password };
      users.set(id, user);
      const { password: _, ...userData } = user;
      currentUser = userData;
      return userData;
    },

    async logout(): Promise<void> {
      await delay(200);
      currentUser = null;
    },

    async getCurrentUser(): Promise<User | null> {
      await delay(100);
      return currentUser;
    },
  },

  leaderboard: {
    async getAll(mode?: GameMode): Promise<LeaderboardEntry[]> {
      await delay(300);
      const entries = mode ? mockLeaderboard.filter(e => e.mode === mode) : mockLeaderboard;
      return [...entries].sort((a, b) => b.score - a.score);
    },

    async submitScore(score: number, mode: GameMode): Promise<LeaderboardEntry> {
      await delay(300);
      if (!currentUser) throw new Error('Must be logged in to submit score');
      const entry: LeaderboardEntry = {
        id: crypto.randomUUID(),
        username: currentUser.username,
        score,
        mode,
        date: new Date().toISOString().split('T')[0],
      };
      mockLeaderboard.push(entry);
      return entry;
    },
  },

  liveGames: {
    async getAll(): Promise<LiveGame[]> {
      await delay(300);
      return [...mockLiveGames];
    },

    async getById(id: string): Promise<LiveGame | null> {
      await delay(200);
      return mockLiveGames.find(g => g.id === id) || null;
    },
  },
};

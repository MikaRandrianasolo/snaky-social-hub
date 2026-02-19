import { describe, it, expect, beforeEach } from 'vitest';
import { api } from '@/services/api';

// Generate unique test emails to avoid conflicts between test runs
const generateTestEmail = (prefix: string) => {
  const timestamp = Date.now();
  const random = Math.random().toString(36).slice(2, 8);
  return `${prefix}${timestamp}${random}@test.com`;
};

describe('api.auth', () => {
  it('signs up a new user', async () => {
    const email = generateTestEmail('newuser');
    const user = await api.auth.signup('TestUser', email, 'password123');
    expect(user.username).toBe('TestUser');
    expect(user.email).toBe(email);
    expect(user.id).toBeDefined();
  });

  it('logs in with valid credentials', async () => {
    const email = generateTestEmail('login');
    await api.auth.signup('LoginTest', email, 'pass123');
    await api.auth.logout();
    const user = await api.auth.login(email, 'pass123');
    expect(user.username).toBe('LoginTest');
  });

  it('rejects invalid login', async () => {
    const email = generateTestEmail('nonexistent');
    await expect(api.auth.login(email, 'wrong')).rejects.toThrow('Invalid email or password');
  });

  it('rejects duplicate email signup', async () => {
    const email = generateTestEmail('dup');
    await api.auth.signup('Dup1', email, 'pass123');
    await expect(api.auth.signup('Dup2', email, 'pass123')).rejects.toThrow('Email already exists');
  });

  it('logs out correctly', async () => {
    const email = generateTestEmail('logout');
    await api.auth.signup('LogoutUser', email, 'pass123');
    await api.auth.login(email, 'pass123');
    await api.auth.logout();
    const user = await api.auth.getCurrentUser();
    expect(user).toBeNull();
  });

  it('returns current user after login', async () => {
    const email = generateTestEmail('current');
    await api.auth.signup('CurrentUser', email, 'pass123');
    await api.auth.login(email, 'pass123');
    const user = await api.auth.getCurrentUser();
    expect(user?.username).toBe('CurrentUser');
    await api.auth.logout();
  });
});

describe('api.leaderboard', () => {
  it('returns sorted leaderboard entries', async () => {
    const entries = await api.leaderboard.getAll();
    expect(entries.length).toBeGreaterThan(0);
    for (let i = 1; i < entries.length; i++) {
      expect(entries[i - 1].score).toBeGreaterThanOrEqual(entries[i].score);
    }
  });

  it('filters by mode', async () => {
    const wallsEntries = await api.leaderboard.getAll('walls');
    wallsEntries.forEach(e => expect(e.mode).toBe('walls'));

    const passEntries = await api.leaderboard.getAll('pass-through');
    passEntries.forEach(e => expect(e.mode).toBe('pass-through'));
  });

  it('submits score when logged in', async () => {
    const email = generateTestEmail('scorer');
    await api.auth.signup('Scorer', email, 'pass123');
    await api.auth.login(email, 'pass123');
    const entry = await api.leaderboard.submitScore(999, 'walls');
    expect(entry.score).toBe(999);
    expect(entry.mode).toBe('walls');
    expect(entry.username).toBe('Scorer');
    await api.auth.logout();
  });

  it('rejects score submission when not logged in', async () => {
    await api.auth.logout();
    await expect(api.leaderboard.submitScore(100, 'walls')).rejects.toThrow('No credentials provided');
  });
});

describe('api.liveGames', () => {
  it('returns list of live games', async () => {
    const games = await api.liveGames.getAll();
    expect(games.length).toBeGreaterThan(0);
    games.forEach(g => {
      expect(g.id).toBeDefined();
      expect(g.username).toBeDefined();
      expect(['pass-through', 'walls']).toContain(g.mode);
    });
  });

  it('returns game by id', async () => {
    const games = await api.liveGames.getAll();
    const game = await api.liveGames.getById(games[0].id);
    expect(game).toBeDefined();
    expect(game?.id).toBe(games[0].id);
  });

  it('returns null for unknown id', async () => {
    const game = await api.liveGames.getById('nonexistent');
    expect(game).toBeNull();
  });
});

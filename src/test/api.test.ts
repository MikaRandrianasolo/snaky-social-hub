import { describe, it, expect, beforeEach } from 'vitest';
import { api } from '@/services/api';

describe('api.auth', () => {
  it('signs up a new user', async () => {
    const user = await api.auth.signup('TestUser', 'test@test.com', 'password123');
    expect(user.username).toBe('TestUser');
    expect(user.email).toBe('test@test.com');
    expect(user.id).toBeDefined();
  });

  it('logs in with valid credentials', async () => {
    await api.auth.signup('LoginTest', 'login@test.com', 'pass123');
    await api.auth.logout();
    const user = await api.auth.login('login@test.com', 'pass123');
    expect(user.username).toBe('LoginTest');
  });

  it('rejects invalid login', async () => {
    await expect(api.auth.login('nobody@test.com', 'wrong')).rejects.toThrow('Invalid email or password');
  });

  it('rejects duplicate email signup', async () => {
    await api.auth.signup('Dup1', 'dup@test.com', 'pass');
    await expect(api.auth.signup('Dup2', 'dup@test.com', 'pass')).rejects.toThrow('Email already exists');
  });

  it('logs out correctly', async () => {
    await api.auth.signup('LogoutUser', 'logout@test.com', 'pass');
    await api.auth.logout();
    const user = await api.auth.getCurrentUser();
    expect(user).toBeNull();
  });

  it('returns current user after login', async () => {
    await api.auth.signup('CurrentUser', 'current@test.com', 'pass');
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
    await api.auth.signup('Scorer', 'scorer@test.com', 'pass');
    const entry = await api.leaderboard.submitScore(999, 'walls');
    expect(entry.score).toBe(999);
    expect(entry.mode).toBe('walls');
    expect(entry.username).toBe('Scorer');
    await api.auth.logout();
  });

  it('rejects score submission when not logged in', async () => {
    await api.auth.logout();
    await expect(api.leaderboard.submitScore(100, 'walls')).rejects.toThrow('Must be logged in');
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

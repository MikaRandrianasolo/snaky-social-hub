/**
 * Frontend API service - integrates with FastAPI backend
 * Based on OpenAPI specification: /openapi.yaml
 * Backend URL: http://localhost:8000/api
 */

export interface User {
  id: string;
  username: string;
  email: string;
}

export interface AuthResponse {
  user: User;
  token: string;
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

// Backend configuration
// Use a relative API path so the frontend talks to the same origin in production.
// During local development you can set `VITE_API_BASE_URL` in your environment.
const API_BASE_URL = (typeof window !== 'undefined' && (window as any).__API_BASE_URL) ||
  (import.meta.env && import.meta.env.VITE_API_BASE_URL) || '/api';

// Token storage - always use localStorage as primary source
let memoryTokenStorage: string | null = null;

/**
 * Get auth token from localStorage first, then memory fallback
 */
function getStoredToken(): string | null {
  if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
    try {
      const token = localStorage.getItem('auth_token');
      if (token) {
        memoryTokenStorage = token; // Keep memory in sync
        return token;
      }
    } catch {
      // localStorage not available, fall through to memory
    }
  }

  return memoryTokenStorage;
}

/**
 * Store auth token in localStorage and memory
 */
function storeToken(token: string): void {
  memoryTokenStorage = token;

  if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
    try {
      localStorage.setItem('auth_token', token);
    } catch {
      // localStorage not available, use memory storage
      console.warn('localStorage not available, using memory storage for token');
    }
  }
}

/**
 * Clear auth token from localStorage and memory
 */
function clearToken(): void {
  memoryTokenStorage = null;

  if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
    try {
      localStorage.removeItem('auth_token');
    } catch {
      // localStorage not available
    }
  }
}

/**
 * Fetch with authentication header
 */
async function fetchWithAuth(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getStoredToken();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle 401 Unauthorized by clearing token
  if (response.status === 401) {
    clearToken();
  }

  return response;
}

/**
 * Handle API response errors
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `API Error: ${response.status}`;
    try {
      const error = await response.json();
      errorMessage = error.error || error.message || errorMessage;
    } catch {
      // Could not parse error response
    }
    throw new Error(errorMessage);
  }
  return response.json();
}


// Auth API endpoints
export const api = {
  auth: {
    /**
     * Sign up a new user
     * POST /api/auth/signup
     */
    async signup(username: string, email: string, password: string): Promise<User> {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      });

      let errorMessage = 'Signup failed';
      if (!response.ok) {
        try {
          const error = await response.json();
          // Handle FastAPI validation errors
          if (error.detail && typeof error.detail === 'string') {
            errorMessage = error.detail;
          } else if (error.detail && Array.isArray(error.detail)) {
            // Validation error array
            errorMessage = error.detail[0]?.msg || 'Invalid input';
          } else if (error.error) {
            errorMessage = error.error;
          } else if (error.message) {
            errorMessage = error.message;
          }
        } catch {
          // Could not parse error response, use generic message
        }
        throw new Error(errorMessage);
      }

      return response.json();
    },

    /**
     * Login with email and password
     * POST /api/auth/login
     * Returns {user, token}
     */
    async login(email: string, password: string): Promise<User> {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      let errorMessage = 'Login failed';
      if (!response.ok) {
        try {
          const error = await response.json();
          // Handle FastAPI validation errors
          if (error.detail && typeof error.detail === 'string') {
            errorMessage = error.detail;
          } else if (error.detail && Array.isArray(error.detail)) {
            errorMessage = error.detail[0]?.msg || 'Invalid input';
          } else if (error.error) {
            errorMessage = error.error;
          } else if (error.message) {
            errorMessage = error.message;
          }
        } catch {
          // Could not parse error response, use status-based message
          if (response.status === 401) {
            errorMessage = 'Invalid email or password';
          }
        }
        throw new Error(errorMessage);
      }

      const data: AuthResponse = await response.json();
      // Store token for future requests
      storeToken(data.token);
      return data.user;
    },

    /**
     * Logout current user
     * POST /api/auth/logout
     */
    async logout(): Promise<void> {
      try {
        await fetchWithAuth('/auth/logout', { method: 'POST' });
      } finally {
        // Clear token regardless of response
        clearToken();
      }
    },

    /**
     * Get current authenticated user
     * GET /api/auth/me
     */
    async getCurrentUser(): Promise<User | null> {
      try {
        const token = authToken || getStoredToken();
        if (!token) {
          return null;
        }

        const response = await fetchWithAuth('/auth/me');
        if (!response.ok) {
          if (response.status === 401) {
            clearToken();
          }
          return null;
        }

        return response.json();
      } catch {
        // Silently return null if not authenticated
        return null;
      }
    },
  },

  leaderboard: {
    /**
     * Get all leaderboard entries
     * GET /api/leaderboard?mode=walls|pass-through (optional)
     */
    async getAll(mode?: GameMode): Promise<LeaderboardEntry[]> {
      const params = new URLSearchParams();
      if (mode) {
        params.append('mode', mode);
      }

      const response = await fetch(
        `${API_BASE_URL}/leaderboard${params.toString() ? '?' + params.toString() : ''}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch leaderboard');
      }

      return response.json();
    },

    /**
     * Submit a score to the leaderboard
     * POST /api/leaderboard
     * Requires authentication
     */
    async submitScore(score: number, mode: GameMode): Promise<LeaderboardEntry> {
      const response = await fetchWithAuth('/leaderboard', {
        method: 'POST',
        body: JSON.stringify({ score, mode }),
      });

      let errorMessage = 'Failed to submit score';
      if (!response.ok) {
        try {
          const error = await response.json();
          // Handle FastAPI validation errors
          if (error.detail && typeof error.detail === 'string') {
            errorMessage = error.detail;
          } else if (error.detail && Array.isArray(error.detail)) {
            errorMessage = error.detail[0]?.msg || 'Invalid input';
          } else if (error.error) {
            errorMessage = error.error;
          } else if (error.message) {
            errorMessage = error.message;
          }
        } catch {
          // Could not parse error response
          if (response.status === 401) {
            errorMessage = 'Must be logged in to submit score';
          }
        }
        throw new Error(errorMessage);
      }

      return response.json();
    },
  },

  liveGames: {
    /**
     * Get all active live games
     * GET /api/games
     */
    async getAll(): Promise<LiveGame[]> {
      const response = await fetch(`${API_BASE_URL}/games`);

      if (!response.ok) {
        throw new Error('Failed to fetch live games');
      }

      return response.json();
    },

    /**
     * Get a specific live game by ID
     * GET /api/games/{gameId}
     */
    async getById(id: string): Promise<LiveGame | null> {
      const response = await fetch(`${API_BASE_URL}/games/${id}`);

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error('Failed to fetch game details');
      }

      return response.json();
    },
  },
};

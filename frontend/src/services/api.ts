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

// Token storage - single source of truth
let currentToken: string | null = null;

/**
 * Get current auth token
 */
function getStoredToken(): string | null {
  // Check memory first (fastest)
  if (currentToken) {
    return currentToken;
  }
  
  // Fall back to localStorage
  if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
    try {
      const token = localStorage.getItem('auth_token');
      if (token) {
        currentToken = token; // Sync to memory
        console.log('[Auth] Token restored from localStorage');
        return token;
      }
    } catch (err) {
      console.warn('[Auth] localStorage access failed:', err);
    }
  }

  return null;
}

/**
 * Store auth token in memory and localStorage
 */
function storeToken(token: string): void {
  currentToken = token;
  console.log('[Auth] Token stored in memory');

  if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
    try {
      localStorage.setItem('auth_token', token);
      console.log('[Auth] Token stored in localStorage');
    } catch (err) {
      console.warn('[Auth] Failed to store token in localStorage:', err);
    }
  }
}

/**
 * Clear auth token from memory and localStorage
 */
function clearToken(): void {
  currentToken = null;
  console.log('[Auth] Token cleared');

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
  console.log(`[API] fetchWithAuth ${endpoint} - token present: ${!!token}`);

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
    console.log('[API] Authorization header set');
  } else {
    console.warn('[API] No token available for authenticated request');
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle 401 Unauthorized by clearing token
  if (response.status === 401) {
    console.warn('[Auth] 401 Unauthorized - clearing token');
    clearToken();
  }

  return response;
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
      console.log('[Auth] Starting signup:', { username, email });
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
        console.error('[Auth] Signup error:', errorMessage);
        throw new Error(errorMessage);
      }

      try {
        const data: AuthResponse = await response.json();
        console.log('[Auth] Signup response received:', { hasToken: !!data.token, hasUser: !!data.user });
        
        if (!data.token) {
          console.error('[Auth] Signup response missing token:', data);
          throw new Error('No authentication token received from signup');
        }
        
        // Store token for future requests (user is now authenticated)
        storeToken(data.token);
        console.log('[Auth] Signup successful, token stored');
        return data.user;
      } catch (err) {
        console.error('[Auth] Failed to parse signup response:', err);
        throw new Error('Invalid signup response from server');
      }
    },

    /**
     * Login with email and password
     * POST /api/auth/login
     * Returns {user, token}
     */
    async login(email: string, password: string): Promise<User> {
      console.log('[Auth] Starting login:', { email });
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
        console.error('[Auth] Login error:', errorMessage);
        throw new Error(errorMessage);
      }

      const data: AuthResponse = await response.json();
      console.log('[Auth] Login response received, storing token');
      // Store token for future requests
      storeToken(data.token);
      console.log('[Auth] Login successful');
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
        const token = getStoredToken();
        if (!token) {
          console.log('[Auth] No token available, user not authenticated');
          return null;
        }

        console.log('[Auth] Fetching current user with token');
        const response = await fetchWithAuth('/auth/me');
        if (!response.ok) {
          console.warn(`[Auth] Get user failed: ${response.status}`);
          if (response.status === 401) {
            clearToken();
          }
          return null;
        }

        const user = await response.json();
        console.log('[Auth] Current user retrieved:', user.username);
        return user;
      } catch (err) {
        console.error('[Auth] Error getting current user:', err);
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
      console.log('[Score] Submitting score:', { score, mode });
      const token = getStoredToken();
      console.log('[Score] Token present:', !!token);
      
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
            errorMessage = 'Authentication required - please log in first';
          } else if (response.status === 400) {
            errorMessage = 'Invalid score or mode';
          } else {
            errorMessage = `Server error: ${response.status}`;
          }
        }
        console.error('[Score] Submission failed:', { status: response.status, message: errorMessage });
        throw new Error(errorMessage);
      }

      const entry = await response.json();
      console.log('[Score] Score submitted successfully:', { id: entry.id, score: entry.score });
      return entry;
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

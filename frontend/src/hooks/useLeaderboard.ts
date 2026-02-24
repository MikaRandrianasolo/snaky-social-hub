import { useEffect, useState } from 'react';
import { api, LeaderboardEntry, GameMode } from '@/services/api';

interface UseLeaderboardOptions {
    mode?: GameMode | 'all';
}

export function useLeaderboard({ mode = 'all' }: UseLeaderboardOptions = {}) {
    const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchLeaderboard = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await api.leaderboard.getAll(
                mode === 'all' ? undefined : mode
            );
            setEntries(data);
        } catch (err) {
            setError(err instanceof Error ? err : new Error('Failed to fetch leaderboard'));
            console.error('Failed to fetch leaderboard:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLeaderboard();
    }, [mode]);

    return {
        entries,
        loading,
        error,
        refetch: fetchLeaderboard,
    };
}

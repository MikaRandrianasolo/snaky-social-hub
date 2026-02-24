import { useState, useEffect, useCallback, useRef } from 'react';
import { GameMode } from '@/services/api';
import {
  GameState, Direction, createInitialState, moveSnake,
  isValidDirectionChange, getSpeed, getAIDirection,
} from '@/game/engine';

interface UseSnakeGameOptions {
  mode: GameMode;
  autoPlay?: boolean;
  onGameOver?: (score: number) => void;
}

export function useSnakeGame({ mode, autoPlay = false, onGameOver }: UseSnakeGameOptions) {
  const [gameState, setGameState] = useState<GameState>(() => createInitialState(mode));
  const directionQueue = useRef<Direction[]>([]);
  const gameLoopRef = useRef<number | null>(null);
  const isRunning = useRef(false);

  const resetGame = useCallback(() => {
    directionQueue.current = [];
    setGameState(createInitialState(mode));
  }, [mode]);

  const changeDirection = useCallback((dir: Direction) => {
    directionQueue.current.push(dir);
  }, []);

  const togglePause = useCallback(() => {
    setGameState(prev => ({ ...prev, isPaused: !prev.isPaused }));
  }, []);

  const startGame = useCallback(() => {
    setGameState(prev => ({ ...prev, isPaused: false }));
  }, []);

  // Game loop
  useEffect(() => {
    if (gameState.isGameOver || gameState.isPaused) {
      if (gameLoopRef.current) {
        clearTimeout(gameLoopRef.current);
        gameLoopRef.current = null;
      }
      if (gameState.isGameOver && onGameOver && isRunning.current) {
        isRunning.current = false;
        onGameOver(gameState.score);
      }
      return;
    }

    isRunning.current = true;
    const speed = getSpeed(gameState.score);

    gameLoopRef.current = window.setTimeout(() => {
      setGameState(prev => {
        // Process direction queue
        let dir = prev.direction;
        while (directionQueue.current.length > 0) {
          const next = directionQueue.current.shift()!;
          if (isValidDirectionChange(dir, next)) {
            dir = next;
            break;
          }
        }

        // AI for autoPlay
        if (autoPlay) {
          dir = getAIDirection({ ...prev, direction: dir });
        }

        return moveSnake({ ...prev, direction: dir });
      });
    }, speed);

    return () => {
      if (gameLoopRef.current) clearTimeout(gameLoopRef.current);
    };
  }, [gameState.isGameOver, gameState.isPaused, gameState.snake, gameState.score, autoPlay, onGameOver]);

  // Keyboard controls
  useEffect(() => {
    if (autoPlay) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // If the user is focusing an input, textarea, select, or a contentEditable element,
      // do not intercept keys so typing in forms (login/signup) works as expected.
      const active = document.activeElement as HTMLElement | null;
      if (active) {
        const tag = active.tagName?.toUpperCase();
        if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || active.isContentEditable) {
          return;
        }
      }
      const keyMap: Record<string, Direction> = {
        ArrowUp: 'UP', ArrowDown: 'DOWN', ArrowLeft: 'LEFT', ArrowRight: 'RIGHT',
        w: 'UP', s: 'DOWN', a: 'LEFT', d: 'RIGHT',
        W: 'UP', S: 'DOWN', A: 'LEFT', D: 'RIGHT',
      };
      const dir = keyMap[e.key];
      if (dir) {
        e.preventDefault();
        changeDirection(dir);
      }
      if (e.key === ' ') {
        e.preventDefault();
        togglePause();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [autoPlay, changeDirection, togglePause]);

  return { gameState, resetGame, changeDirection, togglePause, startGame };
}

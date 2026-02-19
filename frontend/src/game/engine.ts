import { GameMode } from '@/services/api';

export type Direction = 'UP' | 'DOWN' | 'LEFT' | 'RIGHT';
export type Position = { x: number; y: number };

export interface GameState {
  snake: Position[];
  food: Position;
  direction: Direction;
  score: number;
  isGameOver: boolean;
  isPaused: boolean;
  mode: GameMode;
  gridSize: number;
}

export const GRID_SIZE = 20;
export const INITIAL_SPEED = 150;
export const SPEED_INCREMENT = 2;
export const MIN_SPEED = 50;

export function createInitialState(mode: GameMode): GameState {
  const center = Math.floor(GRID_SIZE / 2);
  const snake = [
    { x: center, y: center },
    { x: center - 1, y: center },
    { x: center - 2, y: center },
  ];
  return {
    snake,
    food: generateFood(snake),
    direction: 'RIGHT',
    score: 0,
    isGameOver: false,
    isPaused: false,
    mode,
    gridSize: GRID_SIZE,
  };
}

export function generateFood(snake: Position[]): Position {
  let food: Position;
  do {
    food = {
      x: Math.floor(Math.random() * GRID_SIZE),
      y: Math.floor(Math.random() * GRID_SIZE),
    };
  } while (snake.some(s => s.x === food.x && s.y === food.y));
  return food;
}

export function getOppositeDirection(dir: Direction): Direction {
  const opposites: Record<Direction, Direction> = {
    UP: 'DOWN', DOWN: 'UP', LEFT: 'RIGHT', RIGHT: 'LEFT',
  };
  return opposites[dir];
}

export function isValidDirectionChange(current: Direction, next: Direction): boolean {
  return next !== getOppositeDirection(current);
}

export function moveSnake(state: GameState): GameState {
  if (state.isGameOver || state.isPaused) return state;

  const head = state.snake[0];
  const delta: Record<Direction, Position> = {
    UP: { x: 0, y: -1 },
    DOWN: { x: 0, y: 1 },
    LEFT: { x: -1, y: 0 },
    RIGHT: { x: 1, y: 0 },
  };

  let newHead: Position = {
    x: head.x + delta[state.direction].x,
    y: head.y + delta[state.direction].y,
  };

  // Handle wall collision based on mode
  if (state.mode === 'pass-through') {
    newHead = {
      x: (newHead.x + GRID_SIZE) % GRID_SIZE,
      y: (newHead.y + GRID_SIZE) % GRID_SIZE,
    };
  } else {
    // Walls mode - game over on wall hit
    if (newHead.x < 0 || newHead.x >= GRID_SIZE || newHead.y < 0 || newHead.y >= GRID_SIZE) {
      return { ...state, isGameOver: true };
    }
  }

  // Self collision (exclude tail since it will move)
  const bodyWithoutTail = state.snake.slice(0, -1);
  if (bodyWithoutTail.some(s => s.x === newHead.x && s.y === newHead.y)) {
    return { ...state, isGameOver: true };
  }

  const ateFood = newHead.x === state.food.x && newHead.y === state.food.y;
  const newSnake = [newHead, ...state.snake];
  if (!ateFood) newSnake.pop();

  return {
    ...state,
    snake: newSnake,
    food: ateFood ? generateFood(newSnake) : state.food,
    score: ateFood ? state.score + 10 : state.score,
  };
}

export function getSpeed(score: number): number {
  return Math.max(MIN_SPEED, INITIAL_SPEED - Math.floor(score / 10) * SPEED_INCREMENT);
}

// AI logic for watch mode - simple food-seeking with some randomness
export function getAIDirection(state: GameState): Direction {
  const head = state.snake[0];
  const food = state.food;
  const possibleDirs: Direction[] = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    .filter(d => isValidDirectionChange(state.direction, d as Direction)) as Direction[];

  // Filter out directions that would cause self-collision
  const safeDirs = possibleDirs.filter(dir => {
    const delta: Record<Direction, Position> = {
      UP: { x: 0, y: -1 }, DOWN: { x: 0, y: 1 },
      LEFT: { x: -1, y: 0 }, RIGHT: { x: 1, y: 0 },
    };
    let next = { x: head.x + delta[dir].x, y: head.y + delta[dir].y };
    if (state.mode === 'pass-through') {
      next = { x: (next.x + GRID_SIZE) % GRID_SIZE, y: (next.y + GRID_SIZE) % GRID_SIZE };
    } else if (next.x < 0 || next.x >= GRID_SIZE || next.y < 0 || next.y >= GRID_SIZE) {
      return false;
    }
    return !state.snake.some(s => s.x === next.x && s.y === next.y);
  });

  if (safeDirs.length === 0) return state.direction;

  // 80% chance to move toward food, 20% random
  if (Math.random() < 0.8) {
    const dx = food.x - head.x;
    const dy = food.y - head.y;
    const preferred: Direction[] = [];
    if (dy < 0) preferred.push('UP');
    if (dy > 0) preferred.push('DOWN');
    if (dx < 0) preferred.push('LEFT');
    if (dx > 0) preferred.push('RIGHT');
    const smartMove = preferred.find(d => safeDirs.includes(d));
    if (smartMove) return smartMove;
  }

  return safeDirs[Math.floor(Math.random() * safeDirs.length)];
}

import { describe, it, expect } from 'vitest';
import {
  createInitialState, moveSnake, isValidDirectionChange,
  getSpeed, getOppositeDirection, generateFood, getAIDirection,
  GRID_SIZE, INITIAL_SPEED, MIN_SPEED,
} from '@/game/engine';

describe('createInitialState', () => {
  it('creates state with 3-segment snake at center', () => {
    const state = createInitialState('pass-through');
    expect(state.snake).toHaveLength(3);
    expect(state.direction).toBe('RIGHT');
    expect(state.score).toBe(0);
    expect(state.isGameOver).toBe(false);
    expect(state.mode).toBe('pass-through');
  });

  it('creates state with walls mode', () => {
    const state = createInitialState('walls');
    expect(state.mode).toBe('walls');
  });

  it('places food not on snake', () => {
    const state = createInitialState('pass-through');
    const onSnake = state.snake.some(s => s.x === state.food.x && s.y === state.food.y);
    expect(onSnake).toBe(false);
  });
});

describe('moveSnake', () => {
  it('moves snake right by default', () => {
    const state = createInitialState('pass-through');
    const next = moveSnake(state);
    expect(next.snake[0].x).toBe(state.snake[0].x + 1);
    expect(next.snake[0].y).toBe(state.snake[0].y);
  });

  it('wraps around in pass-through mode', () => {
    const state = createInitialState('pass-through');
    state.snake = [{ x: GRID_SIZE - 1, y: 5 }];
    state.direction = 'RIGHT';
    const next = moveSnake(state);
    expect(next.snake[0].x).toBe(0);
    expect(next.isGameOver).toBe(false);
  });

  it('wraps left in pass-through mode', () => {
    const state = createInitialState('pass-through');
    state.snake = [{ x: 0, y: 5 }];
    state.direction = 'LEFT';
    const next = moveSnake(state);
    expect(next.snake[0].x).toBe(GRID_SIZE - 1);
  });

  it('wraps top in pass-through mode', () => {
    const state = createInitialState('pass-through');
    state.snake = [{ x: 5, y: 0 }];
    state.direction = 'UP';
    const next = moveSnake(state);
    expect(next.snake[0].y).toBe(GRID_SIZE - 1);
  });

  it('wraps bottom in pass-through mode', () => {
    const state = createInitialState('pass-through');
    state.snake = [{ x: 5, y: GRID_SIZE - 1 }];
    state.direction = 'DOWN';
    const next = moveSnake(state);
    expect(next.snake[0].y).toBe(0);
  });

  it('dies on wall hit in walls mode (right)', () => {
    const state = createInitialState('walls');
    state.snake = [{ x: GRID_SIZE - 1, y: 5 }];
    state.direction = 'RIGHT';
    const next = moveSnake(state);
    expect(next.isGameOver).toBe(true);
  });

  it('dies on wall hit in walls mode (left)', () => {
    const state = createInitialState('walls');
    state.snake = [{ x: 0, y: 5 }];
    state.direction = 'LEFT';
    const next = moveSnake(state);
    expect(next.isGameOver).toBe(true);
  });

  it('dies on wall hit in walls mode (top)', () => {
    const state = createInitialState('walls');
    state.snake = [{ x: 5, y: 0 }];
    state.direction = 'UP';
    const next = moveSnake(state);
    expect(next.isGameOver).toBe(true);
  });

  it('dies on wall hit in walls mode (bottom)', () => {
    const state = createInitialState('walls');
    state.snake = [{ x: 5, y: GRID_SIZE - 1 }];
    state.direction = 'DOWN';
    const next = moveSnake(state);
    expect(next.isGameOver).toBe(true);
  });

  it('dies on self collision', () => {
    const state = createInitialState('pass-through');
    // Snake curled so moving DOWN hits its own body
    state.snake = [
      { x: 5, y: 5 },
      { x: 5, y: 4 },
      { x: 6, y: 4 },
      { x: 6, y: 5 },
      { x: 6, y: 6 },
      { x: 5, y: 6 },
    ];
    state.direction = 'RIGHT';
    const next = moveSnake(state);
    expect(next.isGameOver).toBe(true);
  });

  it('grows snake when eating food', () => {
    const state = createInitialState('pass-through');
    const head = state.snake[0];
    state.food = { x: head.x + 1, y: head.y };
    const originalLength = state.snake.length;
    const next = moveSnake(state);
    expect(next.snake.length).toBe(originalLength + 1);
    expect(next.score).toBe(10);
  });

  it('does not move when game is over', () => {
    const state = createInitialState('pass-through');
    state.isGameOver = true;
    const next = moveSnake(state);
    expect(next).toEqual(state);
  });

  it('does not move when paused', () => {
    const state = createInitialState('pass-through');
    state.isPaused = true;
    const next = moveSnake(state);
    expect(next).toEqual(state);
  });
});

describe('isValidDirectionChange', () => {
  it('allows perpendicular changes', () => {
    expect(isValidDirectionChange('RIGHT', 'UP')).toBe(true);
    expect(isValidDirectionChange('RIGHT', 'DOWN')).toBe(true);
    expect(isValidDirectionChange('UP', 'LEFT')).toBe(true);
    expect(isValidDirectionChange('UP', 'RIGHT')).toBe(true);
  });

  it('blocks opposite direction', () => {
    expect(isValidDirectionChange('RIGHT', 'LEFT')).toBe(false);
    expect(isValidDirectionChange('LEFT', 'RIGHT')).toBe(false);
    expect(isValidDirectionChange('UP', 'DOWN')).toBe(false);
    expect(isValidDirectionChange('DOWN', 'UP')).toBe(false);
  });

  it('allows same direction', () => {
    expect(isValidDirectionChange('RIGHT', 'RIGHT')).toBe(true);
  });
});

describe('getOppositeDirection', () => {
  it('returns opposite for each direction', () => {
    expect(getOppositeDirection('UP')).toBe('DOWN');
    expect(getOppositeDirection('DOWN')).toBe('UP');
    expect(getOppositeDirection('LEFT')).toBe('RIGHT');
    expect(getOppositeDirection('RIGHT')).toBe('LEFT');
  });
});

describe('getSpeed', () => {
  it('returns initial speed at score 0', () => {
    expect(getSpeed(0)).toBe(INITIAL_SPEED);
  });

  it('decreases speed as score increases', () => {
    expect(getSpeed(100)).toBeLessThan(INITIAL_SPEED);
  });

  it('never goes below minimum speed', () => {
    expect(getSpeed(10000)).toBe(MIN_SPEED);
  });
});

describe('generateFood', () => {
  it('generates food not on the snake', () => {
    const snake = [{ x: 5, y: 5 }, { x: 4, y: 5 }];
    for (let i = 0; i < 100; i++) {
      const food = generateFood(snake);
      const onSnake = snake.some(s => s.x === food.x && s.y === food.y);
      expect(onSnake).toBe(false);
    }
  });

  it('generates food within grid bounds', () => {
    const snake = [{ x: 5, y: 5 }];
    for (let i = 0; i < 100; i++) {
      const food = generateFood(snake);
      expect(food.x).toBeGreaterThanOrEqual(0);
      expect(food.x).toBeLessThan(GRID_SIZE);
      expect(food.y).toBeGreaterThanOrEqual(0);
      expect(food.y).toBeLessThan(GRID_SIZE);
    }
  });
});

describe('getAIDirection', () => {
  it('returns a valid direction', () => {
    const state = createInitialState('pass-through');
    const dir = getAIDirection(state);
    expect(['UP', 'DOWN', 'LEFT', 'RIGHT']).toContain(dir);
  });

  it('does not return opposite direction', () => {
    const state = createInitialState('pass-through');
    state.direction = 'RIGHT';
    for (let i = 0; i < 50; i++) {
      const dir = getAIDirection(state);
      expect(dir).not.toBe('LEFT');
    }
  });

  it('avoids walls in walls mode', () => {
    const state = createInitialState('walls');
    state.snake = [{ x: GRID_SIZE - 1, y: 5 }];
    state.direction = 'RIGHT';
    for (let i = 0; i < 50; i++) {
      const dir = getAIDirection(state);
      expect(dir).not.toBe('RIGHT');
    }
  });
});

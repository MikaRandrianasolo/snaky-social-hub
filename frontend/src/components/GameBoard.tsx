import { GameState } from '@/game/engine';

interface GameBoardProps {
  gameState: GameState;
  compact?: boolean;
}

export function GameBoard({ gameState, compact = false }: GameBoardProps) {
  const { snake, food, gridSize, mode } = gameState;
  const cellSize = compact ? 12 : 20;
  const boardSize = cellSize * gridSize;

  return (
    <div className="relative inline-block">
      <svg
        width={boardSize}
        height={boardSize}
        className={`border-2 rounded-sm ${mode === 'walls' ? 'border-destructive/60' : 'border-primary/40'}`}
        style={{
          boxShadow: mode === 'walls'
            ? '0 0 15px hsl(0 80% 55% / 0.3), inset 0 0 15px hsl(0 80% 55% / 0.1)'
            : 'var(--neon-glow)',
        }}
      >
        {/* Background */}
        <rect width={boardSize} height={boardSize} fill="hsl(220, 20%, 6%)" />

        {/* Grid lines */}
        {Array.from({ length: gridSize }, (_, i) => (
          <g key={i}>
            <line
              x1={i * cellSize} y1={0} x2={i * cellSize} y2={boardSize}
              stroke="hsl(150, 100%, 50%)" strokeOpacity="0.05"
            />
            <line
              x1={0} y1={i * cellSize} x2={boardSize} y2={i * cellSize}
              stroke="hsl(150, 100%, 50%)" strokeOpacity="0.05"
            />
          </g>
        ))}

        {/* Food */}
        <rect
          x={food.x * cellSize + 1}
          y={food.y * cellSize + 1}
          width={cellSize - 2}
          height={cellSize - 2}
          rx={compact ? 2 : 4}
          fill="hsl(280, 100%, 65%)"
          className="animate-pulse-neon"
        >
          <animate attributeName="opacity" values="1;0.6;1" dur="0.8s" repeatCount="indefinite" />
        </rect>

        {/* Snake */}
        {snake.map((segment, i) => {
          const isHead = i === 0;
          return (
            <rect
              key={i}
              x={segment.x * cellSize + (isHead ? 0 : 1)}
              y={segment.y * cellSize + (isHead ? 0 : 1)}
              width={cellSize - (isHead ? 0 : 2)}
              height={cellSize - (isHead ? 0 : 2)}
              rx={isHead ? (compact ? 3 : 4) : 2}
              fill={isHead ? 'hsl(150, 100%, 50%)' : `hsl(150, 80%, ${45 - i * 0.5}%)`}
              style={isHead ? {
                filter: 'drop-shadow(0 0 4px hsl(150, 100%, 50%))',
              } : undefined}
            />
          );
        })}
      </svg>
    </div>
  );
}

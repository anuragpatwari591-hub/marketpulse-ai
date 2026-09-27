import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { Card, Badge, LoadingState, ErrorState } from '../components/ui/primitives'

const LABEL_TONE: Record<string, 'good' | 'bad' | 'neutral' | 'warn'> = {
  'Very Strong': 'good',
  Strong: 'good',
  Watch: 'warn',
  Weak: 'neutral',
  Neutral: 'neutral',
}

export function Signals() {
  const { data, isLoading, isError, error } = useQuery({ queryKey: ['top-signals'], queryFn: () => api.topSignals(25) })

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-semibold">Signals</h1>
        <p className="text-xs text-slate-500">
          Multi-factor composite scores across the demo universe. These are analytical scores, not trade
          recommendations — open a symbol to see the full factor breakdown, risks and invalidation levels.
        </p>
      </div>
      {isLoading && <LoadingState label="Computing signals…" />}
      {isError && <ErrorState message={(error as Error).message} />}
      {data && (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          {data.items.map((s) => (
            <Link key={s.symbol} to={`/signals/${s.symbol}`}>
              <Card className="transition-colors hover:border-slate-600">
                <div className="flex items-center justify-between">
                  <span className="mono text-base font-semibold">{s.symbol}</span>
                  <Badge tone={LABEL_TONE[s.label] ?? 'neutral'}>{s.label}</Badge>
                </div>
                <div className="mt-2 flex items-end justify-between">
                  <span className="text-xs capitalize text-slate-500">{s.direction}</span>
                  <span className="mono text-2xl font-bold">{s.score.toFixed(0)}</span>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

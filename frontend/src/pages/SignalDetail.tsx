import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { api } from '../lib/api'
import { Card, CardTitle, Badge, LoadingState, ErrorState } from '../components/ui/primitives'

export function SignalDetail() {
  const { symbol = '' } = useParams()
  const { data, isLoading, isError, error } = useQuery({ queryKey: ['signal', symbol], queryFn: () => api.signal(symbol) })

  if (isLoading) return <LoadingState label={`Computing signal for ${symbol}…`} />
  if (isError) return <ErrorState message={(error as Error).message} />
  if (!data) return null

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="mono text-2xl font-bold">{data.symbol}</h1>
          <span className="text-sm capitalize text-slate-500">{data.direction} · {data.label}</span>
        </div>
        <div className="mono text-4xl font-bold">{data.score.toFixed(0)}<span className="text-base text-slate-500">/100</span></div>
      </div>

      <Card className="border-amber-900/40 bg-amber-950/10">
        <p className="text-xs text-amber-400">{data.disclaimer}</p>
      </Card>

      <Card>
        <CardTitle>Factor Breakdown</CardTitle>
        <div className="space-y-2">
          {data.contributions.map((c) => (
            <div key={c.factor} className="border-b border-slate-900 pb-2 last:border-0">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium capitalize">{c.factor.replace(/_/g, ' ')}</span>
                <span className="mono text-slate-400">
                  {c.raw_score.toFixed(0)} raw × {c.weight_pct}% = <strong>{c.weighted_score.toFixed(1)}</strong>
                </span>
              </div>
              <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
                <div className="h-full bg-sky-500" style={{ width: `${c.raw_score}%` }} />
              </div>
              <p className="mt-1 text-xs text-slate-500">{c.evidence}</p>
            </div>
          ))}
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardTitle>Risks</CardTitle>
          <ul className="list-inside list-disc space-y-1 text-sm text-slate-300">
            {data.risks.map((r) => <li key={r}>{r}</li>)}
          </ul>
        </Card>
        <Card>
          <CardTitle>Scenarios</CardTitle>
          <ul className="list-inside list-disc space-y-1 text-sm text-slate-300">
            {data.scenarios.map((s) => <li key={s}>{s}</li>)}
          </ul>
        </Card>
      </div>

      <Card>
        <CardTitle>Invalidation</CardTitle>
        <p className="text-sm text-slate-300">{data.invalidation}</p>
      </Card>

      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
        <span>Sources:</span>
        {data.sources.map((s) => <Badge key={s}>{s}</Badge>)}
        <span className="ml-auto">{data.data_freshness}</span>
      </div>
    </div>
  )
}

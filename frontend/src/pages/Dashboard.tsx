import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { useWatchlist } from '../store/watchlist'
import { Card, CardTitle, ChangeBadge, Badge, LoadingState, ErrorState, EmptyState, DataFreshness } from '../components/ui/primitives'

export function Dashboard() {
  const indices = useQuery({ queryKey: ['indices'], queryFn: api.indices, refetchInterval: 15000 })
  const breadth = useQuery({ queryKey: ['breadth'], queryFn: api.breadth, refetchInterval: 15000 })
  const movers = useQuery({ queryKey: ['movers'], queryFn: () => api.movers(5), refetchInterval: 15000 })
  const sectors = useQuery({ queryKey: ['sectors'], queryFn: api.sectors, refetchInterval: 30000 })
  const anomalies = useQuery({ queryKey: ['anomalies'], queryFn: () => api.anomalies(6), refetchInterval: 20000 })
  const news = useQuery({ queryKey: ['news', 'dashboard'], queryFn: () => api.news(6), refetchInterval: 60000 })
  const regime = useQuery({ queryKey: ['regime'], queryFn: api.regime, refetchInterval: 60000 })
  const watchlist = useWatchlist((s) => s.symbols)

  return (
    <div className="space-y-4">
      <section>
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-300">Indices</h2>
          {indices.data && <DataFreshness timestamp={indices.data.items[0]?.last_updated ?? new Date().toISOString()} />}
        </div>
        {indices.isLoading && <LoadingState label="Loading indices…" />}
        {indices.isError && <ErrorState message={(indices.error as Error).message} />}
        {indices.data && (
          <div className="grid grid-cols-2 gap-3 md:grid-cols-5">
            {indices.data.items.map((idx) => (
              <Card key={idx.symbol}>
                <div className="text-xs text-slate-400">{idx.name}</div>
                <div className="mono mt-1 text-lg font-semibold">{idx.price.toLocaleString('en-IN')}</div>
                <ChangeBadge value={idx.change_pct} />
              </Card>
            ))}
          </div>
        )}
      </section>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card>
          <CardTitle>Market Breadth</CardTitle>
          {breadth.isLoading && <LoadingState />}
          {breadth.isError && <ErrorState message={(breadth.error as Error).message} />}
          {breadth.data && (
            <div className="space-y-2">
              <div className="flex h-3 overflow-hidden rounded-full bg-slate-800">
                <div
                  className="bg-emerald-500"
                  style={{ width: `${(breadth.data.advances / (breadth.data.advances + breadth.data.declines + breadth.data.unchanged || 1)) * 100}%` }}
                />
                <div
                  className="bg-red-500"
                  style={{ width: `${(breadth.data.declines / (breadth.data.advances + breadth.data.declines + breadth.data.unchanged || 1)) * 100}%` }}
                />
              </div>
              <div className="flex justify-between text-xs mono">
                <span className="text-emerald-400">{breadth.data.advances} adv</span>
                <span className="text-slate-500">{breadth.data.unchanged} flat</span>
                <span className="text-red-400">{breadth.data.declines} dec</span>
              </div>
            </div>
          )}
        </Card>

        <Card>
          <CardTitle>Market Regime</CardTitle>
          {regime.isLoading && <LoadingState />}
          {regime.data && (
            <div className="space-y-1.5 text-sm">
              <div className="flex justify-between"><span className="text-slate-500">Trend</span><Badge tone={regime.data.trend === 'trending_bull' ? 'good' : regime.data.trend === 'trending_bear' ? 'bad' : 'neutral'}>{String(regime.data.trend).replace('_', ' ')}</Badge></div>
              <div className="flex justify-between"><span className="text-slate-500">Volatility</span><Badge tone={regime.data.volatility_state === 'high_volatility' ? 'warn' : 'neutral'}>{String(regime.data.volatility_state).replace('_', ' ')}</Badge></div>
              <div className="flex justify-between"><span className="text-slate-500">Risk Stance</span><Badge tone={regime.data.risk_state === 'risk_on' ? 'good' : regime.data.risk_state === 'risk_off' ? 'bad' : 'neutral'}>{String(regime.data.risk_state).replace('_', ' ')}</Badge></div>
              <p className="pt-1 text-[11px] text-slate-600">Derived from measurable inputs (trend/volatility/breadth), not AI-inferred.</p>
            </div>
          )}
        </Card>

        <Card>
          <CardTitle>Watchlist</CardTitle>
          {watchlist.length === 0 && <EmptyState message="Your watchlist is empty. Add symbols from a stock page." />}
          <ul className="space-y-1">
            {watchlist.map((symbol) => (
              <li key={symbol}>
                <Link to={`/stocks/${symbol}`} className="mono flex justify-between rounded px-1.5 py-1 text-sm hover:bg-slate-900">
                  {symbol}
                </Link>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardTitle>Top Gainers / Losers</CardTitle>
          {movers.isLoading && <LoadingState />}
          {movers.data && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="mb-1 text-[11px] uppercase text-emerald-500">Gainers</div>
                {movers.data.gainers.map((q) => (
                  <Link key={q.symbol} to={`/stocks/${q.symbol}`} className="flex items-center justify-between py-1 text-sm hover:text-white">
                    <span className="mono">{q.symbol}</span>
                    <ChangeBadge value={q.change_pct} />
                  </Link>
                ))}
              </div>
              <div>
                <div className="mb-1 text-[11px] uppercase text-red-500">Losers</div>
                {movers.data.losers.map((q) => (
                  <Link key={q.symbol} to={`/stocks/${q.symbol}`} className="flex items-center justify-between py-1 text-sm hover:text-white">
                    <span className="mono">{q.symbol}</span>
                    <ChangeBadge value={q.change_pct} />
                  </Link>
                ))}
              </div>
            </div>
          )}
        </Card>

        <Card>
          <CardTitle>Sector Heatmap</CardTitle>
          {sectors.isLoading && <LoadingState />}
          {sectors.data && (
            <div className="grid grid-cols-3 gap-2">
              {sectors.data.items.map((s) => {
                const intensity = Math.min(Math.abs(s.avg_change_pct) / 3, 1)
                const bg = s.avg_change_pct >= 0
                  ? `rgba(16,199,132,${0.15 + intensity * 0.55})`
                  : `rgba(234,57,67,${0.15 + intensity * 0.55})`
                return (
                  <div key={s.sector} style={{ backgroundColor: bg }} className="rounded p-2 text-center">
                    <div className="text-[11px] font-medium text-slate-100">{s.sector}</div>
                    <div className="mono text-xs text-slate-200">{s.avg_change_pct.toFixed(2)}%</div>
                  </div>
                )
              })}
            </div>
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardTitle>Volume &amp; Price Anomalies</CardTitle>
          {anomalies.isLoading && <LoadingState />}
          {anomalies.data && anomalies.data.items.length === 0 && <EmptyState message="No anomalies detected right now." />}
          {anomalies.data && anomalies.data.items.map((a) => (
            <Link key={a.symbol} to={`/stocks/${a.symbol}`} className="flex items-center justify-between border-b border-slate-900 py-1.5 text-sm last:border-0 hover:text-white">
              <span className="mono">{a.symbol}</span>
              <span className="flex items-center gap-2">
                {a.flags.map((f) => <Badge key={f} tone="warn">{f.replace(/_/g, ' ')}</Badge>)}
                <span className="mono text-xs text-slate-400">score {a.anomaly_score.toFixed(0)}</span>
              </span>
            </Link>
          ))}
        </Card>

        <Card>
          <CardTitle>Latest News</CardTitle>
          {news.isLoading && <LoadingState />}
          {news.data && news.data.items.map((n) => (
            <div key={n.id} className="border-b border-slate-900 py-1.5 text-sm last:border-0">
              <div className="flex items-center gap-2">
                <Badge tone={n.sentiment === 'positive' ? 'good' : n.sentiment === 'negative' ? 'bad' : 'neutral'}>{n.event_type}</Badge>
                <span className="mono text-xs text-slate-500">{n.symbol}</span>
              </div>
              <div className="mt-0.5 text-slate-300">{n.headline}</div>
            </div>
          ))}
        </Card>
      </div>
    </div>
  )
}

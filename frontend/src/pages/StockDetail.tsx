import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { api } from '../lib/api'
import { useWatchlist } from '../store/watchlist'
import { StockChart } from '../components/StockChart'
import { Card, CardTitle, ChangeBadge, Badge, LoadingState, ErrorState, EmptyState } from '../components/ui/primitives'

export function StockDetail() {
  const { symbol = '' } = useParams()
  const quote = useQuery({ queryKey: ['stock', symbol], queryFn: () => api.stock(symbol), refetchInterval: 15000 })
  const candles = useQuery({ queryKey: ['candles', symbol], queryFn: () => api.candles(symbol, 180) })
  const analysis = useQuery({ queryKey: ['analysis', symbol], queryFn: () => api.analysis(symbol) })
  const news = useQuery({ queryKey: ['stock-news', symbol], queryFn: () => api.stockNews(symbol) })
  const inWatchlist = useWatchlist((s) => s.symbols.includes(symbol))
  const toggle = useWatchlist((s) => s.toggle)

  if (quote.isLoading) return <LoadingState label={`Loading ${symbol}…`} />
  if (quote.isError) return <ErrorState message={(quote.error as Error).message} />
  if (!quote.data) return null

  const q = quote.data

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="mono text-2xl font-bold">{q.symbol}</h1>
            <Badge>{q.sector}</Badge>
          </div>
          <div className="text-sm text-slate-500">{q.name}</div>
        </div>
        <div className="text-right">
          <div className="mono text-2xl font-semibold">₹{q.price.toLocaleString('en-IN')}</div>
          <ChangeBadge value={q.change_pct} />
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => toggle(symbol)}
          className="rounded border border-slate-700 px-3 py-1.5 text-sm hover:bg-slate-900"
        >
          {inWatchlist ? '★ In Watchlist' : '☆ Add to Watchlist'}
        </button>
        <Link to={`/signals/${symbol}`} className="rounded border border-slate-700 px-3 py-1.5 text-sm hover:bg-slate-900">
          View Signal →
        </Link>
      </div>

      <Card>
        <CardTitle>Price Chart (180d)</CardTitle>
        {candles.isLoading && <LoadingState />}
        {candles.data && <StockChart candles={candles.data.items} />}
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card>
          <CardTitle>Technical Indicators</CardTitle>
          {analysis.isLoading && <LoadingState />}
          {analysis.data && (
            <dl className="grid grid-cols-2 gap-y-1.5 text-sm">
              {Object.entries(analysis.data.indicators).map(([key, value]) => (
                <div key={key} className="contents">
                  <dt className="text-slate-500">{key.replace(/_/g, ' ')}</dt>
                  <dd className="mono text-right">{value ?? '—'}</dd>
                </div>
              ))}
            </dl>
          )}
        </Card>

        <Card>
          <CardTitle>Levels</CardTitle>
          {analysis.data && (
            <dl className="grid grid-cols-2 gap-y-1.5 text-sm">
              {Object.entries(analysis.data.levels).map(([key, value]) => (
                <div key={key} className="contents">
                  <dt className="text-slate-500">{key.replace(/_/g, ' ')}</dt>
                  <dd className="mono text-right">₹{value}</dd>
                </div>
              ))}
              <div className="contents">
                <dt className="text-slate-500">gap</dt>
                <dd className="mono text-right">{analysis.data.gap.gap_type} ({analysis.data.gap.gap_pct}%)</dd>
              </div>
            </dl>
          )}
        </Card>

        <Card>
          <CardTitle>Volume Intelligence</CardTitle>
          {analysis.data && (
            <dl className="grid grid-cols-2 gap-y-1.5 text-sm">
              {Object.entries(analysis.data.volume).map(([key, value]) => (
                <div key={key} className="contents">
                  <dt className="text-slate-500">{key.replace(/_/g, ' ')}</dt>
                  <dd className="mono text-right">{String(value ?? '—')}</dd>
                </div>
              ))}
            </dl>
          )}
        </Card>
      </div>

      <Card>
        <CardTitle>Recent News</CardTitle>
        {news.isLoading && <LoadingState />}
        {news.data && news.data.items.length === 0 && <EmptyState message="No recent news for this symbol." />}
        {news.data && news.data.items.map((n) => (
          <div key={n.id} className="border-b border-slate-900 py-2 text-sm last:border-0">
            <div className="flex items-center gap-2">
              <Badge tone={n.sentiment === 'positive' ? 'good' : n.sentiment === 'negative' ? 'bad' : 'neutral'}>{n.event_type}</Badge>
              <span className="text-xs text-slate-500">{new Date(n.timestamp).toLocaleString()}</span>
            </div>
            <div className="mt-1 text-slate-200">{n.headline}</div>
            <div className="mt-0.5 text-xs text-slate-500">{n.summary}</div>
          </div>
        ))}
      </Card>
    </div>
  )
}

import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { ChangeBadge, ErrorState, LoadingState, EmptyState, Badge } from '../components/ui/primitives'

const SECTORS = [
  'IT', 'Banking', 'Financial Services', 'Auto', 'Pharma', 'FMCG', 'Energy',
  'Metals', 'Realty', 'Defence', 'Railways', 'Renewables', 'Telecom', 'Chemicals',
]

export function Screener() {
  const [sector, setSector] = useState('')
  const [minChange, setMinChange] = useState('')
  const [minRelVol, setMinRelVol] = useState('')
  const [aboveVwap, setAboveVwap] = useState<'any' | 'yes' | 'no'>('any')
  const [volClass, setVolClass] = useState('')

  const params = new URLSearchParams()
  if (sector) params.set('sector', sector)
  if (minChange) params.set('min_change_pct', minChange)
  if (minRelVol) params.set('min_relative_volume', minRelVol)
  if (aboveVwap !== 'any') params.set('above_vwap', aboveVwap === 'yes' ? 'true' : 'false')
  if (volClass) params.set('volume_classification', volClass)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['screener', params.toString()],
    queryFn: () => api.screener(params),
  })

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-semibold">Screener</h1>
        <p className="text-xs text-slate-500">
          Structured filters over the demo universe. A natural-language query box (e.g. "F&amp;O stocks with rising OI and volume above 2x")
          is planned but not implemented in this build — see PROJECT_STATUS.md.
        </p>
      </div>

      <div className="flex flex-wrap gap-3 rounded-lg border border-slate-800 bg-[var(--color-terminal-panel)] p-3">
        <select value={sector} onChange={(e) => setSector(e.target.value)} className="rounded border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm">
          <option value="">All sectors</option>
          {SECTORS.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <input
          placeholder="Min change %"
          value={minChange}
          onChange={(e) => setMinChange(e.target.value)}
          className="w-32 rounded border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm"
        />
        <input
          placeholder="Min rel. volume"
          value={minRelVol}
          onChange={(e) => setMinRelVol(e.target.value)}
          className="w-36 rounded border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm"
        />
        <select value={aboveVwap} onChange={(e) => setAboveVwap(e.target.value as 'any' | 'yes' | 'no')} className="rounded border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm">
          <option value="any">VWAP: any</option>
          <option value="yes">Above VWAP</option>
          <option value="no">Below VWAP</option>
        </select>
        <select value={volClass} onChange={(e) => setVolClass(e.target.value)} className="rounded border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm">
          <option value="">Volume: any</option>
          <option value="elevated">Elevated</option>
          <option value="unusual">Unusual</option>
          <option value="extreme">Extreme</option>
        </select>
      </div>

      {isLoading && <LoadingState label="Running screener…" />}
      {isError && <ErrorState message={(error as Error).message} />}
      {data && data.items.length === 0 && <EmptyState message="No stocks match these filters." />}
      {data && data.items.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-sm">
            <thead className="bg-slate-900 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-3 py-2">Symbol</th>
                <th className="px-3 py-2">Sector</th>
                <th className="px-3 py-2">Price</th>
                <th className="px-3 py-2">Chg %</th>
                <th className="px-3 py-2">Rel. Vol</th>
                <th className="px-3 py-2">RSI(14)</th>
                <th className="px-3 py-2">VWAP</th>
                <th className="px-3 py-2">Volume</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((r) => (
                <tr key={r.symbol} className="border-t border-slate-900 hover:bg-slate-900/60">
                  <td className="px-3 py-2"><Link to={`/stocks/${r.symbol}`} className="mono font-medium hover:underline">{r.symbol}</Link></td>
                  <td className="px-3 py-2 text-slate-400">{r.sector}</td>
                  <td className="mono px-3 py-2">₹{r.price.toLocaleString('en-IN')}</td>
                  <td className="px-3 py-2"><ChangeBadge value={r.change_pct} /></td>
                  <td className="mono px-3 py-2">{r.relative_volume.toFixed(2)}x</td>
                  <td className="mono px-3 py-2">{r.rsi_14?.toFixed(1) ?? '—'}</td>
                  <td className="px-3 py-2">{r.above_vwap === null ? '—' : <Badge tone={r.above_vwap ? 'good' : 'bad'}>{r.above_vwap ? 'above' : 'below'}</Badge>}</td>
                  <td className="px-3 py-2"><Badge tone={r.volume_classification === 'normal' ? 'neutral' : 'warn'}>{r.volume_classification}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type Quote } from '../lib/api'
import { ChangeBadge, ErrorState, LoadingState } from '../components/ui/primitives'

type SortKey = 'symbol' | 'price' | 'change_pct' | 'relative_volume' | 'sector'

export function Markets() {
  const { data, isLoading, isError, error } = useQuery({ queryKey: ['stocks'], queryFn: api.stocks, refetchInterval: 15000 })
  const [sortKey, setSortKey] = useState<SortKey>('change_pct')
  const [sortDir, setSortDir] = useState<1 | -1>(-1)
  const [search, setSearch] = useState('')

  const rows = useMemo(() => {
    let items: Quote[] = data?.items ?? []
    if (search.trim()) {
      const q = search.trim().toUpperCase()
      items = items.filter((r) => r.symbol.includes(q) || r.name.toUpperCase().includes(q))
    }
    return [...items].sort((a, b) => {
      const av = a[sortKey]
      const bv = b[sortKey]
      if (typeof av === 'string' && typeof bv === 'string') return av.localeCompare(bv) * sortDir
      return ((av as number) - (bv as number)) * sortDir
    })
  }, [data, sortKey, sortDir, search])

  function toggleSort(key: SortKey) {
    if (key === sortKey) {
      setSortDir((d) => (d === 1 ? -1 : 1))
    } else {
      setSortKey(key)
      setSortDir(-1)
    }
  }

  const columns: { key: SortKey; label: string }[] = [
    { key: 'symbol', label: 'Symbol' },
    { key: 'sector', label: 'Sector' },
    { key: 'price', label: 'Price' },
    { key: 'change_pct', label: 'Chg %' },
    { key: 'relative_volume', label: 'Rel. Vol' },
  ]

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h1 className="text-lg font-semibold">Markets</h1>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search symbol or name…"
          className="w-64 rounded border border-slate-800 bg-slate-900 px-3 py-1.5 text-sm outline-none focus:border-slate-600"
        />
      </div>
      {isLoading && <LoadingState label="Loading market universe…" />}
      {isError && <ErrorState message={(error as Error).message} />}
      {data && (
        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-sm">
            <thead className="bg-slate-900 text-left text-xs uppercase text-slate-500">
              <tr>
                {columns.map((c) => (
                  <th key={c.key} className="cursor-pointer select-none px-3 py-2" onClick={() => toggleSort(c.key)}>
                    {c.label} {sortKey === c.key ? (sortDir === 1 ? '▲' : '▼') : ''}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.symbol} className="border-t border-slate-900 hover:bg-slate-900/60">
                  <td className="px-3 py-2">
                    <Link to={`/stocks/${r.symbol}`} className="mono font-medium text-slate-100 hover:underline">
                      {r.symbol}
                    </Link>
                    <div className="text-[11px] text-slate-500">{r.name}</div>
                  </td>
                  <td className="px-3 py-2 text-slate-400">{r.sector}</td>
                  <td className="mono px-3 py-2">₹{r.price.toLocaleString('en-IN')}</td>
                  <td className="px-3 py-2"><ChangeBadge value={r.change_pct} /></td>
                  <td className="mono px-3 py-2 text-slate-400">{r.relative_volume.toFixed(2)}x</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { api, ApiError, type RiskRequest, type RiskResult } from '../lib/api'
import { Card, CardTitle, ErrorState } from '../components/ui/primitives'

const initial: RiskRequest = {
  account_size: 500000,
  max_risk_pct: 1,
  entry: 100,
  stop_loss: 95,
  target: 115,
  lot_size: 1,
}

export function RiskCalculator() {
  const [form, setForm] = useState<RiskRequest>(initial)
  const mutation = useMutation<RiskResult, ApiError, RiskRequest>({
    mutationFn: api.calculateRisk,
  })

  function update<K extends keyof RiskRequest>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value === '' ? undefined : Number(value) }) as RiskRequest)
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-semibold">Risk Calculator</h1>
        <p className="text-xs text-slate-500">
          Pure position-sizing math. MarketPulse never places trades automatically — this only computes
          quantities and monetary risk from the numbers you enter.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardTitle>Inputs</CardTitle>
          <form
            className="space-y-3"
            onSubmit={(e) => {
              e.preventDefault()
              mutation.mutate(form)
            }}
          >
            {([
              ['account_size', 'Account size (₹)'],
              ['max_risk_pct', 'Max risk per trade (%)'],
              ['entry', 'Entry price'],
              ['stop_loss', 'Stop loss'],
              ['target', 'Target (optional)'],
              ['lot_size', 'Lot size'],
            ] as [keyof RiskRequest, string][]).map(([key, label]) => (
              <label key={key} className="block text-sm">
                <span className="mb-1 block text-slate-400">{label}</span>
                <input
                  type="number"
                  value={form[key] ?? ''}
                  onChange={(e) => update(key, e.target.value)}
                  className="w-full rounded border border-slate-700 bg-slate-900 px-2 py-1.5"
                  step="any"
                />
              </label>
            ))}
            <button type="submit" className="w-full rounded bg-sky-600 py-2 text-sm font-medium hover:bg-sky-500" disabled={mutation.isPending}>
              {mutation.isPending ? 'Calculating…' : 'Calculate'}
            </button>
          </form>
        </Card>

        <Card>
          <CardTitle>Result</CardTitle>
          {mutation.isError && <ErrorState message={mutation.error.message} />}
          {mutation.data && (
            <dl className="grid grid-cols-2 gap-y-2 text-sm">
              <dt className="text-slate-500">Max monetary risk</dt>
              <dd className="mono text-right">₹{mutation.data.max_monetary_risk.toLocaleString('en-IN')}</dd>
              <dt className="text-slate-500">Risk per unit</dt>
              <dd className="mono text-right">₹{mutation.data.risk_per_unit}</dd>
              <dt className="text-slate-500">Max quantity</dt>
              <dd className="mono text-right">{mutation.data.max_quantity}</dd>
              <dt className="text-slate-500">Max lots</dt>
              <dd className="mono text-right">{mutation.data.max_lots}</dd>
              <dt className="text-slate-500">Position value</dt>
              <dd className="mono text-right">₹{mutation.data.position_size_value.toLocaleString('en-IN')}</dd>
              <dt className="text-slate-500">Potential loss</dt>
              <dd className="mono text-right text-red-400">₹{mutation.data.potential_loss.toLocaleString('en-IN')}</dd>
              {mutation.data.potential_profit != null && (
                <>
                  <dt className="text-slate-500">Potential profit</dt>
                  <dd className="mono text-right text-emerald-400">₹{mutation.data.potential_profit.toLocaleString('en-IN')}</dd>
                </>
              )}
              {mutation.data.risk_reward_ratio != null && (
                <>
                  <dt className="text-slate-500">Risk/reward</dt>
                  <dd className="mono text-right">{mutation.data.risk_reward_ratio}:1</dd>
                </>
              )}
            </dl>
          )}
          {mutation.data && mutation.data.warnings.length > 0 && (
            <ul className="mt-3 space-y-1 border-t border-slate-800 pt-3 text-xs text-amber-400">
              {mutation.data.warnings.map((w) => <li key={w}>⚠ {w}</li>)}
            </ul>
          )}
          {!mutation.data && !mutation.isError && <p className="text-sm text-slate-600">Enter values and calculate to see results.</p>}
        </Card>
      </div>
    </div>
  )
}

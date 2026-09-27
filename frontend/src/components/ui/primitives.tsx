import clsx from 'clsx'
import type { ReactNode } from 'react'

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={clsx('rounded-lg border border-slate-800 bg-[var(--color-terminal-panel)] p-4', className)}>
      {children}
    </div>
  )
}

export function CardTitle({ children, className }: { children: ReactNode; className?: string }) {
  return <h3 className={clsx('mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400', className)}>{children}</h3>
}

export function ChangeBadge({ value, className }: { value: number; className?: string }) {
  const positive = value > 0
  const flat = value === 0
  return (
    <span
      className={clsx(
        'mono rounded px-1.5 py-0.5 text-xs font-medium',
        flat && 'bg-slate-800 text-slate-300',
        positive && 'bg-emerald-950 text-emerald-400',
        !positive && !flat && 'bg-red-950 text-red-400',
        className,
      )}
    >
      {positive ? '+' : ''}
      {value.toFixed(2)}%
    </span>
  )
}

export function Badge({ children, tone = 'neutral' }: { children: ReactNode; tone?: 'neutral' | 'good' | 'bad' | 'warn' }) {
  const tones: Record<string, string> = {
    neutral: 'bg-slate-800 text-slate-300',
    good: 'bg-emerald-950 text-emerald-400',
    bad: 'bg-red-950 text-red-400',
    warn: 'bg-amber-950 text-amber-400',
  }
  return <span className={clsx('rounded px-1.5 py-0.5 text-[11px] font-medium uppercase tracking-wide', tones[tone])}>{children}</span>
}

export function DemoBanner() {
  return (
    <div className="flex items-center gap-2 border-b border-amber-900/50 bg-amber-950/40 px-4 py-1.5 text-xs font-medium text-amber-400">
      <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-amber-400" />
      DEMO MODE — NOT LIVE MARKET DATA. All prices, volumes and news are synthetic/deterministic sample data.
    </div>
  )
}

export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex items-center justify-center py-16 text-sm text-slate-500">
      <span className="mr-2 inline-block h-3 w-3 animate-spin rounded-full border-2 border-slate-600 border-t-slate-300" />
      {label}
    </div>
  )
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-md border border-red-900/60 bg-red-950/30 px-4 py-3 text-sm text-red-400">
      Failed to load data: {message}
    </div>
  )
}

export function EmptyState({ message }: { message: string }) {
  return <div className="rounded-md border border-dashed border-slate-800 px-4 py-8 text-center text-sm text-slate-500">{message}</div>
}

export function DataFreshness({ timestamp }: { timestamp: string }) {
  const date = new Date(timestamp)
  const ageMs = Date.now() - date.getTime()
  const isStale = ageMs > 5 * 60 * 1000
  return (
    <span className={clsx('mono text-[11px]', isStale ? 'text-amber-500' : 'text-slate-500')}>
      {isStale ? 'DATA STALE · ' : ''}
      updated {date.toLocaleTimeString()}
    </span>
  )
}

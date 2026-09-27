import clsx from 'clsx'
import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { DemoBanner } from '../ui/primitives'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard' },
  { to: '/markets', label: 'Markets' },
  { to: '/screener', label: 'Screener' },
  { to: '/signals', label: 'Signals' },
  { to: '/risk', label: 'Risk Calculator' },
]

const ROADMAP_ITEMS = [
  'Options', 'Futures', 'Corporate Events', 'IPO Intelligence', 'AI Research',
  'Backtesting', 'Strategy Lab', 'Paper Trading', 'Portfolio', 'Alerts',
]

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen flex-col">
      <DemoBanner />
      <div className="flex flex-1 overflow-hidden">
        <aside className="hidden w-56 shrink-0 flex-col border-r border-slate-800 bg-[var(--color-terminal-panel)] md:flex">
          <div className="border-b border-slate-800 px-4 py-4">
            <div className="text-sm font-bold tracking-tight text-slate-100">MARKETPULSE AI</div>
            <div className="text-[11px] text-slate-500">v0.1.0 · demo build</div>
          </div>
          <nav className="flex-1 overflow-y-auto px-2 py-3">
            <div className="mb-1 px-2 text-[10px] font-semibold uppercase tracking-wider text-slate-600">Live</div>
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  clsx(
                    'mb-0.5 block rounded px-2 py-1.5 text-sm transition-colors',
                    isActive ? 'bg-slate-800 text-white' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200',
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
            <div className="mb-1 mt-4 px-2 text-[10px] font-semibold uppercase tracking-wider text-slate-600">
              Roadmap (not yet built)
            </div>
            {ROADMAP_ITEMS.map((label) => (
              <div key={label} className="mb-0.5 flex items-center justify-between rounded px-2 py-1.5 text-sm text-slate-600">
                {label}
                <span className="text-[9px] text-slate-700">soon</span>
              </div>
            ))}
          </nav>
          <div className="border-t border-slate-800 px-4 py-3 text-[11px] text-slate-600">
            <a
              className="hover:text-slate-400"
              href="https://github.com/anuragpatwari591-hub/marketpulse-ai"
              target="_blank"
              rel="noreferrer"
            >
              GitHub Repository ↗
            </a>
          </div>
        </aside>
        <main className="flex-1 overflow-y-auto bg-[var(--color-terminal-bg)] p-4 md:p-6">{children}</main>
      </div>
    </div>
  )
}

import { create } from 'zustand'

interface WatchlistState {
  symbols: string[]
  add: (symbol: string) => void
  remove: (symbol: string) => void
  toggle: (symbol: string) => void
}

const STORAGE_KEY = 'marketpulse.watchlist'

function loadInitial(): string[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {
    // ignore - fall back to default watchlist
  }
  return ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY']
}

function persist(symbols: string[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(symbols))
  } catch {
    // ignore - non-fatal, e.g. private browsing storage restrictions
  }
}

export const useWatchlist = create<WatchlistState>((set, get) => ({
  symbols: loadInitial(),
  add: (symbol) => {
    if (get().symbols.includes(symbol)) return
    const next = [...get().symbols, symbol]
    set({ symbols: next })
    persist(next)
  },
  remove: (symbol) => {
    const next = get().symbols.filter((s) => s !== symbol)
    set({ symbols: next })
    persist(next)
  },
  toggle: (symbol) => {
    if (get().symbols.includes(symbol)) {
      get().remove(symbol)
    } else {
      get().add(symbol)
    }
  },
}))

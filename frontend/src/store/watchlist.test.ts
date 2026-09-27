import { beforeEach, describe, expect, it } from 'vitest'
import { useWatchlist } from './watchlist'

describe('watchlist store', () => {
  beforeEach(() => {
    localStorage.clear()
    useWatchlist.setState({ symbols: ['RELIANCE', 'TCS'] })
  })

  it('adds a new symbol without duplicating', () => {
    useWatchlist.getState().add('INFY')
    useWatchlist.getState().add('INFY')
    expect(useWatchlist.getState().symbols.filter((s) => s === 'INFY')).toHaveLength(1)
  })

  it('removes a symbol', () => {
    useWatchlist.getState().remove('TCS')
    expect(useWatchlist.getState().symbols).not.toContain('TCS')
  })

  it('toggle adds when absent and removes when present', () => {
    useWatchlist.getState().toggle('HDFCBANK')
    expect(useWatchlist.getState().symbols).toContain('HDFCBANK')
    useWatchlist.getState().toggle('HDFCBANK')
    expect(useWatchlist.getState().symbols).not.toContain('HDFCBANK')
  })

  it('persists to localStorage', () => {
    useWatchlist.getState().add('SBIN')
    const raw = localStorage.getItem('marketpulse.watchlist')
    expect(raw).toContain('SBIN')
  })
})

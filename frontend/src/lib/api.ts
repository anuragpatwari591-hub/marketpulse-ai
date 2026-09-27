const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail ?? detail
    } catch {
      // ignore body parse failure
    }
    throw new ApiError(detail, res.status)
  }
  return res.json() as Promise<T>
}

export interface Quote {
  symbol: string
  name: string
  sector: string
  price: number
  change: number
  change_pct: number
  open: number
  high: number
  low: number
  prev_close: number
  volume: number
  avg_volume_20d: number
  relative_volume: number
  is_demo: boolean
  last_updated: string
}

export interface IndexQuote {
  symbol: string
  name: string
  price: number
  change: number
  change_pct: number
  is_demo: boolean
  last_updated: string
}

export interface Candle {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface Breadth {
  advances: number
  declines: number
  unchanged: number
  is_demo: boolean
  last_updated: string
}

export interface SectorPerf {
  sector: string
  avg_change_pct: number
  advances: number
  declines: number
  constituent_count: number
}

export interface AnomalyItem {
  symbol: string
  anomaly_score: number
  flags: string[]
  volume_classification: string
  relative_volume: number | null
}

export interface NewsArticle {
  id: string
  headline: string
  source: string
  timestamp: string
  symbol?: string
  sector?: string
  event_type: string
  sentiment: string
  importance: number
  summary: string
  is_demo: boolean
}

export interface FactorContribution {
  factor: string
  weight_pct: number
  raw_score: number
  weighted_score: number
  evidence: string
}

export interface Signal {
  symbol: string
  direction: string
  score: number
  label: string
  contributions: FactorContribution[]
  risks: string[]
  invalidation: string
  scenarios: string[]
  timestamp: string
  data_freshness: string
  sources: string[]
  is_demo: boolean
  disclaimer: string
}

export interface StockAnalysis {
  is_demo: boolean
  symbol: string
  as_of: string
  price: number
  indicators: Record<string, number | null>
  levels: Record<string, number>
  gap: { gap_pct: number; gap_type: string }
  volume: Record<string, unknown>
}

export interface ScreenerItem {
  symbol: string
  name: string
  sector: string
  price: number
  change_pct: number
  relative_volume: number
  rsi_14: number | null
  above_vwap: boolean | null
  volume_classification: string
}

export interface RiskRequest {
  account_size: number
  max_risk_pct: number
  entry: number
  stop_loss: number
  target?: number
  lot_size: number
}

export interface RiskResult {
  max_monetary_risk: number
  risk_per_unit: number
  max_quantity: number
  max_lots: number
  position_size_value: number
  potential_loss: number
  potential_profit: number | null
  risk_reward_ratio: number | null
  warnings: string[]
}

export interface SystemStatus {
  application: string
  version: string
  environment: string
  timestamp: string
  database: { status: string; note: string }
  redis: { status: string; note: string }
  providers: Record<string, { mode: string; live: boolean; reason?: string }>
  workers: { status: string; note: string }
  websocket: { status: string; endpoints: string[] }
}

export const api = {
  systemStatus: () => request<SystemStatus>('/system/status'),
  indices: () => request<{ is_demo: boolean; items: IndexQuote[] }>('/market/indices'),
  breadth: () => request<Breadth>('/market/breadth'),
  movers: (limit = 5) => request<{ gainers: Quote[]; losers: Quote[] }>(`/market/movers?limit=${limit}`),
  sectors: () => request<{ items: SectorPerf[] }>('/market/sectors'),
  anomalies: (limit = 10) => request<{ items: AnomalyItem[] }>(`/market/anomalies?limit=${limit}`),
  regime: () => request<Record<string, unknown>>('/market/regime'),
  stocks: () => request<{ items: Quote[] }>('/stocks'),
  stock: (symbol: string) => request<Quote>(`/stocks/${symbol}`),
  candles: (symbol: string, days = 180) => request<{ items: Candle[] }>(`/stocks/${symbol}/candles?days=${days}`),
  analysis: (symbol: string) => request<StockAnalysis>(`/stocks/${symbol}/analysis`),
  stockNews: (symbol: string) => request<{ items: NewsArticle[] }>(`/stocks/${symbol}/news`),
  news: (limit = 20) => request<{ items: NewsArticle[] }>(`/news?limit=${limit}`),
  screener: (params: URLSearchParams) => request<{ items: ScreenerItem[]; count: number }>(`/screener?${params.toString()}`),
  signal: (symbol: string) => request<Signal>(`/signals/${symbol}`),
  topSignals: (limit = 10) => request<{ items: Signal[] }>(`/signals?limit=${limit}`),
  calculateRisk: (payload: RiskRequest) =>
    request<RiskResult>('/risk/calculate', { method: 'POST', body: JSON.stringify(payload) }),
}

export function wsUrl(path: string): string {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${window.location.host}${path}`
}

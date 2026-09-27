import { CandlestickSeries, ColorType, createChart, type IChartApi } from 'lightweight-charts'
import { useEffect, useRef } from 'react'
import type { Candle } from '../lib/api'

export function StockChart({ candles }: { candles: Candle[] }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const chart = createChart(containerRef.current, {
      layout: { background: { type: ColorType.Solid, color: 'transparent' }, textColor: '#94a3b8' },
      grid: { vertLines: { color: '#1e2733' }, horzLines: { color: '#1e2733' } },
      width: containerRef.current.clientWidth,
      height: 360,
      timeScale: { borderColor: '#1e2733' },
      rightPriceScale: { borderColor: '#1e2733' },
    })
    chartRef.current = chart

    const series = chart.addSeries(CandlestickSeries, {
      upColor: '#16c784',
      downColor: '#ea3943',
      borderVisible: false,
      wickUpColor: '#16c784',
      wickDownColor: '#ea3943',
    })

    series.setData(
      candles.map((c) => ({
        time: (new Date(c.timestamp).getTime() / 1000) as unknown as import('lightweight-charts').UTCTimestamp,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      })),
    )
    chart.timeScale().fitContent()

    const handleResize = () => {
      if (containerRef.current) chart.applyOptions({ width: containerRef.current.clientWidth })
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [candles])

  return <div ref={containerRef} className="w-full" data-testid="stock-chart" />
}

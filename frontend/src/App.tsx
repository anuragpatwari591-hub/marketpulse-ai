import { Route, Routes } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { Dashboard } from './pages/Dashboard'
import { Markets } from './pages/Markets'
import { StockDetail } from './pages/StockDetail'
import { Screener } from './pages/Screener'
import { Signals } from './pages/Signals'
import { SignalDetail } from './pages/SignalDetail'
import { RiskCalculator } from './pages/RiskCalculator'
import { NotFound } from './pages/NotFound'

export function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/markets" element={<Markets />} />
        <Route path="/stocks/:symbol" element={<StockDetail />} />
        <Route path="/screener" element={<Screener />} />
        <Route path="/signals" element={<Signals />} />
        <Route path="/signals/:symbol" element={<SignalDetail />} />
        <Route path="/risk" element={<RiskCalculator />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  )
}

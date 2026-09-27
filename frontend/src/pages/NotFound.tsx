import { Link } from 'react-router-dom'

export function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <div className="text-4xl font-bold text-slate-700">404</div>
      <p className="mt-2 text-sm text-slate-500">This page doesn't exist yet.</p>
      <Link to="/" className="mt-4 text-sm text-sky-400 hover:underline">← Back to dashboard</Link>
    </div>
  )
}

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { ChangeBadge, DemoBanner, Badge } from './primitives'

describe('ChangeBadge', () => {
  it('renders positive change with a plus sign', () => {
    render(<ChangeBadge value={1.23} />)
    expect(screen.getByText('+1.23%')).toBeInTheDocument()
  })

  it('renders negative change without a plus sign', () => {
    render(<ChangeBadge value={-2.5} />)
    expect(screen.getByText('-2.50%')).toBeInTheDocument()
  })

  it('renders zero change as flat', () => {
    render(<ChangeBadge value={0} />)
    expect(screen.getByText('0.00%')).toBeInTheDocument()
  })
})

describe('DemoBanner', () => {
  it('always states this is not live data', () => {
    render(<DemoBanner />)
    expect(screen.getByText(/DEMO MODE/)).toBeInTheDocument()
    expect(screen.getByText(/NOT LIVE MARKET DATA/)).toBeInTheDocument()
  })
})

describe('Badge', () => {
  it('renders children', () => {
    render(<Badge tone="good">Elevated</Badge>)
    expect(screen.getByText('Elevated')).toBeInTheDocument()
  })
})

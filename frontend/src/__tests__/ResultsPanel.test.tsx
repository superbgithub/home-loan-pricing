import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { ResultsPanel } from '../components/ResultsPanel/ResultsPanel'
import type { PricingResultDisplay } from '../types/pricing'

const RESULT: PricingResultDisplay = {
  scenarioId: 'test',
  loanType: 'fixed',
  loanAmount: '320000.00',
  monthlyPayment: '2022.62',
  apr: '6.500',
  totalInterest: '408143.20',
  rateTypeLabel: 'Fixed 30-year',
}

describe('ResultsPanel', () => {
  it('renders the rate-type label', () => {
    render(<ResultsPanel result={RESULT} />)
    expect(screen.getByText('Fixed 30-year')).toBeInTheDocument()
  })

  it('renders monthly payment with $ prefix', () => {
    render(<ResultsPanel result={RESULT} />)
    expect(screen.getByText('$2,022.62')).toBeInTheDocument()
  })

  it('renders APR with % suffix', () => {
    render(<ResultsPanel result={RESULT} />)
    expect(screen.getByText('6.500%')).toBeInTheDocument()
  })

  it('renders total interest with $ prefix', () => {
    render(<ResultsPanel result={RESULT} />)
    expect(screen.getByText('$408,143.20')).toBeInTheDocument()
  })

  it('renders loan amount', () => {
    render(<ResultsPanel result={RESULT} />)
    expect(screen.getByText('$320,000.00')).toBeInTheDocument()
  })
})

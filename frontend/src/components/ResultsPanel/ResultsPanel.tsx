import type { PricingResultDisplay } from '../../types/pricing'
import styles from './ResultsPanel.module.css'

function formatCurrency(value: string): string {
  const num = parseFloat(value)
  return '$' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatApr(value: string): string {
  return value + '%'
}

interface ResultsPanelProps {
  result: PricingResultDisplay
}

export function ResultsPanel({ result }: ResultsPanelProps) {
  return (
    <div className={styles.panel}>
      <h3 className={styles.label}>{result.rateTypeLabel}</h3>
      <dl className={styles.grid}>
        <dt>Monthly Payment</dt>
        <dd>{formatCurrency(result.monthlyPayment)}</dd>
        <dt>APR</dt>
        <dd>{formatApr(result.apr)}</dd>
        <dt>Total Interest</dt>
        <dd>{formatCurrency(result.totalInterest)}</dd>
        <dt>Loan Amount</dt>
        <dd>{formatCurrency(result.loanAmount)}</dd>
      </dl>
    </div>
  )
}

import { useState } from 'react'
import { ScenarioForm } from '../ScenarioForm/ScenarioForm'
import { ResultsPanel } from '../ResultsPanel/ResultsPanel'
import type { ScenarioFormValues, ScenarioPanelState, PricingResultDisplay } from '../../types/pricing'
import { DEFAULT_FORM_VALUES } from '../../types/pricing'
import { priceFixed, priceArm } from '../../services/pricingApi'
import styles from './ScenarioPanel.module.css'

function toPricingResultDisplay(r: any): PricingResultDisplay {
  return {
    scenarioId: r.scenario_id,
    loanType: r.loan_type,
    loanAmount: r.loan_amount,
    monthlyPayment: r.monthly_payment,
    apr: r.apr,
    totalInterest: r.total_interest,
    rateTypeLabel: r.rate_type_label,
  }
}

interface ScenarioPanelProps {
  state: ScenarioPanelState
  onResult: (result: PricingResultDisplay) => void
  onError: (message: string) => void
  onLoading: (loading: boolean) => void
}

export function ScenarioPanel(_props: ScenarioPanelProps) {
  const [result, setResult] = useState<PricingResultDisplay | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (values: ScenarioFormValues) => {
    setLoading(true)
    setError(null)
    try {
      let raw: any
      if (values.productType === 'fixed') {
        raw = await priceFixed({
          home_price: values.homePrice,
          down_payment: values.downPayment,
          term_years: parseInt(values.termYears, 10),
          annual_rate: values.annualRate,
        })
      } else {
        raw = await priceArm({
          home_price: values.homePrice,
          down_payment: values.downPayment,
          term_years: parseInt(values.termYears, 10),
          initial_rate: values.initialRate,
          arm_params: {
            fixed_period_years: parseInt(values.armParams.fixedPeriodYears, 10),
            adjustment_period_years: parseInt(values.armParams.adjustmentPeriodYears, 10),
            initial_cap: values.armParams.initialCap,
            periodic_cap: values.armParams.periodicCap,
            lifetime_cap: values.armParams.lifetimeCap,
          },
        })
      }
      setResult(toPricingResultDisplay(raw))
    } catch (err: any) {
      setError(err.message ?? 'An unexpected error occurred. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.panel}>
      {loading && <div className={styles.loading} aria-label="Loading" role="status">Loading…</div>}
      {error && (
        <div className={styles.errorBanner} role="alert">
          {error}
        </div>
      )}
      <ScenarioForm
        defaultValues={DEFAULT_FORM_VALUES}
        onSubmit={handleSubmit}
        disabled={loading}
      />
      {result && <ResultsPanel result={result} />}
    </div>
  )
}

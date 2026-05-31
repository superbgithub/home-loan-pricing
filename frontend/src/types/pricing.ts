export type ProductType = 'fixed' | 'arm'
export type AppMode = 'single' | 'comparison'

export interface ArmParamsForm {
  fixedPeriodYears: string
  adjustmentPeriodYears: string
  initialCap: string
  periodicCap: string
  lifetimeCap: string
}

export interface ScenarioFormValues {
  productType: ProductType
  homePrice: string
  downPayment: string
  termYears: string
  annualRate: string
  initialRate: string
  armParams: ArmParamsForm
}

export interface PricingResultDisplay {
  scenarioId: string
  loanType: string
  loanAmount: string
  monthlyPayment: string
  apr: string
  totalInterest: string
  rateTypeLabel: string
}

export interface ScenarioPanelState {
  id: 'a' | 'b'
  result: PricingResultDisplay | null
  error: string | null
  loading: boolean
}

export interface AppState {
  mode: AppMode
  scenarioA: ScenarioPanelState
  scenarioB: ScenarioPanelState | null
}

export const DEFAULT_FORM_VALUES: ScenarioFormValues = {
  productType: 'fixed',
  homePrice: '',
  downPayment: '',
  termYears: '30',
  annualRate: '',
  initialRate: '',
  armParams: {
    fixedPeriodYears: '5',
    adjustmentPeriodYears: '1',
    initialCap: '',
    periodicCap: '',
    lifetimeCap: '',
  },
}

export const DEFAULT_PANEL_STATE = (id: 'a' | 'b'): ScenarioPanelState => ({
  id,
  result: null,
  error: null,
  loading: false,
})

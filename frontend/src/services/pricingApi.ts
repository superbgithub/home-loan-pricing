export class PricingApiError extends Error {
  constructor(
    public readonly status: number,
    message: string
  ) {
    super(message)
    this.name = 'PricingApiError'
  }
}

export interface PriceFixedRequest {
  home_price: string
  down_payment: string
  term_years: number
  annual_rate: string
  fee_schedule?: { fees: [] }
  scenario_id?: string
}

export interface ArmParamsRequest {
  fixed_period_years: number
  adjustment_period_years: number
  initial_cap: string
  periodic_cap: string
  lifetime_cap: string
}

export interface PriceArmRequest {
  home_price: string
  down_payment: string
  term_years: number
  initial_rate: string
  arm_params: ArmParamsRequest
  fee_schedule?: { fees: [] }
  scenario_id?: string
}

export interface PriceResponse {
  scenario_id: string
  loan_type: string
  loan_amount: string
  monthly_payment: string
  apr: string
  total_interest: string
  rate_type_label: string
  parameters_summary: Record<string, unknown>
}

export interface PriceErrorResponse {
  scenario_id: string
  error: true
  code: string
  message: string
}

export type CompareScenario =
  | (PriceFixedRequest & { loan_type: 'fixed' })
  | (PriceArmRequest & { loan_type: 'arm' })

export interface CompareRequest {
  scenarios: CompareScenario[]
  comparison_id?: string
}

export interface CompareResponse {
  comparison_id: string
  results: Array<PriceResponse | PriceErrorResponse>
}

const BASE = '/api/v1'

async function post<T>(path: string, body: unknown): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  } catch {
    throw new PricingApiError(0, 'Unable to reach pricing service')
  }
  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try {
      const data = await response.json()
      if (data?.detail?.[0]?.msg) message = data.detail[0].msg
      else if (data?.detail?.[0]?.message) message = data.detail[0].message
    } catch {
      // keep default message
    }
    throw new PricingApiError(response.status, message)
  }
  return response.json() as Promise<T>
}

export const priceFixed = (req: PriceFixedRequest) =>
  post<PriceResponse>('/price/fixed', req)

export const priceArm = (req: PriceArmRequest) =>
  post<PriceResponse>('/price/arm', req)

export const priceCompare = (req: CompareRequest) =>
  post<CompareResponse>('/price/compare', req)

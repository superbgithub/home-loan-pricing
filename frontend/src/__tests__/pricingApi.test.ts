import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from './setup'
import { priceFixed, priceArm, priceCompare, PricingApiError } from '../services/pricingApi'

describe('priceFixed', () => {
  it('returns a PricingResultDisplay on success', async () => {
    const result = await priceFixed({
      home_price: '400000.00',
      down_payment: '80000.00',
      term_years: 30,
      annual_rate: '6.50',
    })
    expect(result.monthly_payment).toBe('2022.62')
    expect(result.loan_type).toBe('fixed')
  })

  it('throws PricingApiError on non-2xx', async () => {
    server.use(
      http.post('/api/v1/price/fixed', () =>
        HttpResponse.json({ detail: [{ msg: 'bad rate' }] }, { status: 422 })
      )
    )
    await expect(priceFixed({ home_price: '0', down_payment: '0', term_years: 0, annual_rate: '99' }))
      .rejects.toBeInstanceOf(PricingApiError)
  })

  it('throws PricingApiError(0) on network failure', async () => {
    server.use(http.post('/api/v1/price/fixed', () => HttpResponse.error()))
    await expect(priceFixed({ home_price: '400000', down_payment: '80000', term_years: 30, annual_rate: '6.5' }))
      .rejects.toMatchObject({ status: 0 })
  })
})

describe('priceArm', () => {
  it('returns ARM result on success', async () => {
    const result = await priceArm({
      home_price: '350000.00',
      down_payment: '70000.00',
      term_years: 30,
      initial_rate: '5.75',
      arm_params: {
        fixed_period_years: 5,
        adjustment_period_years: 1,
        initial_cap: '2.00',
        periodic_cap: '2.00',
        lifetime_cap: '5.00',
      },
    })
    expect(result.loan_type).toBe('arm')
    expect(result.rate_type_label).toBe('5/1 ARM 30-year')
  })
})

describe('priceCompare', () => {
  it('returns comparison result with results array', async () => {
    const result = await priceCompare({
      scenarios: [
        { loan_type: 'fixed', scenario_id: '30yr', home_price: '400000', down_payment: '80000', term_years: 30, annual_rate: '6.5' },
        { loan_type: 'fixed', scenario_id: '15yr', home_price: '400000', down_payment: '80000', term_years: 15, annual_rate: '6.0' },
      ],
    })
    expect(result.results).toHaveLength(2)
    expect(result.comparison_id).toBeDefined()
  })
})

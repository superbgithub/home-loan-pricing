import '@testing-library/jest-dom/vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { beforeAll, afterEach, afterAll } from 'vitest'

export const FIXED_RESULT = {
  scenario_id: 'test-fixed',
  loan_type: 'fixed',
  loan_amount: '320000.00',
  monthly_payment: '2022.62',
  apr: '6.500',
  total_interest: '408143.20',
  rate_type_label: 'Fixed 30-year',
  parameters_summary: {},
}

export const ARM_RESULT = {
  scenario_id: 'test-arm',
  loan_type: 'arm',
  loan_amount: '280000.00',
  monthly_payment: '1634.00',
  apr: '5.750',
  total_interest: '308240.00',
  rate_type_label: '5/1 ARM 30-year',
  parameters_summary: {},
}

export const server = setupServer(
  http.post('/api/v1/price/fixed', () => HttpResponse.json(FIXED_RESULT)),
  http.post('/api/v1/price/arm', () => HttpResponse.json(ARM_RESULT)),
  http.post('/api/v1/price/compare', ({ request }) =>
    request.json().then((body: any) =>
      HttpResponse.json({
        comparison_id: 'cmp-test',
        results: (body.scenarios as any[]).map((_s, i) =>
          i === 0 ? FIXED_RESULT : { ...FIXED_RESULT, scenario_id: 'test-b', rate_type_label: 'Fixed 15-year' }
        ),
      })
    )
  )
)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

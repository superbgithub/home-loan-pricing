import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from './setup'
import { ScenarioPanel } from '../components/ScenarioPanel/ScenarioPanel'
import { DEFAULT_PANEL_STATE } from '../types/pricing'

const submitFixedForm = async (user: ReturnType<typeof userEvent.setup>) => {
  await user.type(screen.getByLabelText(/home price/i), '400000')
  await user.type(screen.getByLabelText(/down payment/i), '80000')
  await user.selectOptions(screen.getByLabelText(/loan term/i), '30')
  await user.type(screen.getByLabelText(/annual rate/i), '6.5')
  await user.click(screen.getByRole('button', { name: /get quote/i }))
}

describe('ScenarioPanel', () => {
  it('shows results panel after successful API response', async () => {
    const user = userEvent.setup()
    render(<ScenarioPanel state={DEFAULT_PANEL_STATE('a')} onResult={vi.fn()} onError={vi.fn()} onLoading={vi.fn()} />)
    await submitFixedForm(user)
    await waitFor(() => expect(screen.getByText('Fixed 30-year')).toBeInTheDocument())
  })

  it('shows error banner when API returns an error', async () => {
    server.use(http.post('/api/v1/price/fixed', () =>
      HttpResponse.json({ detail: [{ msg: 'service error' }] }, { status: 500 })
    ))
    const user = userEvent.setup()
    render(<ScenarioPanel state={DEFAULT_PANEL_STATE('a')} onResult={vi.fn()} onError={vi.fn()} onLoading={vi.fn()} />)
    await submitFixedForm(user)
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument())
  })
})

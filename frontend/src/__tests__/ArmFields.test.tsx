import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { ScenarioForm } from '../components/ScenarioForm/ScenarioForm'
import { DEFAULT_FORM_VALUES } from '../types/pricing'

describe('ArmFields', () => {
  it('ARM fields are hidden in fixed mode', () => {
    render(<ScenarioForm defaultValues={DEFAULT_FORM_VALUES} onSubmit={vi.fn()} />)
    expect(screen.queryByLabelText(/fixed period/i)).not.toBeInTheDocument()
    expect(screen.queryByLabelText(/adjustment interval/i)).not.toBeInTheDocument()
  })

  it('shows all 5 ARM cap inputs when in ARM mode', async () => {
    const user = userEvent.setup()
    render(<ScenarioForm defaultValues={DEFAULT_FORM_VALUES} onSubmit={vi.fn()} />)
    await user.click(screen.getByRole('button', { name: /adjustable rate/i }))
    expect(screen.getByLabelText(/fixed period/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/adjustment interval/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/initial cap/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/periodic cap/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/lifetime cap/i)).toBeInTheDocument()
  })

  it('shows cross-field error when periodicCap > lifetimeCap', async () => {
    const user = userEvent.setup()
    render(<ScenarioForm defaultValues={DEFAULT_FORM_VALUES} onSubmit={vi.fn()} />)
    await user.click(screen.getByRole('button', { name: /adjustable rate/i }))
    await user.type(screen.getByLabelText(/home price/i), '350000')
    await user.type(screen.getByLabelText(/down payment/i), '70000')
    await user.type(screen.getByLabelText(/initial rate/i), '5.75')
    await user.type(screen.getByLabelText(/fixed period/i), '5')
    await user.type(screen.getByLabelText(/adjustment interval/i), '1')
    await user.type(screen.getByLabelText(/initial cap/i), '2')
    await user.type(screen.getByLabelText(/periodic cap/i), '6')
    await user.type(screen.getByLabelText(/lifetime cap/i), '5')
    await user.click(screen.getByRole('button', { name: /get quote/i }))
    await waitFor(() =>
      expect(screen.getByText(/periodic cap must be ≤ lifetime cap/i)).toBeInTheDocument()
    )
  })
})

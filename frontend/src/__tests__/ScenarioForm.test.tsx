import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { ScenarioForm } from '../components/ScenarioForm/ScenarioForm'
import { DEFAULT_FORM_VALUES } from '../types/pricing'

const fillFixed = async (user: ReturnType<typeof userEvent.setup>) => {
  await user.clear(screen.getByLabelText(/home price/i))
  await user.type(screen.getByLabelText(/home price/i), '400000')
  await user.clear(screen.getByLabelText(/down payment/i))
  await user.type(screen.getByLabelText(/down payment/i), '80000')
  await user.selectOptions(screen.getByLabelText(/loan term/i), '30')
  await user.clear(screen.getByLabelText(/annual rate/i))
  await user.type(screen.getByLabelText(/annual rate/i), '6.5')
}

describe('ScenarioForm — fixed rate', () => {
  it('renders all fixed-rate fields', () => {
    render(<ScenarioForm defaultValues={DEFAULT_FORM_VALUES} onSubmit={vi.fn()} />)
    expect(screen.getByLabelText(/home price/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/down payment/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/loan term/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/annual rate/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /get quote/i })).toBeInTheDocument()
  })

  it('calls onSubmit with valid fixed-rate data', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<ScenarioForm defaultValues={DEFAULT_FORM_VALUES} onSubmit={onSubmit} />)
    await fillFixed(user)
    await user.click(screen.getByRole('button', { name: /get quote/i }))
    await waitFor(() => expect(onSubmit).toHaveBeenCalledOnce())
    expect(onSubmit.mock.calls[0][0].productType).toBe('fixed')
  })

  it('shows error and does not submit when Home Price is blank', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<ScenarioForm defaultValues={DEFAULT_FORM_VALUES} onSubmit={onSubmit} />)
    await user.click(screen.getByRole('button', { name: /get quote/i }))
    await waitFor(() => expect(screen.getByText(/home price is required/i)).toBeInTheDocument())
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('shows error for rate above 30', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<ScenarioForm defaultValues={DEFAULT_FORM_VALUES} onSubmit={onSubmit} />)
    await user.type(screen.getByLabelText(/home price/i), '400000')
    await user.type(screen.getByLabelText(/down payment/i), '80000')
    await user.type(screen.getByLabelText(/annual rate/i), '35')
    await user.click(screen.getByRole('button', { name: /get quote/i }))
    await waitFor(() => expect(screen.getByText(/rate must be between 0 and 30/i)).toBeInTheDocument())
    expect(onSubmit).not.toHaveBeenCalled()
  })
})

describe('ScenarioForm — ARM toggle', () => {
  it('shows ARM fields when toggled to ARM', async () => {
    const user = userEvent.setup()
    render(<ScenarioForm defaultValues={DEFAULT_FORM_VALUES} onSubmit={vi.fn()} />)
    await user.click(screen.getByRole('button', { name: /adjustable rate/i }))
    expect(screen.getByLabelText(/initial rate/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/fixed period/i)).toBeInTheDocument()
  })

  it('preserves shared fields when toggling product type', async () => {
    const user = userEvent.setup()
    render(<ScenarioForm defaultValues={DEFAULT_FORM_VALUES} onSubmit={vi.fn()} />)
    await user.type(screen.getByLabelText(/home price/i), '350000')
    await user.click(screen.getByRole('button', { name: /adjustable rate/i }))
    expect(screen.getByLabelText(/home price/i)).toHaveValue(350000)
  })
})

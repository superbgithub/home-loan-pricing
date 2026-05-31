import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect } from 'vitest'
import App from '../App'

describe('App — single fixed-rate flow', () => {
  it('shows results after filling and submitting fixed form', async () => {
    const user = userEvent.setup()
    render(<App />)
    await user.type(screen.getByLabelText(/home price/i), '400000')
    await user.type(screen.getByLabelText(/down payment/i), '80000')
    await user.selectOptions(screen.getByLabelText(/loan term/i), '30')
    await user.type(screen.getByLabelText(/annual rate/i), '6.5')
    await user.click(screen.getByRole('button', { name: /get quote/i }))
    await waitFor(() => expect(screen.getByText('Fixed 30-year')).toBeInTheDocument())
    expect(screen.getByText('$2,022.62')).toBeInTheDocument()
  })
})

describe('App — comparison mode', () => {
  it('renders two scenario panels in comparison mode', async () => {
    const user = userEvent.setup()
    render(<App />)
    await user.click(screen.getByRole('button', { name: /compare two scenarios/i }))
    expect(screen.getAllByLabelText(/home price/i)).toHaveLength(2)
  })

  it('hides second panel when comparison mode is deactivated', async () => {
    const user = userEvent.setup()
    render(<App />)
    await user.click(screen.getByRole('button', { name: /compare two scenarios/i }))
    await user.click(screen.getByRole('button', { name: /single scenario/i }))
    expect(screen.getAllByLabelText(/home price/i)).toHaveLength(1)
  })
})

import { render, screen } from '../test/utils'
import { useAuth } from './AuthContext'
import { describe, it, expect } from 'vitest'

const TestComponent = () => {
    const { status } = useAuth()
    return <div data-testid="auth-status">Status: {status}</div>
}

describe('AuthContext', () => {
    it('provides initial status', () => {
        render(<TestComponent />)
        expect(screen.getByTestId('auth-status')).toHaveTextContent(/Status:/)
    })
})

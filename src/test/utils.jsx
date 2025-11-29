import React from 'react'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import { WorkspaceProvider } from '../context/WorkspaceContext'
import { ToastProvider } from '../components/Toast'

const AllTheProviders = ({ children }) => {
    return (
        <BrowserRouter>
            <ToastProvider>
                <AuthProvider>
                    <WorkspaceProvider>
                        {children}
                    </WorkspaceProvider>
                </AuthProvider>
            </ToastProvider>
        </BrowserRouter>
    )
}

const customRender = (ui, options) =>
    render(ui, { wrapper: AllTheProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }

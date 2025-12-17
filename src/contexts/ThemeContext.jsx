import React, { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext({
    theme: 'light',
    toggleTheme: () => { },
    setTheme: () => { },
})

export const useTheme = () => {
    const context = useContext(ThemeContext)
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider')
    }
    return context
}

export const ThemeProvider = ({ children }) => {
    const [theme, setThemeState] = useState(() => {
        // Check localStorage first
        if (typeof window !== 'undefined') {
            const stored = localStorage.getItem('raptorflow-theme')
            if (stored === 'dark' || stored === 'light') {
                return stored
            }
            // Check system preference
            if (window.matchMedia?.('(prefers-color-scheme: dark)').matches) {
                return 'dark'
            }
        }
        return 'light'
    })

    const [forceLight, setForceLight] = useState(false)

    useEffect(() => {
        if (typeof window === 'undefined') return

        const update = () => {
            const path = window.location?.pathname || '/'
            const isApp = path.startsWith('/app') || path.startsWith('/onboarding')
            const isMarketing =
                path === '/' ||
                path === '/premium' ||
                path === '/pricing' ||
                path === '/start' ||
                path === '/login' ||
                path === '/signup' ||
                path.startsWith('/product/') ||
                path === '/about' ||
                path === '/blog' ||
                path === '/careers' ||
                path === '/contact' ||
                path === '/privacy' ||
                path === '/terms' ||
                path === '/refunds' ||
                path === '/manifesto' ||
                path === '/faq' ||
                path === '/changelog' ||
                path === '/status' ||
                path === '/cookies'

            const isLanding = !isApp && isMarketing

            setForceLight(isLanding)
        }

        update()
        window.addEventListener('popstate', update)
        return () => window.removeEventListener('popstate', update)
    }, [])

    useEffect(() => {
        // Apply theme to document
        const root = document.documentElement
        if (forceLight) {
            if (theme !== 'light') {
                setThemeState('light')
            }
            root.classList.remove('dark')
            localStorage.setItem('raptorflow-theme', 'light')
            return
        }

        if (theme === 'dark') {
            root.classList.add('dark')
        } else {
            root.classList.remove('dark')
        }
        // Persist to localStorage
        localStorage.setItem('raptorflow-theme', theme)
    }, [theme, forceLight])

    const toggleTheme = () => {
        setThemeState(prev => prev === 'light' ? 'dark' : 'light')
    }

    const setTheme = (newTheme) => {
        if (newTheme === 'light' || newTheme === 'dark') {
            setThemeState(newTheme)
        }
    }

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
            {children}
        </ThemeContext.Provider>
    )
}

export default ThemeContext

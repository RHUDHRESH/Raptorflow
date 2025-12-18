import React from 'react'
import { Sun, Moon } from 'lucide-react'
import { useTheme } from '../../contexts/ThemeContext'

const ThemeToggle = ({ className = '' }) => {
    const { theme, toggleTheme } = useTheme()

    return (
        <button
            onClick={toggleTheme}
            className={`
        relative flex items-center justify-center w-9 h-9 rounded-lg
        bg-muted/50 hover:bg-muted border border-border
        transition-all duration-200 ease-out
        hover:scale-105 active:scale-95
        ${className}
      `}
            title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
            aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
        >
            {/* Sun icon for light mode */}
            <Sun
                className={`
          w-4 h-4 absolute transition-all duration-300
          ${theme === 'light'
                        ? 'opacity-100 rotate-0 scale-100 text-amber-500'
                        : 'opacity-0 rotate-90 scale-0 text-amber-500'
                    }
        `}
                strokeWidth={2}
            />
            {/* Moon icon for dark mode */}
            <Moon
                className={`
          w-4 h-4 absolute transition-all duration-300
          ${theme === 'dark'
                        ? 'opacity-100 rotate-0 scale-100 text-orange-400'
                        : 'opacity-0 -rotate-90 scale-0 text-orange-400'
                    }
        `}
                strokeWidth={2}
            />
        </button>
    )
}

export default ThemeToggle

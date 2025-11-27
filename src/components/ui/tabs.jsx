import React, { createContext, useContext, useState } from 'react'

const TabsContext = createContext()

const Tabs = ({ children, defaultValue, value: controlledValue, onValueChange, className = '' }) => {
    const [internalValue, setInternalValue] = useState(defaultValue)
    const value = controlledValue !== undefined ? controlledValue : internalValue

    const setValue = (newValue) => {
        if (controlledValue === undefined) {
            setInternalValue(newValue)
        }
        onValueChange?.(newValue)
    }

    return (
        <TabsContext.Provider value={{ value, setValue }}>
            <div className={className}>
                {children}
            </div>
        </TabsContext.Provider>
    )
}

const TabsList = React.forwardRef(({ className = '', children, ...props }, ref) => (
    <div
        ref={ref}
        className={`inline-flex h-10 items-center justify-center rounded-md bg-gray-100 p-1 text-gray-500 ${className}`}
        {...props}
    >
        {children}
    </div>
))
TabsList.displayName = 'TabsList'

const TabsTrigger = React.forwardRef(({ className = '', value, children, ...props }, ref) => {
    const { value: selectedValue, setValue } = useContext(TabsContext)
    const isActive = selectedValue === value

    return (
        <button
            ref={ref}
            type="button"
            role="tab"
            aria-selected={isActive}
            data-state={isActive ? 'active' : 'inactive'}
            onClick={() => setValue(value)}
            className={`inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${isActive ? 'bg-white text-gray-950 shadow-sm' : ''
                } ${className}`}
            {...props}
        >
            {children}
        </button>
    )
})
TabsTrigger.displayName = 'TabsTrigger'

const TabsContent = React.forwardRef(({ className = '', value, children, ...props }, ref) => {
    const { value: selectedValue } = useContext(TabsContext)

    if (selectedValue !== value) return null

    return (
        <div
            ref={ref}
            role="tabpanel"
            className={`mt-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-950 focus-visible:ring-offset-2 ${className}`}
            {...props}
        >
            {children}
        </div>
    )
})
TabsContent.displayName = 'TabsContent'

export { Tabs, TabsList, TabsTrigger, TabsContent }

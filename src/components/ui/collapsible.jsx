import * as React from "react"
import { cn } from "../../utils/cn"

const CollapsibleContext = React.createContext({
  open: false,
  onOpenChange: () => {},
})

const Collapsible = ({ open: openProp, defaultOpen, onOpenChange, children, ...props }) => {
  const [open, setOpen] = React.useState(defaultOpen ?? false)
  const isControlled = openProp !== undefined
  const isOpen = isControlled ? openProp : open
  
  const handleOpenChange = React.useCallback((newOpen) => {
    if (!isControlled) {
      setOpen(newOpen)
    }
    onOpenChange?.(newOpen)
  }, [isControlled, onOpenChange])
  
  return (
    <CollapsibleContext.Provider value={{ open: isOpen, onOpenChange: handleOpenChange }}>
      <div data-state={isOpen ? "open" : "closed"} {...props}>
        {children}
      </div>
    </CollapsibleContext.Provider>
  )
}

const CollapsibleTrigger = React.forwardRef(({ className, asChild = false, children, ...props }, ref) => {
  const { open, onOpenChange } = React.useContext(CollapsibleContext)
  
  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children, {
      onClick: () => onOpenChange(!open),
      ref,
      ...props
    })
  }
  
  return (
    <button
      ref={ref}
      type="button"
      onClick={() => onOpenChange(!open)}
      className={cn("transition-all duration-180", className)}
      {...props}
    >
      {children}
    </button>
  )
})
CollapsibleTrigger.displayName = "CollapsibleTrigger"

const CollapsibleContent = React.forwardRef(({ className, ...props }, ref) => {
  const { open } = React.useContext(CollapsibleContext)
  
  if (!open) return null
  
  return (
    <div
      ref={ref}
      className={cn("overflow-hidden animate-in", className)}
      {...props}
    />
  )
})
CollapsibleContent.displayName = "CollapsibleContent"

export { Collapsible, CollapsibleContent, CollapsibleTrigger }

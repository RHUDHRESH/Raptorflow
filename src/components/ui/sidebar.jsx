import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Menu, X } from "lucide-react"
import { cn } from "../../utils/cn"

const SidebarContext = React.createContext(undefined)

const useSidebar = () => {
  const context = React.useContext(SidebarContext)
  if (context === undefined) {
    throw new Error("useSidebar must be used within a SidebarProvider")
  }
  return context
}

const SidebarProvider = ({ 
  children, 
  open: openProp, 
  setOpen: setOpenProp,
  animate = true,
  defaultOpen = false 
}) => {
  const [openState, setOpenState] = React.useState(defaultOpen)
  const open = openProp !== undefined ? openProp : openState
  const setOpen = setOpenProp !== undefined ? setOpenProp : setOpenState
  
  return (
    <SidebarContext.Provider value={{ open, setOpen, animate }}>
      {children}
    </SidebarContext.Provider>
  )
}

const Sidebar = ({ children, open, setOpen, animate, ...props }) => {
  return (
    <SidebarProvider open={open} setOpen={setOpen} animate={animate}>
      {children}
    </SidebarProvider>
  )
}
Sidebar.displayName = "Sidebar"

const DesktopSidebar = React.forwardRef(({ className, children, ...props }, ref) => {
  const { open, setOpen, animate } = useSidebar()
  
  return (
    <motion.aside
      ref={ref}
      className={cn(
        "fixed left-0 top-0 z-50 h-screen border-r border-neutral-200 bg-white hidden md:flex md:flex-col flex-shrink-0 overflow-hidden",
        className
      )}
      animate={{
        width: animate ? (open ? "256px" : "64px") : "64px",
      }}
      transition={{ duration: 0.2, ease: "easeInOut" }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      {...props}
    >
      {children}
    </motion.aside>
  )
})
DesktopSidebar.displayName = "DesktopSidebar"

const MobileSidebar = React.forwardRef(({ className, children, ...props }, ref) => {
  const { open, setOpen } = useSidebar()
  
  return (
    <>
      <div
        ref={ref}
        className={cn(
          "h-16 px-4 py-4 flex flex-row md:hidden items-center justify-between bg-white border-b border-neutral-200 w-full z-50"
        )}
        {...props}
      >
        <div className="flex justify-end z-20 w-full">
          <Menu
            className="text-neutral-800 cursor-pointer"
            onClick={() => setOpen(!open)}
            size={24}
          />
        </div>
      </div>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ x: "-100%", opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: "-100%", opacity: 0 }}
            transition={{
              duration: 0.3,
              ease: "easeInOut",
            }}
            className={cn(
              "fixed h-full w-full inset-0 bg-white p-10 z-[100] flex flex-col justify-between md:hidden",
              className
            )}
          >
            <div
              className="absolute right-10 top-10 z-50 text-neutral-800 cursor-pointer"
              onClick={() => setOpen(false)}
            >
              <X size={24} />
            </div>
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
})
MobileSidebar.displayName = "MobileSidebar"

const SidebarHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex shrink-0 items-center gap-2 border-b px-2 py-3", className)}
    {...props}
  />
))
SidebarHeader.displayName = "SidebarHeader"

const SidebarContent = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex-1 overflow-y-auto overflow-x-hidden p-2 scrollbar-hide", className)}
    {...props}
  />
))
SidebarContent.displayName = "SidebarContent"

const SidebarGroup = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("space-y-1", className)}
    {...props}
  />
))
SidebarGroup.displayName = "SidebarGroup"

const SidebarGroupContent = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("space-y-1", className)}
    {...props}
  />
))
SidebarGroupContent.displayName = "SidebarGroupContent"

const SidebarMenu = React.forwardRef(({ className, ...props }, ref) => (
  <nav
    ref={ref}
    className={cn("space-y-0.5 list-none", className)}
    {...props}
  />
))
SidebarMenu.displayName = "SidebarMenu"

const SidebarMenuItem = React.forwardRef(({ className, ...props }, ref) => (
  <li ref={ref} className={cn("list-none", className)} {...props} />
))
SidebarMenuItem.displayName = "SidebarMenuItem"

const SidebarMenuButton = React.forwardRef(
  ({ className, variant, asChild = false, isActive, children, ...props }, ref) => {
    const baseClasses = "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neutral-900 disabled:pointer-events-none disabled:opacity-50"
    const variantClasses = isActive 
      ? "bg-neutral-900 text-white hover:bg-neutral-800" 
      : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900"
    
    if (asChild && React.isValidElement(children)) {
      const existingClassName = children.props?.className || ""
      return React.cloneElement(children, {
        className: cn(baseClasses, variantClasses, existingClassName, className),
        ref,
        ...props
      })
    }
    
    return (
      <button
        ref={ref}
        className={cn(baseClasses, variantClasses, className)}
        {...props}
      >
        {children}
      </button>
    )
  }
)
SidebarMenuButton.displayName = "SidebarMenuButton"

const SidebarInset = React.forwardRef(({ className, ...props }, ref) => {
  const { open, animate } = useSidebar()
  const [isMobile, setIsMobile] = React.useState(false)
  
  React.useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768)
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])
  
  return (
    <motion.div
      ref={ref}
      className={cn(
        "flex flex-col min-h-screen transition-all duration-200 ease-in-out",
        isMobile && "ml-0",
        className
      )}
      animate={!isMobile ? {
        marginLeft: animate ? (open ? "256px" : "64px") : "64px",
      } : {}}
      transition={{ duration: 0.2, ease: "easeInOut" }}
      {...props}
    />
  )
})
SidebarInset.displayName = "SidebarInset"

const SidebarTrigger = React.forwardRef(({ className, ...props }, ref) => {
  const { open, setOpen } = useSidebar()
  
  return (
    <button
      ref={ref}
      onClick={() => setOpen(!open)}
      className={cn(
        "inline-flex items-center justify-center rounded-md p-2 text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neutral-900 transition-colors",
        className
      )}
      {...props}
    >
      {open ? (
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M11.7816 4.03157C12.0062 3.80702 12.0062 3.44295 11.7816 3.2184C11.5571 2.99385 11.193 2.99385 10.9685 3.2184L7.50005 6.68682L4.03164 3.2184C3.80708 2.99385 3.44301 2.99385 3.21846 3.2184C2.99391 3.44295 2.99391 3.80702 3.21846 4.03157L6.68688 7.49999L3.21846 10.9684C2.99391 11.193 2.99391 11.557 3.21846 11.7816C3.44301 12.0061 3.80708 12.0061 4.03164 11.7816L7.50005 8.31316L10.9685 11.7816C11.193 12.0061 11.5571 12.0061 11.7816 11.7816C12.0062 11.557 12.0062 11.193 11.7816 10.9684L8.31322 7.49999L11.7816 4.03157Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path>
        </svg>
      ) : (
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M1.5 3C1.22386 3 1 3.22386 1 3.5C1 3.77614 1.22386 4 1.5 4H13.5C13.7761 4 14 3.77614 14 3.5C14 3.22386 13.7761 3 13.5 3H1.5ZM1 7.5C1 7.22386 1.22386 7 1.5 7H13.5C13.7761 7 14 7.22386 14 7.5C14 7.77614 13.7761 8 13.5 8H1.5C1.22386 8 1 7.77614 1 7.5ZM1 11.5C1 11.2239 1.22386 11 1.5 11H13.5C13.7761 11 14 11.2239 14 11.5C14 11.7761 13.7761 12 13.5 12H1.5C1.22386 12 1 11.7761 1 11.5Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path>
        </svg>
      )}
    </button>
  )
})
SidebarTrigger.displayName = "SidebarTrigger"

const SidebarInput = React.forwardRef(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      "flex h-9 w-full rounded-md border border-neutral-200 bg-white px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-neutral-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neutral-900 disabled:cursor-not-allowed disabled:opacity-50",
      className
    )}
    {...props}
  />
))
SidebarInput.displayName = "SidebarInput"

const SidebarRail = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("absolute right-0 top-0 h-full w-px bg-neutral-200", className)}
    {...props}
  />
))
SidebarRail.displayName = "SidebarRail"

export {
  Sidebar,
  DesktopSidebar,
  MobileSidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarInput,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarTrigger,
  useSidebar,
}


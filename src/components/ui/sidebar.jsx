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

const DESKTOP_SIDEBAR_WIDTH = 272
const DESKTOP_SIDEBAR_COLLAPSED_WIDTH = 88

const Sidebar = ({ children, open, setOpen, animate }) => {
  return (
    <SidebarProvider open={open} setOpen={setOpen} animate={animate}>
      {children}
    </SidebarProvider>
  )
}
Sidebar.displayName = "Sidebar"

const DesktopSidebar = React.forwardRef(({ className, children, ...props }, ref) => {
  return (
    <aside
      ref={ref}
      className={cn(
        "fixed left-0 top-0 z-50 h-screen border-r border-white/10 bg-black hidden md:flex md:flex-col flex-shrink-0 overflow-hidden",
        className
      )}
      {...props}
    >
      {children}
    </aside>
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
          "h-16 px-4 py-4 flex flex-row md:hidden items-center justify-between bg-white border-b border-black/10 w-full z-50"
        )}
        {...props}
      >
        <div className="flex justify-end z-20 w-full">
          <Menu
            className="text-black cursor-pointer"
            onClick={() => setOpen(!open)}
            size={24}
            strokeWidth={1.5}
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
              ease: [0.4, 0, 0.2, 1],
            }}
            className={cn(
              "fixed h-full w-full inset-0 bg-white p-10 z-[100] flex flex-col justify-between md:hidden",
              className
            )}
          >
            <div
              className="absolute right-10 top-10 z-50 text-black cursor-pointer"
              onClick={() => setOpen(false)}
            >
              <X size={24} strokeWidth={1.5} />
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
    className={cn("flex shrink-0 items-center gap-2 border-b border-white/10 px-6 py-4", className)}
    {...props}
  />
))
SidebarHeader.displayName = "SidebarHeader"

const SidebarContent = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex-1 overflow-y-auto overflow-x-hidden scrollbar-hide", className)}
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
    className={cn("space-y-1 list-none", className)}
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
    const baseClasses = "flex items-center gap-3 rounded px-3 py-2.5 text-sm font-medium transition-all duration-180 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white disabled:pointer-events-none disabled:opacity-50"
    const variantClasses = isActive 
      ? "bg-white text-black" 
      : "text-white/70 hover:bg-white/10 hover:text-white"
    
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
  const { open } = useSidebar()
  const [isMobile, setIsMobile] = React.useState(() => {
    if (typeof window === "undefined") return false
    return window.innerWidth < 768
  })
  
  React.useEffect(() => {
    const checkMobile = () => {
      if (typeof window === "undefined") return
      setIsMobile(window.innerWidth < 768)
    }
    checkMobile()
    window.addEventListener("resize", checkMobile)
    return () => window.removeEventListener("resize", checkMobile)
  }, [])

  const insetMargin = isMobile ? 0 : (open ? DESKTOP_SIDEBAR_WIDTH : DESKTOP_SIDEBAR_COLLAPSED_WIDTH)
  
  return (
    <div
      ref={ref}
      className={cn(
        "flex flex-col min-h-screen transition-[margin-left] duration-300 ease-out",
        isMobile && "ml-0",
        className
      )}
      style={{
        marginLeft: insetMargin,
      }}
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
        "inline-flex items-center justify-center rounded p-2 text-black hover:bg-black/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black transition-colors duration-180",
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
      "flex h-9 w-full rounded border border-black/20 bg-white px-3 py-1 text-sm transition-all duration-180 file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black disabled:cursor-not-allowed disabled:opacity-50",
      className
    )}
    {...props}
  />
))
SidebarInput.displayName = "SidebarInput"

const SidebarRail = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("absolute right-0 top-0 h-full w-px bg-white/10", className)}
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
  DESKTOP_SIDEBAR_WIDTH,
  DESKTOP_SIDEBAR_COLLAPSED_WIDTH,
}

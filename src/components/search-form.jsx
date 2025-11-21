import { Search } from "lucide-react"
import { motion } from "framer-motion"
import { SidebarGroup, SidebarGroupContent, SidebarInput, useSidebar } from "./ui/sidebar"

export function SearchForm() {
  const { open, animate } = useSidebar()
  
  return (
    <motion.form 
      onSubmit={(e) => e.preventDefault()}
      animate={{
        opacity: animate ? (open ? 1 : 0) : 1,
        display: animate ? (open ? "block" : "none") : "block",
      }}
    >
      <SidebarGroup className="py-0">
        <SidebarGroupContent className="relative">
          <SidebarInput placeholder="Search..." className="pl-8" />
          <Search className="pointer-events-none absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 select-none opacity-50" />
        </SidebarGroupContent>
      </SidebarGroup>
    </motion.form>
  )
}


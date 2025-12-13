import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sidebar, 
  SidebarContent, 
  SidebarHeader, 
  SidebarMenu, 
  SidebarMenuItem, 
  SidebarMenuButton, 
  SidebarProvider,
  SidebarTrigger,
  SidebarInset
} from '@/components/ui/sidebar';
import { 
  LayoutDashboard, 
  BarChart3, 
  Users, 
  ShoppingCart, 
  Settings, 
  FileText, 
  HelpCircle, 
  Bell,
  Search,
  Plus,
  TrendingUp,
  Package,
  CreditCard,
  Shield,
  LogOut,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Input } from '@/components/ui/input';

const menuItems = [
  {
    title: 'Dashboard',
    icon: LayoutDashboard,
    id: 'dashboard',
    badge: null,
    submenu: []
  },
  {
    title: 'Analytics',
    icon: BarChart3,
    id: 'analytics',
    badge: 'New',
    submenu: [
      { title: 'Overview', id: 'analytics-overview' },
      { title: 'Reports', id: 'analytics-reports' },
      { title: 'Real-time', id: 'analytics-realtime' }
    ]
  },
  {
    title: 'Customers',
    icon: Users,
    id: 'customers',
    badge: null,
    submenu: [
      { title: 'All Customers', id: 'customers-all' },
      { title: 'Segments', id: 'customers-segments' },
      { title: 'Activity', id: 'customers-activity' }
    ]
  },
  {
    title: 'Products',
    icon: Package,
    id: 'products',
    badge: '12',
    submenu: [
      { title: 'Inventory', id: 'products-inventory' },
      { title: 'Categories', id: 'products-categories' },
      { title: 'Analytics', id: 'products-analytics' }
    ]
  },
  {
    title: 'Orders',
    icon: ShoppingCart,
    id: 'orders',
    badge: '5',
    submenu: [
      { title: 'All Orders', id: 'orders-all' },
      { title: 'Fulfillment', id: 'orders-fulfillment' },
      { title: 'Returns', id: 'orders-returns' }
    ]
  },
  {
    title: 'Billing',
    icon: CreditCard,
    id: 'billing',
    badge: null,
    submenu: [
      { title: 'Overview', id: 'billing-overview' },
      { title: 'Invoices', id: 'billing-invoices' },
      { title: 'Subscriptions', id: 'billing-subscriptions' }
    ]
  },
  {
    title: 'Security',
    icon: Shield,
    id: 'security',
    badge: null,
    submenu: []
  },
  {
    title: 'Settings',
    icon: Settings,
    id: 'settings',
    badge: null,
    submenu: [
      { title: 'General', id: 'settings-general' },
      { title: 'Team', id: 'settings-team' },
      { title: 'Integrations', id: 'settings-integrations' }
    ]
  }
];

export function DashboardSidebar({ activeItem, setActiveItem, expandedItems, setExpandedItems }) {
  const [searchQuery, setSearchQuery] = useState('');

  const toggleExpanded = (itemId) => {
    setExpandedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const filteredMenuItems = menuItems.filter(item =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.submenu.some(sub => sub.title.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <Sidebar>
      <SidebarHeader className="p-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-lg">Raptorflow</span>
        </div>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Search menu..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-gray-50 border-gray-200"
          />
        </div>
      </SidebarHeader>

      <SidebarContent className="px-3">
        <SidebarMenu>
          {filteredMenuItems.map((item) => (
            <SidebarMenuItem key={item.id}>
              <div>
                <SidebarMenuButton
                  isActive={activeItem === item.id}
                  onClick={() => {
                    setActiveItem(item.id);
                    if (item.submenu.length > 0) {
                      toggleExpanded(item.id);
                    }
                  }}
                  className="w-full justify-between group"
                >
                  <div className="flex items-center gap-3">
                    <item.icon className="w-4 h-4" />
                    <span className="font-medium">{item.title}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {item.badge && (
                      <Badge variant={item.badge === 'New' ? 'default' : 'secondary'} className="text-xs">
                        {item.badge}
                      </Badge>
                    )}
                    {item.submenu.length > 0 && (
                      expandedItems.includes(item.id) ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronRight className="w-4 h-4" />
                      )
                    )}
                  </div>
                </SidebarMenuButton>

                <AnimatePresence>
                  {item.submenu.length > 0 && expandedItems.includes(item.id) && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <div className="ml-8 mt-1 space-y-1">
                        {item.submenu.map((subItem) => (
                          <SidebarMenuButton
                            key={subItem.id}
                            isActive={activeItem === subItem.id}
                            onClick={() => setActiveItem(subItem.id)}
                            className="w-full justify-start text-sm text-gray-600 hover:text-gray-900"
                          >
                            {subItem.title}
                          </SidebarMenuButton>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>

        <div className="mt-auto p-3 border-t border-gray-200">
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton className="w-full justify-start text-gray-600 hover:text-gray-900">
                <HelpCircle className="w-4 h-4" />
                <span>Help & Support</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <SidebarMenuButton className="w-full justify-start text-red-600 hover:text-red-700">
                <LogOut className="w-4 h-4" />
                <span>Log out</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </div>
      </SidebarContent>

      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-3">
          <Avatar className="w-8 h-8">
            <AvatarImage src="/api/placeholder/32/32" alt="User" />
            <AvatarFallback>JD</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">John Doe</p>
            <p className="text-xs text-gray-500 truncate">john@example.com</p>
          </div>
          <div className="relative">
            <Bell className="w-4 h-4 text-gray-400" />
            <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </div>
        </div>
      </div>
    </Sidebar>
  );
}

export function DashboardLayout({ children, activeItem, setActiveItem, expandedItems, setExpandedItems }) {
  return (
    <SidebarProvider>
      <div className="flex h-screen bg-gray-50">
        <DashboardSidebar 
          activeItem={activeItem}
          setActiveItem={setActiveItem}
          expandedItems={expandedItems}
          setExpandedItems={setExpandedItems}
        />
        <SidebarInset className="flex-1 overflow-auto">
          <header className="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <SidebarTrigger />
                <div className="flex items-center gap-2">
                  <Plus className="w-5 h-5 text-indigo-600" />
                  <span className="font-medium">Quick Actions</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <Search className="w-5 h-5 text-gray-600" />
                </button>
                <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors relative">
                  <Bell className="w-5 h-5 text-gray-600" />
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>
              </div>
            </div>
          </header>
          <main className="p-6">
            {children}
          </main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}

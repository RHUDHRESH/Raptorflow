import React from 'react'
import { Outlet } from 'react-router-dom'
import { AppSidebar } from '../components/app-sidebar'
import { SidebarProvider, SidebarInset } from '../components/ui/sidebar'

const AppLayout = () => {
    return (
        <SidebarProvider>
            <div className="flex min-h-screen w-full">
                <AppSidebar />
                <SidebarInset className="flex-1">
                    <main className="flex-1 overflow-auto">
                        <Outlet />
                    </main>
                </SidebarInset>
            </div>
        </SidebarProvider>
    )
}

export default AppLayout

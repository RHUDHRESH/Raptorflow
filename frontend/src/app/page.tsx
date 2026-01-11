/**
 * Main Page Component
 * Root page that uses the main layout
 */
import MainLayout from "@/components/MainLayout"
import Dashboard from "@/components/Dashboard"

export default function HomePage() {
  return (
    <MainLayout>
      <Dashboard />
    </MainLayout>
  )
}

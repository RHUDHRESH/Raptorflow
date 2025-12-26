export default function SystemPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">System Status</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Backend Services</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">API Server</span>
                <span className="text-green-600">● Online</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Database</span>
                <span className="text-green-600">● Connected</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Radar Engine</span>
                <span className="text-green-600">● Active</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Performance</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Response Time</span>
                <span className="text-gray-800">120ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">CPU Usage</span>
                <span className="text-gray-800">45%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Memory</span>
                <span className="text-gray-800">2.1GB</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Recent Activity</h2>
            <div className="space-y-2">
              <div className="text-sm text-gray-600">
                Last scan: 2 hours ago
              </div>
              <div className="text-sm text-gray-600">
                Signals processed: 1,234
              </div>
              <div className="text-sm text-gray-600">
                Active users: 42
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

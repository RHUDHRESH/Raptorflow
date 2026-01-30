export default function SupportPage() {
  return (
    <div className="min-h-screen bg-gray-50 px-6 py-12">
      <div className="mx-auto max-w-3xl rounded-2xl bg-white p-8 shadow">
        <h1 className="text-3xl font-bold text-gray-900">Support</h1>
        <p className="mt-4 text-gray-600">
          Need help with Raptorflow? Our team is here to assist you.
        </p>
        <div className="mt-6 space-y-4 text-sm text-gray-600">
          <p>
            Email us at <span className="font-medium text-gray-800">support@raptorflow.ai</span>
            {' '}for account assistance or product questions.
          </p>
          <p>
            For urgent issues, include your workspace name and a short description of the
            problem so we can respond quickly.
          </p>
          <p>
            You can also browse our documentation for setup guides and best practices.
          </p>
        </div>
      </div>
    </div>
  );
}

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gray-50 px-6 py-12">
      <div className="mx-auto max-w-3xl rounded-2xl bg-white p-8 shadow">
        <h1 className="text-3xl font-bold text-gray-900">Terms of Service</h1>
        <p className="mt-4 text-gray-600">
          These terms govern your access to Raptorflow. Please review them carefully before
          using the platform.
        </p>
        <div className="mt-6 space-y-4 text-sm text-gray-600">
          <p>
            By using Raptorflow, you agree to comply with all applicable laws and to keep your
            account credentials secure.
          </p>
          <p>
            We may update these terms from time to time. Continued use of the service indicates
            acceptance of the updated terms.
          </p>
          <p>
            For questions about these terms, reach out to our support team at any time.
          </p>
        </div>
      </div>
    </div>
  );
}

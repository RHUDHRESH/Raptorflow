export default function GDPRPage() {
  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Privacy Policy
        </h1>

        <div className="prose max-w-none">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Data Collection
          </h2>
          <p className="text-gray-600 mb-6">
            We collect and process data in accordance with GDPR regulations to
            provide our competitive intelligence services.
          </p>

          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Your Rights
          </h2>
          <p className="text-gray-600 mb-6">
            You have the right to access, rectify, erase, or restrict processing
            of your personal data.
          </p>

          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Contact</h2>
          <p className="text-gray-600">
            For privacy inquiries, contact our data protection officer.
          </p>
        </div>
      </div>
    </div>
  );
}

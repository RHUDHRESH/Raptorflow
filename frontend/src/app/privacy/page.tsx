export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gray-50 px-6 py-12">
      <div className="mx-auto max-w-3xl rounded-2xl bg-white p-8 shadow">
        <h1 className="text-3xl font-bold text-gray-900">Privacy Policy</h1>
        <p className="mt-4 text-gray-600">
          Your privacy matters. This policy explains how Raptorflow collects, uses, and protects
          your information.
        </p>
        <div className="mt-6 space-y-4 text-sm text-gray-600">
          <p>
            We collect only the data necessary to provide and improve our services, and we never
            sell your personal information.
          </p>
          <p>
            You can request access to, correction of, or deletion of your data by contacting our
            support team.
          </p>
          <p>
            We use industry-standard safeguards to protect your data, including encryption and
            access controls.
          </p>
        </div>
      </div>
    </div>
  );
}

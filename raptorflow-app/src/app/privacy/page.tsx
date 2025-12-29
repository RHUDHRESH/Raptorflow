'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';

export default function PrivacyPage() {
  return (
    <MarketingLayout>
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-4xl px-6 lg:px-8">
          <div className="text-center mb-16">
            <h1 className="font-serif text-5xl lg:text-6xl font-medium text-gray-900 mb-6 leading-tight">
              Privacy Policy
            </h1>
            <p className="text-lg text-gray-600 leading-relaxed max-w-2xl mx-auto">
              Last updated: December 26, 2024
            </p>
          </div>

          <div className="prose prose-lg max-w-none space-y-8">
            <div className="text-gray-700 leading-relaxed space-y-6">
              <h2 className="font-serif text-2xl font-medium text-gray-900">
                Introduction
              </h2>
              <p>
                RaptorFlow ("we," "us," or "our") is committed to protecting
                your personal information and respecting your privacy. This
                Privacy Policy explains how we collect, use, store, and protect
                your personal data when you use our marketing platform and
                related services.
              </p>
              <p>
                This policy is written in compliance with the Digital Personal
                Data Protection Act, 2023 (DPDPA) of India and applies to all
                users within India and Indian residents using our services
                globally.
              </p>
            </div>

            <div className="text-gray-700 leading-relaxed space-y-6">
              <h2 className="font-serif text-2xl font-medium text-gray-900">
                Personal Data We Collect
              </h2>
              <p>We collect the following categories of personal data:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>
                  <strong>Account Information:</strong> Name, email address,
                  phone number, company details, and billing information.
                </li>
                <li>
                  <strong>Usage Data:</strong> How you interact with our
                  platform, features used, time spent, and navigation patterns.
                </li>
                <li>
                  <strong>Technical Data:</strong> IP address, device
                  information, browser type, operating system, and cookies.
                </li>
                <li>
                  <strong>Marketing Data:</strong> Campaign data, analytics,
                  performance metrics, and creative assets you create.
                </li>
              </ul>
            </div>

            <div className="text-gray-700 leading-relaxed space-y-6">
              <h2 className="font-serif text-2xl font-medium text-gray-900">
                How We Use Your Personal Data
              </h2>
              <p>We use your personal data for the following purposes:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>
                  To provide, maintain, and improve our marketing platform and
                  services.
                </li>
                <li>
                  To analyze usage patterns and improve our platform
                  functionality and user experience.
                </li>
                <li>
                  To send you important updates, security alerts, and customer
                  support communications.
                </li>
                <li>
                  To comply with applicable laws, regulations, and legal
                  processes.
                </li>
              </ul>
            </div>

            <div className="text-gray-700 leading-relaxed space-y-6">
              <h2 className="font-serif text-2xl font-medium text-gray-900">
                Your Rights Under DPDPA 2023
              </h2>
              <p>
                Under the Digital Personal Data Protection Act, 2023, you have
                the following rights:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>
                  <strong>Right to Access:</strong> You can request a copy of
                  the personal data we hold about you.
                </li>
                <li>
                  <strong>Right to Correction:</strong> You can request
                  correction of inaccurate or incomplete personal data.
                </li>
                <li>
                  <strong>Right to Erasure:</strong> You can request deletion of
                  your personal data in certain circumstances.
                </li>
                <li>
                  <strong>Right to Withdraw Consent:</strong> You can withdraw
                  your consent at any time, subject to legal and contractual
                  restrictions.
                </li>
              </ul>
            </div>

            <div className="text-gray-700 leading-relaxed space-y-6">
              <h2 className="font-serif text-2xl font-medium text-gray-900">
                Data Security
              </h2>
              <p>
                We implement appropriate technical and organizational security
                measures to protect your personal data against unauthorized
                access, alteration, disclosure, or destruction. These include
                encryption, secure servers, access controls, and regular
                security audits.
              </p>
              <p>
                However, no method of transmission over the internet or method
                of electronic storage is 100% secure. While we strive to use
                commercially acceptable means to protect your personal data, we
                cannot guarantee its absolute security.
              </p>
            </div>

            <div className="text-gray-700 leading-relaxed space-y-6">
              <h2 className="font-serif text-2xl font-medium text-gray-900">
                International Data Transfers
              </h2>
              <p>
                Your personal data may be transferred to and processed in
                countries other than India. We ensure adequate protection for
                your personal data in accordance with DPDPA 2023 requirements
                through appropriate safeguards including standard contractual
                clauses and compliance with applicable data protection laws.
              </p>
            </div>

            <div className="text-gray-700 leading-relaxed space-y-6">
              <h2 className="font-serif text-2xl font-medium text-gray-900">
                How to Exercise Your Rights
              </h2>
              <p>
                To exercise your rights under this Privacy Policy or if you have
                any questions about our data practices, please contact us:
              </p>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                <p className="text-gray-700 mb-2">
                  <strong>Email:</strong> privacy@raptorflow.com
                </p>
                <p className="text-gray-700 mb-2">
                  <strong>Response Time:</strong> We will respond to your
                  request within 30 days as required by DPDPA 2023.
                </p>
                <p className="text-gray-700">
                  <strong>Verification:</strong> We may need to verify your
                  identity before processing request to protect your personal
                  data.
                </p>
              </div>
            </div>

            <div className="text-gray-700 leading-relaxed space-y-6">
              <h2 className="font-serif text-2xl font-medium text-gray-900">
                Complaints to Data Protection Board of India
              </h2>
              <p>
                If you are not satisfied with our response to your privacy
                concerns, you have the right to file a complaint with the Data
                Protection Board of India. The Board is the national authority
                responsible for overseeing data protection compliance in India.
                You can contact them through their official website or by
                following the procedures outlined in the DPDPA 2023.
              </p>
            </div>

            <div className="text-gray-700 leading-relaxed space-y-6">
              <h2 className="font-serif text-2xl font-medium text-gray-900">
                Changes to This Privacy Policy
              </h2>
              <p>
                We may update this Privacy Policy from time to time to reflect
                changes in our practices, legal requirements, or business
                operations. We will notify you of any material changes by
                posting the updated policy on our website and updating the "Last
                updated" date at the top of this policy.
              </p>
            </div>

            <div className="text-gray-700 leading-relaxed space-y-6">
              <h2 className="font-serif text-2xl font-medium text-gray-900">
                Contact Information
              </h2>
              <div className="space-y-2">
                <p>
                  <strong>RaptorFlow</strong>
                  <br />
                  Email: privacy@raptorflow.com
                  <br />
                  Website: www.raptorflow.com
                </p>
                <p className="text-sm">
                  This Privacy Policy is effective as of December 26, 2024 and
                  complies with the Digital Personal Data Protection Act, 2023
                  (India).
                </p>
              </div>
            </div>
          </div>

          <div className="text-center mt-16">
            <Link
              href="/"
              className="inline-flex items-center justify-center rounded-lg bg-gray-900 px-6 py-3 text-white font-medium hover:bg-gray-800 transition-colors"
            >
              Back to Home
            </Link>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}

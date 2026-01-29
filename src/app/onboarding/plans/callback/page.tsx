"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/components/auth/AuthProvider";

export default function PaymentCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { checkPaymentStatus, refreshProfileStatus } = useAuth();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("Processing payment...");

  useEffect(() => {
    const processPaymentCallback = async () => {
      try {
        const merchantOrderId = searchParams.get("merchantOrderId");
        const transactionId = searchParams.get("transactionId");
        const paymentStatus = searchParams.get("status");

        if (!merchantOrderId) {
          setStatus("error");
          setMessage("Missing payment information");
          return;
        }

        console.log("🔐 [Payment Callback] Processing:", {
          merchantOrderId,
          transactionId,
          paymentStatus,
        });

        // Check payment status with backend
        const result = await checkPaymentStatus(merchantOrderId);

        if (result.success) {
          if (result.status === "completed") {
            setStatus("success");
            setMessage("Payment successful! Redirecting to onboarding...");

            // Refresh profile status to update subscription info
            await refreshProfileStatus();

            // Redirect to onboarding after a short delay
            setTimeout(() => {
              router.push("/onboarding/start");
            }, 2000);
          } else if (result.status === "failed") {
            setStatus("error");
            setMessage("Payment failed. Please try again.");
            setTimeout(() => {
              router.push("/onboarding/plans");
            }, 3000);
          } else {
            setStatus("loading");
            setMessage("Payment is processing. Please wait...");

            // Poll for status updates
            const pollInterval = setInterval(async () => {
              const pollResult = await checkPaymentStatus(merchantOrderId);
              if (pollResult.success && pollResult.status !== "pending") {
                clearInterval(pollInterval);
                if (pollResult.status === "completed") {
                  setStatus("success");
                  setMessage("Payment successful! Redirecting to onboarding...");
                  await refreshProfileStatus();
                  setTimeout(() => {
                    router.push("/onboarding/start");
                  }, 2000);
                } else {
                  setStatus("error");
                  setMessage("Payment failed. Please try again.");
                  setTimeout(() => {
                    router.push("/onboarding/plans");
                  }, 3000);
                }
              }
            }, 3000);

            // Clear polling after 5 minutes
            setTimeout(() => {
              clearInterval(pollInterval);
              if (status === "loading") {
                setStatus("error");
                setMessage("Payment verification timed out. Please contact support.");
                setTimeout(() => {
                  router.push("/onboarding/plans");
                }, 3000);
              }
            }, 300000);
          }
        } else {
          setStatus("error");
          setMessage(result.error || "Failed to verify payment status");
          setTimeout(() => {
            router.push("/onboarding/plans");
          }, 3000);
        }
      } catch (error) {
        console.error("🔐 [Payment Callback] Error:", error);
        setStatus("error");
        setMessage("An error occurred while processing your payment.");
        setTimeout(() => {
          router.push("/onboarding/plans");
        }, 3000);
      }
    };

    processPaymentCallback();
  }, [searchParams, checkPaymentStatus, refreshProfileStatus, router, status]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        <div className="mb-6">
          {status === "loading" && (
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          )}
          {status === "success" && (
            <div className="h-16 w-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
              <svg className="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          )}
          {status === "error" && (
            <div className="h-16 w-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
              <svg className="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          )}
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          {status === "loading" && "Processing Payment"}
          {status === "success" && "Payment Successful!"}
          {status === "error" && "Payment Error"}
        </h1>

        <p className="text-gray-600 mb-8">{message}</p>

        {status === "error" && (
          <button
            onClick={() => router.push("/onboarding/plans")}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Back to Plans
          </button>
        )}
      </div>
    </div>
  );
}

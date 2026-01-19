"use client";

import LoginForm from '@/components/auth/LoginForm';
import AuthLayout from '@/components/auth/AuthLayout';

export default function LoginPage() {
    return (
        <AuthLayout
            title={
                <>
                    Marketing. <br />
                    <span className="text-[var(--structure)] opacity-80">Finally under control.</span>
                </>
            }
            subtitle="Stop guessing. Start executing. The operating system for tracking, analyzing, and scaling your market presence with surgical precision."
        >
            <LoginForm />
        </AuthLayout>
    );
}

import Link from 'next/link'

export default function NotFound() {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-[#F3F4EE] text-[#2D3538] font-sans">
            <h2 className="text-3xl font-serif font-bold mb-4">Not Found</h2>
            <p className="mb-8 text-[#5B5F61]">Could not find requested resource</p>
            <Link href="/" className="px-6 py-3 bg-[#2D3538] text-white rounded hover:bg-[#1a1f21] transition-colors">
                Return Home
            </Link>
        </div>
    )
}

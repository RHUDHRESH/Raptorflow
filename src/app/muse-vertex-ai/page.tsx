import MuseChat from "@/components/muse/MuseChat";

export default function MusePage() {
    return (
        <div className="h-screen bg-gray-50">
            <div className="h-full max-w-4xl mx-auto p-4">
                <div className="h-full">
                    <MuseChat />
                </div>
            </div>
        </div>
    );
}

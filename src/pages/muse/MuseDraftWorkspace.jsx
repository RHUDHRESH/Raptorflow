import React from "react";
import { Link } from "react-router-dom";
import { MuseHeader } from "./components/MuseHeader";

export default function MuseDraftWorkspace() {
    return (
        <div className="min-h-screen bg-[#FAFAFA]">
            <MuseHeader title="Draft Workspace" />
            <div className="p-8 text-center">
                <h2 className="text-xl font-bold">Draft Workspace Placeholder</h2>
                <p className="mt-2 text-neutral-500">This screen will contain the Brief, Skeleton, Draft, and Variants tabs.</p>
                <Link to="/muse" className="mt-4 inline-block text-blue-500 underline">Back to Home</Link>
            </div>
        </div>
    );
}

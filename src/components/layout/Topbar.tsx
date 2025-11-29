import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useWorkspace } from '../../context/WorkspaceContext';
import { Sparkles, ChevronDown, LogOut, User, Building2 } from 'lucide-react';

/**
 * Topbar Component
 * 
 * Top navigation bar showing workspace info, user info, and account controls.
 */
export const Topbar: React.FC = () => {
    const { user, logout } = useAuth();
    const { currentWorkspace } = useWorkspace();
    const navigate = useNavigate();
    const [showUserMenu, setShowUserMenu] = useState(false);

    // Get user display name
    const userName = user?.user_metadata?.full_name || user?.email || 'Account';

    // Get user initials
    const getInitials = (name: string) => {
        const parts = name.split(' ');
        if (parts.length >= 2) {
            return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    };

    const handleLogout = async () => {
        await logout();
        navigate('/auth');
    };

    const handleWorkspaceClick = () => {
        navigate('/workspace');
    };

    return (
        <header className="h-16 bg-white border-b border-neutral-200 flex items-center justify-between px-6">
            {/* Left Side - App Logo & Workspace */}
            <div className="flex items-center gap-6">
                {/* App Logo */}
                <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-full bg-neutral-900 flex items-center justify-center">
                        <Sparkles className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-lg font-bold tracking-widest uppercase font-serif hidden sm:inline">
                        RaptorFlow
                    </span>
                </div>

                {/* Workspace Selector */}
                {currentWorkspace && (
                    <button
                        onClick={handleWorkspaceClick}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-neutral-100 transition-colors group"
                    >
                        <Building2 className="h-4 w-4 text-neutral-500 group-hover:text-neutral-900" />
                        <div className="text-left">
                            <div className="text-sm font-medium text-neutral-900">
                                {currentWorkspace.name}
                            </div>
                            {currentWorkspace.plan && (
                                <div className="text-xs text-neutral-500 capitalize">
                                    {currentWorkspace.plan} Plan
                                </div>
                            )}
                        </div>
                        <ChevronDown className="h-4 w-4 text-neutral-400" />
                    </button>
                )}
            </div>

            {/* Right Side - User Menu */}
            <div className="relative">
                <button
                    onClick={() => setShowUserMenu(!showUserMenu)}
                    className="flex items-center gap-3 hover:bg-neutral-100 rounded-lg px-3 py-2 transition-colors"
                >
                    {/* User Avatar */}
                    <div className="h-8 w-8 rounded-full bg-neutral-200 flex items-center justify-center text-sm font-semibold text-neutral-700">
                        {getInitials(userName)}
                    </div>

                    {/* User Name (hidden on mobile) */}
                    <span className="text-sm font-medium text-neutral-900 hidden sm:inline">
                        {userName}
                    </span>

                    <ChevronDown className="h-4 w-4 text-neutral-400" />
                </button>

                {/* Dropdown Menu */}
                {showUserMenu && (
                    <>
                        {/* Backdrop */}
                        <div
                            className="fixed inset-0 z-10"
                            onClick={() => setShowUserMenu(false)}
                        />

                        {/* Menu */}
                        <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-neutral-200 py-1 z-20">
                            {/* User Info */}
                            <div className="px-4 py-3 border-b border-neutral-100">
                                <div className="text-sm font-medium text-neutral-900">{userName}</div>
                                <div className="text-xs text-neutral-500">{user?.email}</div>
                            </div>

                            {/* Menu Items */}
                            <button
                                onClick={() => {
                                    setShowUserMenu(false);
                                    navigate('/settings');
                                }}
                                className="w-full flex items-center gap-3 px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-100 transition-colors"
                            >
                                <User className="h-4 w-4" />
                                <span>Account Settings</span>
                            </button>

                            <button
                                onClick={() => {
                                    setShowUserMenu(false);
                                    handleWorkspaceClick();
                                }}
                                className="w-full flex items-center gap-3 px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-100 transition-colors"
                            >
                                <Building2 className="h-4 w-4" />
                                <span>Switch Workspace</span>
                            </button>

                            <div className="border-t border-neutral-100 my-1" />

                            <button
                                onClick={() => {
                                    setShowUserMenu(false);
                                    handleLogout();
                                }}
                                className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                            >
                                <LogOut className="h-4 w-4" />
                                <span>Sign Out</span>
                            </button>
                        </div>
                    </>
                )}
            </div>
        </header>
    );
};

export default Topbar;

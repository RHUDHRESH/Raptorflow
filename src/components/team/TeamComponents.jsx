/**
 * Enhanced Team Components for Settings Page
 * Includes member management, invite flow, and role updates
 */

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Users,
    UserPlus,
    Mail,
    Clock,
    Shield,
    ShieldCheck,
    Eye,
    Edit3,
    Trash2,
    X,
    Check,
    Loader,
    AlertTriangle,
    Copy,
    ChevronDown,
    Crown
} from 'lucide-react'
import { teamAPI } from '../../lib/api'
import { useAuth } from '../../contexts/AuthContext'

const ROLES = [
    { id: 'admin', name: 'Admin', description: 'Full access, can manage team', icon: ShieldCheck },
    { id: 'editor', name: 'Editor', description: 'Can create and edit content', icon: Edit3 },
    { id: 'viewer', name: 'Viewer', description: 'View-only access', icon: Eye },
]

const ROLE_COLORS = {
    owner: 'bg-amber-100 text-amber-800',
    admin: 'bg-purple-100 text-purple-800',
    editor: 'bg-orange-100 text-orange-800',
    viewer: 'bg-gray-100 text-gray-600',
    billing: 'bg-emerald-100 text-emerald-800',
}

// Invite Member Modal
export const InviteMemberModal = ({ isOpen, onClose, onSuccess }) => {
    const [email, setEmail] = useState('')
    const [role, setRole] = useState('viewer')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [inviteLink, setInviteLink] = useState('')

    const handleInvite = async () => {
        if (!email || !email.includes('@')) {
            setError('Please enter a valid email address')
            return
        }

        setLoading(true)
        setError('')
        try {
            const result = await teamAPI.invite(email, role)
            setInviteLink(result.inviteLink)
            onSuccess?.()
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const copyInviteLink = () => {
        navigator.clipboard.writeText(inviteLink)
    }

    const handleClose = () => {
        setEmail('')
        setRole('viewer')
        setInviteLink('')
        setError('')
        onClose()
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-md bg-card border border-border rounded-2xl overflow-hidden"
            >
                <div className="p-6 border-b border-border">
                    <div className="flex items-center justify-between">
                        <h2 className="font-serif text-xl text-ink">Invite Team Member</h2>
                        <button onClick={handleClose} className="p-2 text-ink-400 hover:text-ink rounded-lg hover:bg-paper-200">
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                <div className="p-6">
                    {error && (
                        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700 text-sm">
                            <AlertTriangle className="w-4 h-4" />
                            {error}
                        </div>
                    )}

                    {inviteLink ? (
                        <div className="space-y-4">
                            <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-2">
                                <Check className="w-8 h-8 text-emerald-600" />
                            </div>
                            <h3 className="text-center text-lg font-medium text-ink">Invite Sent!</h3>
                            <p className="text-center text-body-sm text-ink-400">
                                We've sent an invitation to <strong>{email}</strong>
                            </p>
                            <div className="p-3 bg-paper-200 rounded-lg">
                                <p className="text-body-xs text-ink-400 mb-2">Or share this link:</p>
                                <div className="flex items-center gap-2">
                                    <input
                                        type="text"
                                        value={inviteLink}
                                        readOnly
                                        className="flex-1 px-3 py-2 bg-white border border-border rounded-lg text-body-xs text-ink truncate"
                                    />
                                    <button
                                        onClick={copyInviteLink}
                                        className="p-2 bg-primary text-white rounded-lg hover:opacity-95"
                                    >
                                        <Copy className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                            <button
                                onClick={handleClose}
                                className="w-full py-3 bg-primary text-white rounded-xl hover:opacity-95"
                            >
                                Done
                            </button>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-body-sm font-medium text-ink mb-2">Email Address</label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-ink-400" />
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="colleague@company.com"
                                        className="w-full pl-10 pr-4 py-3 bg-paper border border-border rounded-xl text-ink placeholder:text-ink-400 focus:outline-none focus:border-primary"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-body-sm font-medium text-ink mb-2">Role</label>
                                <div className="space-y-2">
                                    {ROLES.map(r => (
                                        <button
                                            key={r.id}
                                            onClick={() => setRole(r.id)}
                                            className={`w-full p-3 rounded-xl border text-left transition-all flex items-center gap-3 ${role === r.id
                                                    ? 'border-primary bg-signal-muted'
                                                    : 'border-border hover:border-ink-200'
                                                }`}
                                        >
                                            <r.icon className={`w-5 h-5 ${role === r.id ? 'text-primary' : 'text-ink-400'}`} />
                                            <div>
                                                <div className="text-body-sm font-medium text-ink">{r.name}</div>
                                                <div className="text-body-xs text-ink-400">{r.description}</div>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <button
                                onClick={handleInvite}
                                disabled={loading || !email}
                                className="w-full flex items-center justify-center gap-2 py-3 bg-primary text-white rounded-xl hover:opacity-95 disabled:opacity-50"
                            >
                                {loading ? (
                                    <Loader className="w-4 h-4 animate-spin" />
                                ) : (
                                    <>
                                        <UserPlus className="w-4 h-4" />
                                        Send Invite
                                    </>
                                )}
                            </button>
                        </div>
                    )}
                </div>
            </motion.div>
        </div>
    )
}

// Role Dropdown
const RoleDropdown = ({ currentRole, memberId, onUpdate, disabled }) => {
    const [isOpen, setIsOpen] = useState(false)
    const [loading, setLoading] = useState(false)

    const handleChange = async (newRole) => {
        if (newRole === currentRole) {
            setIsOpen(false)
            return
        }
        setLoading(true)
        try {
            await onUpdate(memberId, newRole)
        } finally {
            setLoading(false)
            setIsOpen(false)
        }
    }

    if (currentRole === 'owner' || disabled) {
        return (
            <span className={`px-2 py-1 text-xs rounded-full ${ROLE_COLORS[currentRole] || ROLE_COLORS.viewer}`}>
                {currentRole === 'owner' && <Crown className="inline w-3 h-3 mr-1" />}
                {currentRole.charAt(0).toUpperCase() + currentRole.slice(1)}
            </span>
        )
    }

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                disabled={loading}
                className={`flex items-center gap-1 px-2 py-1 text-xs rounded-full ${ROLE_COLORS[currentRole] || ROLE_COLORS.viewer}`}
            >
                {loading ? <Loader className="w-3 h-3 animate-spin" /> : currentRole}
                <ChevronDown className="w-3 h-3" />
            </button>
            {isOpen && (
                <>
                    <div className="fixed inset-0" onClick={() => setIsOpen(false)} />
                    <div className="absolute right-0 mt-1 w-32 bg-card border border-border rounded-lg shadow-lg z-10">
                        {ROLES.map(r => (
                            <button
                                key={r.id}
                                onClick={() => handleChange(r.id)}
                                className="w-full px-3 py-2 text-left text-sm hover:bg-paper-200 first:rounded-t-lg last:rounded-b-lg"
                            >
                                {r.name}
                            </button>
                        ))}
                    </div>
                </>
            )}
        </div>
    )
}

// Enhanced Team Tab
export const EnhancedTeamTab = () => {
    const { profile } = useAuth()
    const [members, setMembers] = useState([])
    const [invites, setInvites] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [showInviteModal, setShowInviteModal] = useState(false)

    useEffect(() => {
        loadTeamData()
    }, [])

    const loadTeamData = async () => {
        setLoading(true)
        setError('')
        try {
            const [membersRes, invitesRes] = await Promise.all([
                teamAPI.getMembers(),
                teamAPI.getInvites().catch(() => ({ invites: [] })) // Silently fail if no admin access
            ])
            setMembers(membersRes.members || [])
            setInvites(invitesRes.invites || [])
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleUpdateRole = async (memberId, newRole) => {
        try {
            await teamAPI.updateRole(memberId, newRole)
            await loadTeamData()
        } catch (err) {
            setError(err.message)
        }
    }

    const handleRemoveMember = async (memberId) => {
        if (!confirm('Are you sure you want to remove this team member?')) return
        try {
            await teamAPI.removeMember(memberId)
            await loadTeamData()
        } catch (err) {
            setError(err.message)
        }
    }

    const handleRevokeInvite = async (inviteId) => {
        try {
            await teamAPI.revokeInvite(inviteId)
            await loadTeamData()
        } catch (err) {
            setError(err.message)
        }
    }

    const currentUserRole = members.find(m => m.userId === profile?.id)?.role
    const canManage = currentUserRole === 'owner' || currentUserRole === 'admin'

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <Loader className="w-6 h-6 animate-spin text-primary" />
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="font-serif text-xl text-ink">Team</h2>
                    <p className="text-body-sm text-ink-400">Manage your team members and roles</p>
                </div>
                {canManage && (
                    <button
                        onClick={() => setShowInviteModal(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg text-sm hover:opacity-95"
                    >
                        <UserPlus className="w-4 h-4" />
                        Invite Member
                    </button>
                )}
            </div>

            {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-2 text-red-700 text-sm">
                    <AlertTriangle className="w-4 h-4" />
                    {error}
                </div>
            )}

            {/* Members list */}
            <div className="bg-card border border-border rounded-xl overflow-hidden">
                <div className="px-6 py-3 border-b border-border bg-paper-200">
                    <h3 className="text-body-sm font-medium text-ink">Members ({members.length})</h3>
                </div>
                <div className="divide-y divide-border">
                    {members.map(member => (
                        <div key={member.id} className="px-6 py-4 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-orange-400 flex items-center justify-center text-white font-medium">
                                    {member.name?.charAt(0)?.toUpperCase() || member.email?.charAt(0)?.toUpperCase() || '?'}
                                </div>
                                <div>
                                    <div className="text-body-sm font-medium text-ink">
                                        {member.name || 'Unknown'}
                                        {member.userId === profile?.id && <span className="text-ink-400 ml-1">(You)</span>}
                                    </div>
                                    <div className="text-body-xs text-ink-400">{member.email}</div>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <RoleDropdown
                                    currentRole={member.role}
                                    memberId={member.id}
                                    onUpdate={handleUpdateRole}
                                    disabled={!canManage || member.userId === profile?.id}
                                />
                                {canManage && member.role !== 'owner' && member.userId !== profile?.id && (
                                    <button
                                        onClick={() => handleRemoveMember(member.id)}
                                        className="p-2 text-ink-400 hover:text-red-600 hover:bg-red-50 rounded-lg"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Pending invites */}
            {canManage && invites.length > 0 && (
                <div className="bg-card border border-border rounded-xl overflow-hidden">
                    <div className="px-6 py-3 border-b border-border bg-paper-200">
                        <h3 className="text-body-sm font-medium text-ink flex items-center gap-2">
                            <Clock className="w-4 h-4 text-amber-500" />
                            Pending Invites ({invites.length})
                        </h3>
                    </div>
                    <div className="divide-y divide-border">
                        {invites.map(invite => (
                            <div key={invite.id} className="px-6 py-4 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-paper-300 flex items-center justify-center text-ink-400">
                                        <Mail className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <div className="text-body-sm font-medium text-ink">{invite.email}</div>
                                        <div className="text-body-xs text-ink-400">
                                            Invited as {invite.role} • Expires {new Date(invite.expires_at).toLocaleDateString()}
                                        </div>
                                    </div>
                                </div>
                                <button
                                    onClick={() => handleRevokeInvite(invite.id)}
                                    className="px-3 py-1 text-red-600 hover:bg-red-50 rounded-lg text-sm"
                                >
                                    Revoke
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Invite modal */}
            <AnimatePresence>
                {showInviteModal && (
                    <InviteMemberModal
                        isOpen={showInviteModal}
                        onClose={() => setShowInviteModal(false)}
                        onSuccess={loadTeamData}
                    />
                )}
            </AnimatePresence>
        </div>
    )
}

export default EnhancedTeamTab

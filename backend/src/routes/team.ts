/**
 * Team Management Routes
 * API endpoints for organization membership and invites
 */

import { Router, Request, Response } from 'express';
import crypto from 'crypto';
import { supabase, db } from '../lib/supabase';
import { env } from '../config/env';

const router = Router();

// Valid roles in the system
const VALID_ROLES = ['owner', 'admin', 'editor', 'viewer', 'billing'];

// Middleware to verify JWT token
const verifyToken = async (req: Request, res: Response, next: Function) => {
    const authHeader = req.headers.authorization;

    if (!authHeader?.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'Missing authorization' });
    }

    const token = authHeader.split(' ')[1];

    try {
        const { data: { user }, error } = await supabase.auth.getUser(token);

        if (error || !user) {
            return res.status(401).json({ error: 'Invalid token' });
        }

        (req as any).user = user;
        next();
    } catch (err) {
        return res.status(401).json({ error: 'Token verification failed' });
    }
};

// Helper to get user's organization and role
async function getUserOrgAndRole(userId: string): Promise<{
    orgId: string | null;
    role: string | null;
    error: any;
}> {
    // Get user's current org
    const { data: profile, error: profileError } = await supabase
        .from('profiles')
        .select('current_org_id')
        .eq('id', userId)
        .single();

    if (profileError || !profile?.current_org_id) {
        return { orgId: null, role: null, error: profileError || new Error('No organization') };
    }

    // Get user's role in org
    const { data: member, error: memberError } = await supabase
        .from('organization_members')
        .select('role')
        .eq('organization_id', profile.current_org_id)
        .eq('user_id', userId)
        .eq('is_active', true)
        .is('removed_at', null)
        .single();

    if (memberError) {
        return { orgId: profile.current_org_id, role: null, error: memberError };
    }

    return { orgId: profile.current_org_id, role: member?.role || null, error: null };
}

// Check if user can manage team (owner or admin)
function canManageTeam(role: string | null): boolean {
    return role === 'owner' || role === 'admin';
}

/**
 * GET /api/team/members
 * List all members of the current organization
 */
router.get('/members', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;
        const { orgId, error: orgError } = await getUserOrgAndRole(userId);

        if (orgError || !orgId) {
            return res.status(400).json({ error: 'No organization found' });
        }

        const { data: members, error } = await supabase
            .from('organization_members')
            .select(`
        id,
        role,
        is_active,
        joined_at,
        user:profiles!organization_members_user_id_fkey(
          id,
          email,
          full_name,
          avatar_url
        )
      `)
            .eq('organization_id', orgId)
            .eq('is_active', true)
            .is('removed_at', null)
            .order('joined_at', { ascending: true });

        if (error) {
            return res.status(500).json({ error: error.message });
        }

        // Format response
        const formattedMembers = (members || []).map((m: any) => ({
            id: m.id,
            userId: m.user?.id,
            email: m.user?.email,
            name: m.user?.full_name || m.user?.email?.split('@')[0] || 'Unknown',
            avatarUrl: m.user?.avatar_url,
            role: m.role,
            joinedAt: m.joined_at
        }));

        res.json({ members: formattedMembers });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

/**
 * POST /api/team/invite
 * Send an invite to join the organization
 */
router.post('/invite', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;
        const { email, role = 'viewer' } = req.body;

        if (!email) {
            return res.status(400).json({ error: 'Email is required' });
        }

        if (!VALID_ROLES.includes(role) || role === 'owner') {
            return res.status(400).json({ error: 'Invalid role. Cannot invite as owner.' });
        }

        const { orgId, role: userRole, error: orgError } = await getUserOrgAndRole(userId);

        if (orgError || !orgId) {
            return res.status(400).json({ error: 'No organization found' });
        }

        if (!canManageTeam(userRole)) {
            return res.status(403).json({ error: 'Only owners and admins can invite members' });
        }

        // Check if user is already a member
        const { data: existingMember } = await supabase
            .from('organization_members')
            .select('id')
            .eq('organization_id', orgId)
            .eq('user_id', (
                await supabase
                    .from('profiles')
                    .select('id')
                    .eq('email', email.toLowerCase())
                    .maybeSingle()
            ).data?.id || '')
            .maybeSingle();

        if (existingMember) {
            return res.status(400).json({ error: 'User is already a member of this organization' });
        }

        // Check for existing pending invite
        const { data: existingInvite } = await supabase
            .from('organization_invites')
            .select('id')
            .eq('organization_id', orgId)
            .eq('email', email.toLowerCase())
            .eq('status', 'pending')
            .maybeSingle();

        if (existingInvite) {
            return res.status(400).json({ error: 'An invite is already pending for this email' });
        }

        // Generate invite token
        const token = crypto.randomBytes(32).toString('hex');

        // Create invite
        const { data: invite, error: inviteError } = await supabase
            .from('organization_invites')
            .insert({
                organization_id: orgId,
                email: email.toLowerCase(),
                role,
                token,
                invited_by: userId,
                status: 'pending',
                expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 7 days
            })
            .select('id, token, expires_at')
            .single();

        if (inviteError) {
            return res.status(500).json({ error: inviteError.message });
        }

        // Build invite link
        const frontendUrl = env.FRONTEND_PUBLIC_URL || 'http://localhost:5173';
        const inviteLink = `${frontendUrl}/invite/${token}`;

        // TODO: Send invite email via Resend/SendGrid

        res.json({
            success: true,
            message: `Invite sent to ${email}`,
            inviteId: invite.id,
            inviteLink,
            expiresAt: invite.expires_at
        });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

/**
 * GET /api/team/invites
 * List pending invites for the organization
 */
router.get('/invites', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;
        const { orgId, role, error: orgError } = await getUserOrgAndRole(userId);

        if (orgError || !orgId) {
            return res.status(400).json({ error: 'No organization found' });
        }

        if (!canManageTeam(role)) {
            return res.status(403).json({ error: 'Only owners and admins can view invites' });
        }

        const { data: invites, error } = await supabase
            .from('organization_invites')
            .select(`
        id,
        email,
        role,
        status,
        expires_at,
        created_at,
        inviter:profiles!organization_invites_invited_by_fkey(full_name, email)
      `)
            .eq('organization_id', orgId)
            .eq('status', 'pending')
            .order('created_at', { ascending: false });

        if (error) {
            return res.status(500).json({ error: error.message });
        }

        res.json({ invites: invites || [] });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

/**
 * DELETE /api/team/invites/:id
 * Revoke a pending invite
 */
router.delete('/invites/:id', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;
        const { id } = req.params;

        const { orgId, role, error: orgError } = await getUserOrgAndRole(userId);

        if (orgError || !orgId) {
            return res.status(400).json({ error: 'No organization found' });
        }

        if (!canManageTeam(role)) {
            return res.status(403).json({ error: 'Only owners and admins can revoke invites' });
        }

        const { error } = await supabase
            .from('organization_invites')
            .update({ status: 'revoked' })
            .eq('id', id)
            .eq('organization_id', orgId)
            .eq('status', 'pending');

        if (error) {
            return res.status(500).json({ error: error.message });
        }

        res.json({ success: true, message: 'Invite revoked' });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

/**
 * POST /api/team/accept-invite
 * Accept an invite by token (called by invited user after they sign up/in)
 */
router.post('/accept-invite', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;
        const userEmail = (req as any).user.email;
        const { token } = req.body;

        if (!token) {
            return res.status(400).json({ error: 'Token is required' });
        }

        // Find the invite
        const { data: invite, error: inviteError } = await supabase
            .from('organization_invites')
            .select('*')
            .eq('token', token)
            .eq('status', 'pending')
            .single();

        if (inviteError || !invite) {
            return res.status(404).json({ error: 'Invalid or expired invite' });
        }

        // Check if invite is expired
        if (new Date(invite.expires_at) < new Date()) {
            await supabase
                .from('organization_invites')
                .update({ status: 'expired' })
                .eq('id', invite.id);
            return res.status(400).json({ error: 'Invite has expired' });
        }

        // Check email matches
        if (invite.email.toLowerCase() !== userEmail.toLowerCase()) {
            return res.status(403).json({ error: 'This invite is for a different email address' });
        }

        // Add user to organization
        const { error: memberError } = await supabase
            .from('organization_members')
            .insert({
                organization_id: invite.organization_id,
                user_id: userId,
                role: invite.role,
                is_active: true,
                invited_by: invite.invited_by
            });

        if (memberError) {
            // Check if already a member
            if (memberError.code === '23505') {
                return res.status(400).json({ error: 'You are already a member of this organization' });
            }
            return res.status(500).json({ error: memberError.message });
        }

        // Update invite status
        await supabase
            .from('organization_invites')
            .update({ status: 'accepted' })
            .eq('id', invite.id);

        // Update user's current org
        await supabase
            .from('profiles')
            .update({ current_org_id: invite.organization_id })
            .eq('id', userId);

        res.json({
            success: true,
            message: 'You have joined the organization',
            organizationId: invite.organization_id
        });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

/**
 * PATCH /api/team/members/:id
 * Update a member's role
 */
router.patch('/members/:id', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;
        const { id } = req.params;
        const { role } = req.body;

        if (!role || !VALID_ROLES.includes(role)) {
            return res.status(400).json({ error: 'Valid role is required' });
        }

        const { orgId, role: userRole, error: orgError } = await getUserOrgAndRole(userId);

        if (orgError || !orgId) {
            return res.status(400).json({ error: 'No organization found' });
        }

        if (!canManageTeam(userRole)) {
            return res.status(403).json({ error: 'Only owners and admins can change roles' });
        }

        // Cannot change owner role
        const { data: targetMember } = await supabase
            .from('organization_members')
            .select('role, user_id')
            .eq('id', id)
            .eq('organization_id', orgId)
            .single();

        if (!targetMember) {
            return res.status(404).json({ error: 'Member not found' });
        }

        if (targetMember.role === 'owner') {
            return res.status(403).json({ error: 'Cannot change owner role' });
        }

        // Cannot make someone else owner
        if (role === 'owner') {
            return res.status(403).json({ error: 'Cannot assign owner role' });
        }

        const { error } = await supabase
            .from('organization_members')
            .update({ role })
            .eq('id', id)
            .eq('organization_id', orgId);

        if (error) {
            return res.status(500).json({ error: error.message });
        }

        res.json({ success: true, message: 'Role updated' });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

/**
 * DELETE /api/team/members/:id
 * Remove a member from the organization
 */
router.delete('/members/:id', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;
        const { id } = req.params;

        const { orgId, role: userRole, error: orgError } = await getUserOrgAndRole(userId);

        if (orgError || !orgId) {
            return res.status(400).json({ error: 'No organization found' });
        }

        if (!canManageTeam(userRole)) {
            return res.status(403).json({ error: 'Only owners and admins can remove members' });
        }

        // Get target member
        const { data: targetMember } = await supabase
            .from('organization_members')
            .select('role, user_id')
            .eq('id', id)
            .eq('organization_id', orgId)
            .single();

        if (!targetMember) {
            return res.status(404).json({ error: 'Member not found' });
        }

        // Cannot remove owner
        if (targetMember.role === 'owner') {
            return res.status(403).json({ error: 'Cannot remove the owner' });
        }

        // Soft delete
        const { error } = await supabase
            .from('organization_members')
            .update({
                is_active: false,
                removed_at: new Date().toISOString()
            })
            .eq('id', id)
            .eq('organization_id', orgId);

        if (error) {
            return res.status(500).json({ error: error.message });
        }

        res.json({ success: true, message: 'Member removed' });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

export default router;

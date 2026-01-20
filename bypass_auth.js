const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, supabaseKey);

async function bypass() {
    const email = 'rhudhreshr@gmail.com';
    const name = 'RHUDHRESH';
    const googleId = '108900795003179679140';

    console.log(`🚀 Bypassing auth for ${email}...`);

    let userId;
    const { data: usersData, error: listError } = await supabase.auth.admin.listUsers();
    const existingUser = usersData?.users.find(u => u.email === email);

    if (existingUser) {
        console.log('User exists in auth. ID:', existingUser.id);
        userId = existingUser.id;
    } else {
        const { data: userData, error: createError } = await supabase.auth.admin.createUser({
            email: email,
            email_confirm: true,
            user_metadata: { full_name: name, google_id: googleId },
            password: 'temporary-password-123'
        });
        if (createError) {
            console.error('❌ Create error:', createError.message);
            return;
        }
        userId = userData.user.id;
    }

    // 2. Ensure user exists in public.users and public.profiles
    const { error: publicUserError } = await supabase.from('users').upsert({
        id: userId,
        auth_user_id: userId,
        email: email,
        full_name: name,
        onboarding_status: 'active',
        is_active: true
    });

    if (publicUserError) console.error('❌ Error in public.users:', publicUserError.message);

    const { error: profileError } = await supabase.from('profiles').upsert({
        id: userId,
        email: email,
        full_name: name,
        onboarding_status: 'active',
        is_active: true
    });

    if (profileError) console.error('❌ Error in public.profiles:', profileError.message);

    // 3. Create Session
    const { data: sessionData, error: signInError } = await supabase.auth.signInWithPassword({
        email: email,
        password: 'temporary-password-123'
    });

    if (signInError) {
        console.error('❌ Sign in error:', signInError.message);
        return;
    }

    const projectRef = supabaseUrl.split('//')[1].split('.')[0];
    const sessionStr = JSON.stringify(sessionData.session);
    const base64Session = Buffer.from(sessionStr).toString('base64');
    
    const cookieOptions = {
        path: "/",
        expires: Math.floor(Date.now() / 1000) + 3600,
        httpOnly: false,
        secure: false,
        sameSite: "Lax"
    };

    const playwrightState = {
        cookies: [
            { name: `sb-${projectRef}-auth-token`, value: sessionStr, domain: "localhost", ...cookieOptions },
            { name: `sb-${projectRef}-auth-token.0`, value: sessionData.session.access_token, domain: "localhost", ...cookieOptions },
            { name: `sb-${projectRef}-auth-token.1`, value: sessionData.session.refresh_token, domain: "localhost", ...cookieOptions },
            { name: "access_token", value: sessionData.session.access_token, domain: "localhost", ...cookieOptions },
            { name: "refresh_token", value: sessionData.session.refresh_token, domain: "localhost", ...cookieOptions }
        ],
        origins: [
            {
                origin: "http://localhost:3000",
                localStorage: [
                    { name: `sb-${projectRef}-auth-token`, value: sessionStr }
                ]
            }
        ]
    };

    fs.writeFileSync('playwright-auth.json', JSON.stringify(playwrightState, null, 2));
    console.log('✅ Auth bypass successful. storageState saved to playwright-auth.json');
}

bypass();
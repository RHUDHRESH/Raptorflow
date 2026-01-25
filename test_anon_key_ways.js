// Test anon key with different approaches
import { createServerClient } from '@supabase/ssr';
import dotenv from 'dotenv';

dotenv.config();

async function testAnonKeyDifferentWays() {
  console.log('Testing anon key with different approaches...');
  
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  
  console.log('URL:', url);
  console.log('Anon key:', anonKey?.substring(0, 20) + '...');
  
  // Test 1: Direct API call
  console.log('\n1. Testing direct API call...');
  try {
    const response = await fetch(`${url}/rest/v1/`, {
      headers: {
        'apikey': anonKey,
        'Authorization': `Bearer ${anonKey}`
      }
    });
    
    console.log('Direct API response status:', response.status);
    if (response.ok) {
      console.log('✅ Direct API call works');
    } else {
      const text = await response.text();
      console.log('❌ Direct API call failed:', text);
    }
  } catch (error) {
    console.log('❌ Direct API call error:', error.message);
  }
  
  // Test 2: Supabase client with simple query
  console.log('\n2. Testing Supabase client...');
  try {
    const supabase = createServerClient(url, anonKey, {
      cookies: {
        get() { return null; },
        set() {},
        remove() {}
      }
    });

    // Try a different query - maybe profiles doesn't exist or has RLS
    const { data, error } = await supabase.rpc('version', {});
    
    if (error) {
      console.log('❌ RPC version failed:', error.message);
      
      // Try to get auth settings instead
      const { data: authData, error: authError } = await supabase.auth.getSession();
      if (authError) {
        console.log('❌ Auth session failed:', authError.message);
      } else {
        console.log('✅ Auth session works (anon key is valid)');
      }
    } else {
      console.log('✅ RPC version works:', data);
    }
  } catch (error) {
    console.log('❌ Supabase client error:', error.message);
  }
  
  // Test 3: Check if the URL is correct
  console.log('\n3. Testing URL connectivity...');
  try {
    const response = await fetch(url);
    console.log('URL response status:', response.status);
    const text = await response.text();
    console.log('URL response preview:', text.substring(0, 200));
  } catch (error) {
    console.log('❌ URL connectivity error:', error.message);
  }
}

testAnonKeyDifferentWays();

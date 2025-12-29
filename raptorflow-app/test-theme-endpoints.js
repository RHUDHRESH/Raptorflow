// Test script for theme settings endpoints
// Run this with: node test-theme-endpoints.js

const testThemeEndpoints = async () => {
  const baseUrl = 'http://localhost:3000';
  const workspaceId = 'test-workspace-id';

  console.log('Testing Theme Settings Endpoints...\n');

  // Test GET endpoint
  console.log('1. Testing GET /api/settings/theme');
  try {
    const response = await fetch(`${baseUrl}/api/settings/theme?workspace_id=${workspaceId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    const data = await response.json();
    console.log('Response status:', response.status);
    console.log('Response data:', JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('GET error:', error.message);
  }

  console.log('\n2. Testing PUT /api/settings/theme');

  // Test PUT endpoint with valid data
  try {
    const putData = {
      theme_mode: 'dark',
      accent_color: '#ef4444',
      design_tokens: {
        borderRadius: {
          sm: '0.25rem',
          md: '0.5rem'
        }
      }
    };

    const response = await fetch(`${baseUrl}/api/settings/theme?workspace_id=${workspaceId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(putData)
    });

    const data = await response.json();
    console.log('Response status:', response.status);
    console.log('Response data:', JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('PUT error:', error.message);
  }

  console.log('\n3. Testing validation errors');

  // Test invalid theme_mode
  try {
    const invalidData = {
      theme_mode: 'invalid_mode',
      accent_color: '#3b82f6'
    };

    const response = await fetch(`${baseUrl}/api/settings/theme?workspace_id=${workspaceId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(invalidData)
    });

    const data = await response.json();
    console.log('Invalid theme_mode response:', response.status, data);
  } catch (error) {
    console.error('Validation test error:', error.message);
  }

  console.log('\nTest completed!');
};

// Export for use in other files or run directly
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { testThemeEndpoints };
} else {
  // Run if called directly
  testThemeEndpoints();
}

// Complete Authentication Test Runner
// Executes all tests from COMPLETE_AUTH_TEST_PLAN.md

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Test configuration
const TEST_CONFIG = {
  baseUrl: 'http://localhost:3000',
  email: 'rhudhreshr@gmail.com',
  testEmail: 'rhudhresh3697@gmail.com',
  fallbackEmail: 'rhudhreshr@gmail.com',
  timeout: 60000
};

// Test suite results
const testSuiteResults = {
  apiTests: { status: 'pending', results: null },
  browserTests: { status: 'pending', results: null },
  emailVerification: { status: 'pending', results: null },
  overall: { status: 'pending', summary: '' }
};

async function runCompleteTestSuite() {
  console.log('🧪 COMPLETE AUTHENTICATION TEST SUITE');
  console.log('📋 Based on COMPLETE_AUTH_TEST_PLAN.md');
  console.log('🎯 Testing all 6 steps + API endpoints');
  console.log('');

  try {
    // Step 1: Run API Tests
    await runAPITests();
    
    // Step 2: Run Browser Tests
    await runBrowserTests();
    
    // Step 3: Generate Final Report
    await generateFinalReport();
    
  } catch (error) {
    console.error('❌ Test suite failed:', error.message);
  }

  // Print final results
  printFinalResults();
}

async function runAPITests() {
  return new Promise((resolve, reject) => {
    console.log('🔌 Running API Tests...');
    
    testSuiteResults.apiTests.status = 'running';
    
    const apiTest = spawn('node', ['test-auth-api-endpoints.js'], {
      stdio: 'pipe',
      cwd: __dirname
    });
    
    let output = '';
    let errorOutput = '';
    
    apiTest.stdout.on('data', (data) => {
      output += data.toString();
      process.stdout.write(data);
    });
    
    apiTest.stderr.on('data', (data) => {
      errorOutput += data.toString();
      process.stderr.write(data);
    });
    
    apiTest.on('close', (code) => {
      if (code === 0) {
        testSuiteResults.apiTests.status = 'completed';
        testSuiteResults.apiTests.results = { output, errorOutput, exitCode: code };
        console.log('\n✅ API Tests Completed');
        resolve();
      } else {
        testSuiteResults.apiTests.status = 'failed';
        testSuiteResults.apiTests.results = { output, errorOutput, exitCode: code };
        console.log('\n❌ API Tests Failed');
        reject(new Error(`API tests failed with exit code ${code}`));
      }
    });
    
    apiTest.on('error', (error) => {
      testSuiteResults.apiTests.status = 'failed';
      testSuiteResults.apiTests.results = { output, errorOutput, error: error.message };
      console.log(`\n❌ API Tests Error: ${error.message}`);
      reject(error);
    });
  });
}

async function runBrowserTests() {
  return new Promise((resolve, reject) => {
    console.log('\n🌐 Running Browser Tests...');
    
    testSuiteResults.browserTests.status = 'running';
    
    const browserTest = spawn('node', ['test-complete-auth-flow-comprehensive.js'], {
      stdio: 'pipe',
      cwd: __dirname
    });
    
    let output = '';
    let errorOutput = '';
    
    browserTest.stdout.on('data', (data) => {
      output += data.toString();
      process.stdout.write(data);
    });
    
    browserTest.stderr.on('data', (data) => {
      errorOutput += data.toString();
      process.stderr.write(data);
    });
    
    browserTest.on('close', (code) => {
      if (code === 0) {
        testSuiteResults.browserTests.status = 'completed';
        testSuiteResults.browserTests.results = { output, errorOutput, exitCode: code };
        console.log('\n✅ Browser Tests Completed');
        resolve();
      } else {
        testSuiteResults.browserTests.status = 'failed';
        testSuiteResults.browserTests.results = { output, errorOutput, exitCode: code };
        console.log('\n❌ Browser Tests Failed');
        reject(new Error(`Browser tests failed with exit code ${code}`));
      }
    });
    
    browserTest.on('error', (error) => {
      testSuiteResults.browserTests.status = 'failed';
      testSuiteResults.browserTests.results = { output, errorOutput, error: error.message };
      console.log(`\n❌ Browser Tests Error: ${error.message}`);
      reject(error);
    });
  });
}

async function generateFinalReport() {
  console.log('\n📊 Generating Final Report...');
  
  try {
    // Read test results files
    let apiResults = {};
    let authResults = {};
    
    try {
      if (fs.existsSync('api-test-results.json')) {
        apiResults = JSON.parse(fs.readFileSync('api-test-results.json', 'utf8'));
      }
    } catch (error) {
      console.log('⚠️ Could not read API test results');
    }
    
    try {
      if (fs.existsSync('auth-test-results.json')) {
        authResults = JSON.parse(fs.readFileSync('auth-test-results.json', 'utf8'));
      }
    } catch (error) {
      console.log('⚠️ Could not read auth test results');
    }
    
    // Generate comprehensive report
    const report = {
      timestamp: new Date().toISOString(),
      testConfig: TEST_CONFIG,
      apiTests: {
        status: testSuiteResults.apiTests.status,
        results: apiResults,
        summary: summarizeAPITests(apiResults)
      },
      browserTests: {
        status: testSuiteResults.browserTests.status,
        results: authResults,
        summary: summarizeBrowserTests(authResults)
      },
      overall: generateOverallSummary(testSuiteResults),
      recommendations: generateRecommendations(testSuiteResults, apiResults, authResults)
    };
    
    // Save report
    const reportFile = 'complete-auth-test-report.json';
    fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
    
    // Generate markdown report
    const markdownReport = generateMarkdownReport(report);
    fs.writeFileSync('COMPLETE_AUTH_TEST_REPORT.md', markdownReport);
    
    console.log(`✅ Final Report Generated: ${reportFile}`);
    console.log(`✅ Markdown Report Generated: COMPLETE_AUTH_TEST_REPORT.md`);
    
  } catch (error) {
    console.error('❌ Report generation failed:', error.message);
  }
}

function summarizeAPITests(apiResults) {
  const summary = {
    totalTests: 0,
    completedTests: 0,
    failedTests: 0,
    successRate: 0,
    details: []
  };
  
  Object.entries(apiResults).forEach(([endpoint, result]) => {
    summary.totalTests++;
    summary.details.push({
      endpoint,
      status: result.status,
      responseCode: result.response?.status
    });
    
    if (result.status === 'completed') {
      summary.completedTests++;
    } else if (result.status === 'failed') {
      summary.failedTests++;
    }
  });
  
  summary.successRate = summary.totalTests > 0 ? (summary.completedTests / summary.totalTests * 100).toFixed(1) : 0;
  
  return summary;
}

function summarizeBrowserTests(authResults) {
  const summary = {
    totalTests: 0,
    completedTests: 0,
    failedTests: 0,
    successRate: 0,
    details: []
  };
  
  Object.entries(authResults).forEach(([step, result]) => {
    summary.totalTests++;
    summary.details.push({
      step: result.name,
      status: result.status
    });
    
    if (result.status === 'completed') {
      summary.completedTests++;
    } else if (result.status === 'failed') {
      summary.failedTests++;
    }
  });
  
  summary.successRate = summary.totalTests > 0 ? (summary.completedTests / summary.totalTests * 100).toFixed(1) : 0;
  
  return summary;
}

function generateOverallSummary(testSuiteResults) {
  const summary = {
    totalSuites: 2,
    completedSuites: 0,
    failedSuites: 0,
    overallStatus: 'pending',
    successRate: 0
  };
  
  if (testSuiteResults.apiTests.status === 'completed') {
    summary.completedSuites++;
  } else if (testSuiteResults.apiTests.status === 'failed') {
    summary.failedSuites++;
  }
  
  if (testSuiteResults.browserTests.status === 'completed') {
    summary.completedSuites++;
  } else if (testSuiteResults.browserTests.status === 'failed') {
    summary.failedSuites++;
  }
  
  summary.successRate = (summary.completedSuites / summary.totalSuites * 100).toFixed(1);
  
  if (summary.completedSuites === summary.totalSuites) {
    summary.overallStatus = 'completed';
  } else if (summary.failedSuites > 0) {
    summary.overallStatus = 'failed';
  } else {
    summary.overallStatus = 'running';
  }
  
  return summary;
}

function generateRecommendations(testSuiteResults, apiResults, authResults) {
  const recommendations = [];
  
  // API recommendations
  if (testSuiteResults.apiTests.status === 'failed') {
    recommendations.push('🔧 Fix API endpoint issues - check server logs and configuration');
  }
  
  // Browser test recommendations
  if (testSuiteResults.browserTests.status === 'failed') {
    recommendations.push('🌐 Fix browser test issues - check UI elements and selectors');
  }
  
  // Email verification recommendations
  recommendations.push('📧 Verify email delivery - check both rhudhresh3697@gmail.com and rhudhreshr@gmail.com');
  recommendations.push('📧 Check spam/promotions folders for reset emails');
  
  // Security recommendations
  recommendations.push('🔐 Ensure token expiration is working (1 hour)');
  recommendations.push('🔐 Verify input validation and error handling');
  
  // Performance recommendations
  recommendations.push('⚡ Check API response times');
  recommendations.push('⚡ Verify email sending performance');
  
  return recommendations;
}

function generateMarkdownReport(report) {
  return `# 🧪 Complete Authentication Test Report

## 📋 Test Overview
- **Timestamp**: ${report.timestamp}
- **Base URL**: ${report.testConfig.baseUrl}
- **Test Email**: ${report.testConfig.email}
- **Target Email**: ${report.testConfig.testEmail}

## 🔌 API Tests Results

### Status: ${report.apiTests.status.toUpperCase()}
- **Total Tests**: ${report.apiTests.summary.totalTests}
- **Completed**: ${report.apiTests.summary.completedTests}
- **Failed**: ${report.apiTests.summary.failedTests}
- **Success Rate**: ${report.apiTests.summary.successRate}%

### API Endpoints Tested:
${report.apiTests.summary.details.map(detail => 
  `- **${detail.endpoint}**: ${detail.status} (${detail.responseCode || 'N/A'})`
).join('\n')}

## 🌐 Browser Tests Results

### Status: ${report.browserTests.status.toUpperCase()}
- **Total Tests**: ${report.browserTests.summary.totalTests}
- **Completed**: ${report.browserTests.summary.completedTests}
- **Failed**: ${report.browserTests.summary.failedTests}
- **Success Rate**: ${report.browserTests.summary.successRate}%

### Test Steps:
${report.browserTests.summary.details.map(detail => 
  `- **${detail.step}**: ${detail.status}`
).join('\n')}

## 📊 Overall Summary

### Status: ${report.overall.overallStatus.toUpperCase()}
- **Total Test Suites**: ${report.overall.totalSuites}
- **Completed Suites**: ${report.overall.completedSuites}
- **Failed Suites**: ${report.overall.failedSuites}
- **Overall Success Rate**: ${report.overall.successRate}%

## 🎯 Recommendations

${report.recommendations.map(rec => `- ${rec}`).join('\n')}

## 📧 Email Verification Instructions

1. **Check Primary Email**: ${report.testConfig.testEmail}
2. **Check Fallback Email**: ${report.testConfig.fallbackEmail}
3. **Subject**: "Reset Your RaptorFlow Password"
4. **From**: onboarding@resend.dev
5. **Check Folders**: Inbox + Spam/Promotions

## 🔄 Next Steps

1. Review failed tests and fix issues
2. Verify email delivery manually
3. Run tests again after fixes
4. Update documentation with results

---

*Report generated on ${new Date().toLocaleString()}*
`;
}

function printFinalResults() {
  console.log('\n🎯 COMPLETE AUTHENTICATION TEST SUITE RESULTS');
  console.log('=' .repeat(60));
  
  console.log(`\n🔌 API Tests: ${testSuiteResults.apiTests.status.toUpperCase()}`);
  console.log(`🌐 Browser Tests: ${testSuiteResults.browserTests.status.toUpperCase()}`);
  
  const overallStatus = testSuiteResults.overall.status;
  const statusIcon = overallStatus === 'completed' ? '🎉' : 
                    overallStatus === 'failed' ? '❌' : 
                    overallStatus === 'running' ? '⏳' : '⏸️';
  
  console.log(`\n${statusIcon} Overall Status: ${overallStatus.toUpperCase()}`);
  
  if (overallStatus === 'completed') {
    console.log('\n🎉 ALL TESTS PASSED! Authentication system is ready for production!');
  } else if (overallStatus === 'failed') {
    console.log('\n⚠️  Some tests failed. Please review the detailed reports and fix issues.');
  } else {
    console.log('\n⏳ Tests are still running or incomplete.');
  }
  
  console.log('\n📄 Reports Generated:');
  console.log('   📊 complete-auth-test-report.json (JSON)');
  console.log('   📋 COMPLETE_AUTH_TEST_REPORT.md (Markdown)');
  
  console.log('\n📧 Next Steps:');
  console.log('   1. Check email for password reset link');
  console.log('   2. Complete manual verification steps');
  console.log('   3. Review test reports for any issues');
  console.log('   4. Fix any failed tests and re-run');
}

// Check if required files exist
function checkRequiredFiles() {
  const requiredFiles = [
    'test-auth-api-endpoints.js',
    'test-complete-auth-flow-comprehensive.js'
  ];
  
  const missingFiles = requiredFiles.filter(file => !fs.existsSync(file));
  
  if (missingFiles.length > 0) {
    console.log('❌ Missing required test files:');
    missingFiles.forEach(file => console.log(`   - ${file}`));
    console.log('\nPlease ensure all test files are present before running the test suite.');
    process.exit(1);
  }
}

// Run the complete test suite
async function main() {
  console.log('🚀 Starting Complete Authentication Test Suite');
  console.log('📋 Based on COMPLETE_AUTH_TEST_PLAN.md');
  console.log('');
  
  // Check required files
  checkRequiredFiles();
  
  // Run tests
  await runCompleteTestSuite();
}

// Handle process termination
process.on('SIGINT', () => {
  console.log('\n\n⏹️ Test suite interrupted by user');
  process.exit(1);
});

process.on('SIGTERM', () => {
  console.log('\n\n⏹️ Test suite terminated');
  process.exit(1);
});

// Run the test suite
main().catch(console.error);

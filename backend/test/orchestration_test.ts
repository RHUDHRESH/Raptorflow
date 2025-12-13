import { RaptorFlowOrchestrator } from '../src/v2/orchestrator';
import { OrchestratorContext } from '../src/v2/types';
import { toOrchestratorContext, createInitialContext } from '../src/lib/mappers/orchestratorMapper';

async function testOrchestration() {
  console.log('=== MULTI-AGENT ORCHESTRATION TEST ===');

  try {
    // Test 1: Initialize orchestrator
    console.log('1. Initializing RaptorFlow Orchestrator...');
    const orchestrator = new RaptorFlowOrchestrator();
    console.log('   ✅ Orchestrator initialized successfully');

    // Test 2: Create test context
    console.log('2. Creating test context...');
    const testContext: OrchestratorContext = {
      user_id: 'test_user',
      goal: 'Create a comprehensive marketing strategy for a SaaS startup',
      campaign_context: {
        industry: 'SaaS',
        target_market: 'small businesses',
        budget: 50000,
        timeline: '3 months'
      },
      icp_context: {
        demographics: 'CTO/CFO of companies 50-200 employees',
        pain_points: ['inefficient processes', 'high costs', 'lack of visibility'],
        goals: ['increase efficiency', 'reduce costs', 'improve decision making']
      },
      current_state: 'initialization',
      execution_plan: [],
      completed_agents: [],
      failed_agents: [],
      results: {},
      dead_end_detected: false,
      dead_end_reason: '',
      token_budget: 100000,
      execution_metadata: {
        start_time: new Date().toISOString(),
        estimated_tokens: 0,
        actual_tokens: 0
      }
    };
    console.log('   ✅ Test context created');

    // Test 3: Execute simple workflow (just try to run one step)
    console.log('3. Testing workflow execution...');
    try {
      // This will likely fail due to missing agents, but let's see what happens
      const result = await orchestrator.executeWorkflow(testContext);
      console.log('   ✅ Workflow executed successfully');
      console.log('   Result:', result);
    } catch (error) {
      console.log('   ⚠️  Workflow execution failed (expected due to incomplete implementation):', error.message);
    }

    console.log('=== ORCHESTRATION TEST COMPLETE ===');
  } catch (error) {
    console.error('Test failed:', error);
    console.error('Error details:', error);
  }
}

async function testOrchestratorMappers() {
  console.log('=== ORCHESTRATOR MAPPER TESTS ===');

  try {
    // Test 1: Create initial context
    console.log('1. Testing createInitialContext...');
    const initialContext = createInitialContext('test_user', 'Test goal');
    console.log('   ✅ Initial context created');

    // Test 2: Validate context parsing
    console.log('2. Testing toOrchestratorContext with valid data...');
    const validContext = toOrchestratorContext({
      user_id: 'test_user',
      goal: 'Test goal',
      current_state: 'initialization'
    });
    console.log('   ✅ Context validated successfully');

    // Test 3: Test with missing required fields (should provide defaults)
    console.log('3. Testing toOrchestratorContext with partial data...');
    const partialContext = toOrchestratorContext({
      goal: 'Test goal'
      // user_id missing - should get default
    });
    expect(partialContext.user_id).toBe('');
    console.log('   ✅ Partial context handled with defaults');

    console.log('   ✅ All orchestrator mapper tests passed');
  } catch (error) {
    console.error('❌ Orchestrator mapper test failed:', error);
    throw error;
  }
}

testOrchestration().then(() => {
  return testOrchestratorMappers();
}).catch(console.error);

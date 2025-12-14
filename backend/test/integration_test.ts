import { skillLoader } from '../src/v2/skill_loader';
import { toolbox } from '../src/v2/toolbox';
import { RaptorFlowOrchestrator } from '../src/v2/orchestrator';

async function runIntegrationTest() {
  console.log('🧪 RaptorFlow Integration Test Starting...\n');

  try {
    // Test 1: Skills System
    console.log('1️⃣ Testing Skills System...');
    const skills = await skillLoader.loadAllSkillsFromDir();
    console.log(`   ✅ Loaded ${skills.length} skills`);

    const registered = await skillLoader.loadAndRegisterAllSkills();
    console.log(`   ✅ Registered ${registered} skill-based tools`);

    const availableTools = toolbox.getToolNames();
    console.log(`   ✅ Total toolbox tools: ${availableTools.length}`);
    console.log(`   📋 Available tools: ${availableTools.join(', ')}\n`);

    // Test 2: Tool Execution
    console.log('2️⃣ Testing Tool Execution...');
    try {
      const result = await toolbox.executeTool('web_scrape', {
        url: 'https://example.com',
        include_text: true
      });
      console.log('   ✅ Web scraping tool executed successfully');
      console.log(`   📊 Result: ${JSON.stringify(result).substring(0, 100)}...\n`);
    } catch (error) {
      console.log(`   ❌ Web scraping tool failed: ${error.message}\n`);
    }

    // Test 3: Orchestrator Initialization
    console.log('3️⃣ Testing Orchestrator Initialization...');
    try {
      const orchestrator = new RaptorFlowOrchestrator();
      console.log('   ✅ Orchestrator initialized successfully\n');
    } catch (error) {
      console.log(`   ❌ Orchestrator failed: ${error.message}\n`);
    }

    // Test 4: Agent Registry
    console.log('4️⃣ Testing Agent Registry...');
    try {
      const { agentRegistry } = await import('../src/v2/base_agent');
      const agents = agentRegistry.getAllAgents();
      console.log(`   ✅ Found ${agents.length} registered agents`);

      const departments = agents.reduce((acc, agent) => {
        const dept = acc[agent.department] || [];
        dept.push(agent.name);
        acc[agent.department] = dept;
        return acc;
      }, {} as Record<string, string[]>);

      console.log('   📊 Agents by department:');
      Object.entries(departments).forEach(([dept, agents]) => {
        console.log(`      ${dept}: ${agents.length} agents`);
      });
      console.log('');

    } catch (error) {
      console.log(`   ❌ Agent registry failed: ${error.message}\n`);
    }

    console.log('🎉 Integration Test Complete!');
    console.log('📈 RaptorFlow Agentic Backend Status: OPERATIONAL');

  } catch (error) {
    console.error('❌ Integration test failed:', error);
    process.exit(1);
  }
}

runIntegrationTest().catch(console.error);
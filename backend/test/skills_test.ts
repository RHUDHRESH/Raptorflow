import { skillLoader } from '../src/v2/skill_loader';
import { toolbox } from '../src/v2/toolbox';

async function testSkills() {
  console.log('=== SKILLS SYSTEM TEST ===');

  try {
    // Test 1: Load skills from markdown files
    console.log('1. Loading skills from markdown...');
    const skills = await skillLoader.loadAllSkillsFromDir();
    console.log('   Loaded skills:', skills.map(s => s.skill_name));

    // Test 2: Register skills as tools
    console.log('2. Registering skills as tools...');
    const registered = await skillLoader.loadAndRegisterAllSkills();
    console.log('   Registered tools:', registered);

    // Test 3: Check toolbox contents
    console.log('3. Toolbox contents:');
    const toolNames = toolbox.getToolNames();
    console.log('   Available tools:', toolNames);

    // Test 4: Execute web scraping tool
    console.log('4. Testing web scraping tool...');
    try {
      const result = await toolbox.executeTool('web_scrape', {
        url: 'https://example.com',
        include_text: true
      });
      console.log('   Scraping result:', result);
    } catch (error) {
      console.log('   Scraping error:', error.message);
    }

    // Test 5: Execute company enrichment tool
    console.log('5. Testing company enrichment tool...');
    try {
      const result = await toolbox.executeTool('enrich_company', {
        domain: 'openai.com',
        include_tech_stack: true
      });
      console.log('   Enrichment result:', result);
    } catch (error) {
      console.log('   Enrichment error:', error.message);
    }

    console.log('=== SKILLS TEST COMPLETE ===');
  } catch (error) {
    console.error('Test failed:', error);
  }
}

testSkills().catch(console.error);



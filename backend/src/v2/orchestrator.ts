import { StateGraph, START, END } from "@langchain/langgraph";
import { RunnableLambda, RunnableSequence } from "@langchain/core/runnables";
import { AgentExecutor } from "langchain/agents";
import { createOpenAIFunctionsAgent, createReactAgent } from "langchain/agents";
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";
import {
  OrchestratorContext,
  OrchestratorState,
  Department,
  AGENT_ROSTER,
  AgentIO,
  BaseAgent
} from "./types";
import { budgetMiddleware, shouldContinueWorkflow, estimateTokensForTask } from "./budget_middleware";
import { toolbox } from "./toolbox";
import { modelRouter } from "./router";
import { toOrchestratorContext, updateExecutionProgress } from "../lib/mappers/orchestratorMapper";

// =====================================================
// LANGGRAPH ORCHESTRATOR - LANGCHAIN ADVANCED AGENTIC
// =====================================================

export class RaptorFlowOrchestrator {
  private graph: StateGraph<any>;
  private agentExecutors: Map<string, AgentExecutor> = new Map();
  private agentChains: Map<string, RunnableSequence> = new Map();

  constructor() {
    this.graph = new StateGraph<OrchestratorContext>({
      channels: {
        user_id: { value: (x, y) => y ?? x },
        goal: { value: (x, y) => y ?? x },
        campaign_context: { value: (x, y) => y ?? x },
        icp_context: { value: (x, y) => y ?? x },
        current_state: { value: (x, y) => y ?? x },
        execution_plan: { value: (x, y) => y ?? x },
        completed_agents: { value: (x, y) => y ?? x },
        failed_agents: { value: (x, y) => y ?? x },
        results: { value: (x, y) => y ?? x },
        dead_end_detected: { value: (x, y) => y ?? x },
        dead_end_reason: { value: (x, y) => y ?? x },
        token_budget: { value: (x, y) => y ?? x },
        execution_metadata: { value: (x, y) => y ?? x }
      }
    });

    this.buildAgentChains();
    this.buildGraph();
  }

  /**
   * Build LangChain agent chains for all roster agents
   */
  private buildAgentChains(): void {
    // Create agent executors for each agent in roster
    Object.values(Department).forEach(dept => {
      AGENT_ROSTER[dept].forEach(agentName => {
        try {
          this.createAgentExecutor(agentName, dept);
        } catch (error: any) {
          console.warn(`Failed to create agent executor for ${agentName}:`, error?.message || error);
          // Continue with other agents
        }
      });
    });
  }

  /**
   * Create LangChain AgentExecutor for an agent
   */
  private createAgentExecutor(agentName: string, department: Department): void {
    try {
      // Get appropriate model for agent
      const model = modelRouter.getModelForAgent(agentName);

      // Get tools for this agent
      const tools = this.getToolsForAgent(agentName, department);

      // Create agent prompt based on department and agent type
      const systemPrompt = this.getAgentSystemPrompt(agentName, department);
      const prompt = ChatPromptTemplate.fromMessages([
        ["system", `${systemPrompt}

You have access to the following tools: {tools}

Tool names: {tool_names}`],
        ["human", "{input}"],
        new MessagesPlaceholder("agent_scratchpad"),
      ]);

      // Create ReAct agent (highest level of agentic reasoning)
      const agent = createReactAgent({
        llm: model,
        tools,
        prompt,
      });

      // Create executor with memory and callbacks
      const executor = AgentExecutor.fromAgentAndTools({
        agent: agent as any,
        tools,
        memory: undefined, // Will be added per execution
        callbacks: [
          {
            handleAgentAction: (action) => {
              console.log(`🔧 Agent ${agentName} executing: ${action.tool}(${JSON.stringify(action.toolInput)})`);
            },
            handleAgentEnd: (result) => {
              console.log(`✅ Agent ${agentName} completed: ${result.returnValues?.output?.substring(0, 100)}...`);
            }
          }
        ],
        maxIterations: 5,
        maxExecutionTime: 30000, // 30 seconds
        earlyStoppingMethod: "generate",
        returnIntermediateSteps: true,
        handleParsingErrors: true,
      });

      // Create executable chain
      const chain = RunnableSequence.from([
        RunnableLambda.from((input: any) => ({
          ...input,
          agent_name: agentName,
          department,
          timestamp: new Date().toISOString()
        })),
        executor,
        RunnableLambda.from((output: any) => ({
          ...output,
          agent_name: agentName,
          department,
          execution_time: Date.now(),
          token_usage: this.estimateTokenUsage(output),
          success: !output.error
        }))
      ]);

      this.agentExecutors.set(agentName, executor);
      this.agentChains.set(agentName, chain);

      console.log(`🤖 Created LangChain agent executor: ${agentName}`);

    } catch (error) {
      console.error(`Failed to create agent executor for ${agentName}:`, error);
    }
  }

  /**
   * Get system prompt for agent
   */
  private getAgentSystemPrompt(agentName: string, department: Department): string {
    const prompts: Record<string, string> = {
      // Market Intelligence Department
      market_intel_agent: `You are a senior market intelligence analyst with 10+ years experience.
You have access to web scraping tools and search capabilities.
Your role is to provide comprehensive market analysis including size, growth, competitors, and trends.
Always cite sources and provide confidence levels for your analysis.
Be data-driven and specific in your recommendations.`,

      competitor_intelligence_agent: `You are a competitive intelligence specialist.
You excel at analyzing competitor positioning, strategies, and weaknesses.
Use web scraping and historical data analysis to build detailed competitor profiles.
Focus on actionable intelligence that can inform strategic decisions.
Be thorough but prioritize the most impactful insights.`,

      // Add prompts for all other agents...
      // This would be expanded for all 36 agents
    };

    return prompts[agentName] || `You are ${agentName}, an expert agent in the ${department} department.
Execute your specialized role with precision and provide actionable outputs.`;
  }

  /**
   * Get tools for specific agent
   */
  private getToolsForAgent(agentName: string, department: Department): any[] {
    const toolMappings: Record<string, string[]> = {
      market_intel_agent: ['web_scrape', 'enrich_company'],
      competitor_intelligence_agent: ['web_scrape', 'enrich_company'],
      keyword_topic_miner_agent: ['web_scrape'],
      trend_radar_agent: ['web_scrape'],
      audience_insight_agent: ['web_scrape'],
      objection_miner_agent: ['web_scrape'],
      emotional_angle_architect: ['web_scrape'],
      // Offer & Positioning agents
      positioning_architect_agent: ['web_scrape'],
      offer_architect_agent: ['web_scrape'],
      value_proposition_agent: ['web_scrape'],
      rtb_agent: ['web_scrape'],
      message_pillar_agent: ['web_scrape'],
      revenue_model_agent: ['web_scrape'],
      // Funnels, Moves, Campaigns agents
      move_designer_agent: ['web_scrape'],
      campaign_architect_agent: ['web_scrape'],
      funnel_engineer_agent: ['web_scrape'],
      channel_mix_strategist: ['web_scrape'],
      experiment_generator_agent: ['web_scrape'],
      budget_allocation_agent: ['web_scrape'],
      sequencing_agent: ['web_scrape'],
      // Creative & Muse agents
      creative_director_agent: ['web_scrape'],
      copywriter_agent: ['web_scrape'],
      visual_concept_agent: ['web_scrape'],
      social_content_agent: ['web_scrape'],
      ad_variants_agent: ['web_scrape'],
      longform_writer_agent: ['web_scrape'],
      asset_repurposing_agent: ['web_scrape'],
      // Media, Distribution & Automation agents
      distribution_strategist_agent: ['web_scrape'],
      posting_scheduler_agent: ['web_scrape'],
      email_automation_agent: ['web_scrape'],
      whatsapp_engagement_agent: ['web_scrape'],
      ads_targeting_agent: ['web_scrape'],
      retargeting_agent: ['web_scrape'],
      lead_nurture_agent: ['web_scrape'],
      // Analytics, Matrix & Optimization agents
      metrics_interpreter_agent: ['web_scrape'],
      attribution_lite_agent: ['web_scrape'],
      rag_status_agent: ['web_scrape'],
      forecasting_agent: ['web_scrape'],
      insight_engine_agent: ['web_scrape'],
      kill_scale_agent: ['web_scrape'],
      lessons_learned_agent: ['web_scrape'],
      // Memory, Personalization & Learning agents
      brand_memory_agent: ['web_scrape'],
      user_preference_agent: ['web_scrape'],
      template_weighting_agent: ['web_scrape'],
      behavior_tracking_agent: ['web_scrape'],
      knowledge_base_builder_agent: ['web_scrape'],
      periodic_internet_learner_agent: ['web_scrape'],
      persona_evolution_agent: ['web_scrape'],
      // Safety, Quality & Guardrails agents
      brand_safety_agent: ['web_scrape'],
      compliance_agent: ['web_scrape'],
      ethical_guardrail_agent: ['web_scrape'],
      quality_rater_agent: ['web_scrape'],
      rewrite_fixer_agent: ['web_scrape']
    };

    const toolNames = toolMappings[agentName] || ['web_scrape']; // Default to web_scrape if no mapping
    const tools = toolNames.map(name => toolbox.getLangChainTool(name)).filter(Boolean);

    if (tools.length === 0) {
      console.warn(`⚠️  No tools found for agent ${agentName}, using empty array`);
    }

    return tools;
  }

  /**
   * Estimate token usage from execution result
   */
  private estimateTokenUsage(result: any): number {
    // Estimate based on input/output length and intermediate steps
    const inputLength = JSON.stringify(result.input || {}).length;
    const outputLength = JSON.stringify(result.output || {}).length;
    const stepsCount = result.intermediateSteps?.length || 0;

    return Math.ceil((inputLength + outputLength) / 4) + (stepsCount * 100);
  }

  /**
   * Register an agent with the orchestrator (legacy)
   */
  registerAgent(agent: BaseAgent): void {
    // Legacy method for backward compatibility
    // Agents are now auto-created from roster
    console.log(`⚠️  Legacy agent registration: ${agent.name}`);
  }

  /**
   * Create a marketing plan for execution
   */
  async createPlan(userId: string, goal: string, context?: any): Promise<any> {
    const planId = `plan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Analyze goal and select appropriate agents
    const selectedAgents = await this.selectAgentsForGoal(goal, context);
    const estimatedTokens = estimateTokensForTask('general', goal.length);

    const plan = {
      id: planId,
      userId,
      goal,
      context,
      agents: selectedAgents,
      estimatedTokens,
      steps: [
        {
          phase: 'research',
          agents: selectedAgents.filter(a => a.includes('intel') || a.includes('research')),
          duration: '2-3 minutes'
        },
        {
          phase: 'strategy',
          agents: selectedAgents.filter(a => a.includes('architect') || a.includes('positioning')),
          duration: '3-4 minutes'
        },
        {
          phase: 'execution',
          agents: selectedAgents.filter(a => a.includes('move') || a.includes('campaign')),
          duration: '2-3 minutes'
        },
        {
          phase: 'optimization',
          agents: selectedAgents.filter(a => a.includes('analytics') || a.includes('forecasting')),
          duration: '1-2 minutes'
        }
      ],
      created_at: new Date().toISOString()
    };

    // Store plan (in production, would use database)
    this.activePlans.set(planId, plan);

    return plan;
  }

  /**
   * Execute a planned strategy
   */
  async executePlan(planId: string, userId: string, options?: any): Promise<any> {
    const plan = this.activePlans.get(planId);
    if (!plan || plan.userId !== userId) {
      throw new Error('Plan not found or access denied');
    }

    // Execute using LangGraph workflow
    const context: OrchestratorContext = {
      user_id: userId,
      goal: plan.goal,
      campaign_context: plan.context?.campaign || {},
      icp_context: plan.context?.icp || {},
      current_state: OrchestratorState.PLANNING,
      execution_plan: plan.steps,
      completed_agents: [],
      failed_agents: [],
      results: {},
      dead_end_detected: false,
      dead_end_reason: '',
      token_budget: { total: 50000, used: 0, remaining: 50000, last_checkpoint: 0 },
      execution_metadata: {
        start_time: new Date().toISOString(),
        progress_percentage: 0,
        estimated_completion: new Date(Date.now() + 10 * 60 * 1000).toISOString()
      }
    };

    try {
      const result = await this.executeWorkflow(plan.userId, plan.goal, context);
      return result;
    } catch (error) {
      console.error(`Plan execution failed for ${planId}:`, error);
      throw error;
    }
  }

  /**
   * Process user feedback for agent learning
   */
  async processFeedback(userId: string, executionId: string, feedback: any): Promise<any> {
    // Store feedback for learning (would integrate with learning system)
    console.log(`📚 Processing feedback for execution ${executionId}:`, feedback);

    // Update agent performance metrics
    // In production, this would update agent prompts, tool selection, etc.

    return {
      processed: true,
      feedback_type: feedback.type,
      learning_applied: true,
      agents_updated: feedback.agent_outputs?.length || 0
    };
  }

  /**
   * Get execution status
   */
  async getExecutionStatus(executionId: string, userId: string): Promise<any> {
    // Mock status - in production would check actual execution state
    const mockStatus = {
      state: 'processing',
      progress: 65,
      currentAgent: 'creative_director_agent',
      completedAgents: ['market_intel_agent', 'positioning_architect_agent'],
      estimatedCompletion: new Date(Date.now() + 5 * 60 * 1000).toISOString(),
      tokenUsage: { used: 12500, remaining: 37500, budget: 50000 }
    };

    return mockStatus;
  }

  /**
   * Select appropriate agents for a given goal
   */
  private async selectAgentsForGoal(goal: string, context?: any): Promise<string[]> {
    // Simple agent selection logic based on goal keywords
    const goalLower = goal.toLowerCase();
    const selectedAgents: string[] = [];

    // Always include core agents
    selectedAgents.push('market_intel_agent', 'positioning_architect_agent');

    // Add specialized agents based on goal
    if (goalLower.includes('campaign') || goalLower.includes('launch')) {
      selectedAgents.push('campaign_architect_agent', 'creative_director_agent');
    }

    if (goalLower.includes('content') || goalLower.includes('blog')) {
      selectedAgents.push('copywriter_agent', 'longform_writer_agent');
    }

    if (goalLower.includes('social') || goalLower.includes('instagram') || goalLower.includes('linkedin')) {
      selectedAgents.push('social_content_agent');
    }

    if (goalLower.includes('advertising') || goalLower.includes('ads')) {
      selectedAgents.push('ad_variants_agent', 'ads_targeting_agent');
    }

    if (goalLower.includes('email') || goalLower.includes('automation')) {
      selectedAgents.push('email_automation_agent', 'lead_nurture_agent');
    }

    // Limit to reasonable number
    return selectedAgents.slice(0, 6);
  }

  // Storage for active plans (in production, would use database)
  private activePlans = new Map<string, any>();

  /**
   * Build the execution graph
   */
  private buildGraph(): void {
    // Start node - Initialize workflow
    this.graph.addNode(START, this.initializeWorkflow.bind(this));

    // Department nodes
    Object.values(Department).forEach(dept => {
      this.graph.addNode(dept as any, this.executeDepartment.bind(this, dept));
    });

    // Control nodes
    this.graph.addNode("validate", this.validateProgress.bind(this));
    this.graph.addNode("dead_end_handler", this.handleDeadEnd.bind(this));
    this.graph.addNode(END, this.finalizeWorkflow.bind(this));

    // Conditional edges - START routes to first department or dead_end
    this.graph.addConditionalEdges(
      START,
      this.routeAfterInitialize.bind(this)
    );

    // Remove conditional edge from non-existent "initialize" node

    // Department flow
    const departments = Object.values(Department);
    departments.forEach((dept, index) => {
      if (index < departments.length - 1) {
        this.graph.addConditionalEdges(
          dept as any,
          this.routeDepartmentComplete.bind(this, dept)
        );
      } else {
        this.graph.addEdge(dept as any, END);
      }
    });

    // Connect validate to finalize for now
    this.graph.addEdge("validate", END);

    this.graph.addEdge("dead_end_handler", END);
  }

  /**
   * Initialize workflow state
   */
  private async initializeWorkflow(state: OrchestratorContext): Promise<Partial<OrchestratorContext>> {
    console.log("🚀 Initializing RaptorFlow workflow");

    // Initialize budget
    const budget = await budgetMiddleware.initializeBudget(state.user_id, 50000);

    // Create execution plan based on goal
    const executionPlan = this.createExecutionPlan(state.goal);

    return {
      current_state: OrchestratorState.PLANNING,
      execution_plan: executionPlan,
      token_budget: {
        total: budget.total,
        used: budget.used,
        remaining: budget.remaining,
        last_checkpoint: budget.used
      },
      execution_metadata: {
        start_time: new Date().toISOString(),
        estimated_completion: this.estimateCompletionTime(executionPlan),
        current_step: "Planning execution",
        progress_percentage: 5
      },
      dead_end_detected: false
    };
  }

  /**
   * Create execution plan based on user goal
   */
  private createExecutionPlan(goal: string): OrchestratorContext['execution_plan'] {
    // Simple goal-based routing - could be enhanced with LLM analysis
    const goalLower = goal.toLowerCase();

    let departments: Department[] = [];
    let priority = 'medium';

    if (goalLower.includes('campaign') || goalLower.includes('launch')) {
      departments = [
        Department.MARKET_INTELLIGENCE,
        Department.OFFER_POSITIONING,
        Department.MOVES_CAMPAIGNS,
        Department.CREATIVE,
        Department.DISTRIBUTION,
        Department.ANALYTICS
      ];
      priority = 'high';
    } else if (goalLower.includes('icp') || goalLower.includes('audience')) {
      departments = [
        Department.MARKET_INTELLIGENCE,
        Department.MEMORY_LEARNING
      ];
    } else if (goalLower.includes('creative') || goalLower.includes('content')) {
      departments = [
        Department.CREATIVE,
        Department.SAFETY_QUALITY
      ];
    } else if (goalLower.includes('optimize') || goalLower.includes('analyze')) {
      departments = [
        Department.ANALYTICS,
        Department.MEMORY_LEARNING
      ];
    } else {
      // Default comprehensive workflow
      departments = [
        Department.MARKET_INTELLIGENCE,
        Department.OFFER_POSITIONING,
        Department.MOVES_CAMPAIGNS,
        Department.CREATIVE,
        Department.DISTRIBUTION,
        Department.SAFETY_QUALITY
      ];
    }

    return departments.map(dept => ({
      department: dept,
      agents: [...AGENT_ROSTER[dept]],
      dependencies: [],
      priority: priority as 'high' | 'medium' | 'low'
    }));
  }

  /**
   * Execute a department's agents using LangChain AgentExecutors
   */
  private async executeDepartment(
    department: Department,
    state: OrchestratorContext
  ): Promise<Partial<OrchestratorContext>> {
    console.log(`🏢 Executing department: ${department} (LangChain Agentic)`);

    const deptPlan = state.execution_plan.find(p => p.department === department);
    if (!deptPlan) {
      console.warn(`No plan found for department ${department}`);
      return {};
    }

    const results: Record<string, any> = { ...state.results };
    const completedAgents = [...state.completed_agents];
    const failedAgents = [...state.failed_agents];

    // Execute agents in department with SOTA parallel processing
    const agentExecutionResults = await this.executeAgentsInParallel(
      deptPlan.agents,
      department,
      state
    );

    // Process parallel execution results
    for (const result of agentExecutionResults) {
      if (result.status === 'fulfilled') {
        const { agentName, output } = result.value;

        // Record usage
        budgetMiddleware.recordUsage(
          state.user_id,
          agentName,
          output.token_usage || estimateTokensForTask('general', JSON.stringify(state).length),
          this.estimateCost(agentName, output.token_usage || estimateTokensForTask('general', JSON.stringify(state).length))
        );

        // Store results
        results[agentName] = {
          output: output.output || output.returnValues?.output,
          intermediate_steps: output.intermediateSteps,
          execution_time: output.execution_time,
          success: output.success
        };
        completedAgents.push(agentName);

        console.log(`✅ LangChain agent ${agentName} completed (parallel)`);

      } else {
        const { agentName, error } = result.reason;
        console.error(`❌ LangChain agent ${agentName} failed:`, error);
        failedAgents.push(agentName);

        // Check if we should continue or dead-end for critical agents
        if (this.isCriticalAgent(agentName)) {
          return {
            current_state: OrchestratorState.ERROR,
            failed_agents: failedAgents,
            dead_end_detected: true,
            dead_end_reason: `Critical agent ${agentName} failed: ${error}`
          };
        }
      }
    }

    return {
      results,
      completed_agents: completedAgents,
      failed_agents: failedAgents,
      execution_metadata: {
        ...state.execution_metadata,
        current_step: `Completed ${department}`,
        progress_percentage: this.calculateProgress(state.execution_plan, completedAgents, failedAgents)
      }
    };
  }

  /**
   * Validate workflow progress and decide next steps
   */
  private async validateProgress(state: OrchestratorContext): Promise<Partial<OrchestratorContext>> {
    console.log("🔍 Validating workflow progress");

    const totalAgents = state.execution_plan.reduce((sum, dept) => sum + dept.agents.length, 0);
    const completedCount = state.completed_agents.length;
    const failedCount = state.failed_agents.length;

    const successRate = completedCount / totalAgents;

    if (successRate >= 0.8) { // 80% success threshold
      console.log("✅ Workflow validation passed, finalizing...");
      return {
        current_state: OrchestratorState.COMPLETING
      };
    } else if (failedCount > completedCount) {
      console.log("❌ Too many failures, triggering dead end handling");
      return {
        current_state: OrchestratorState.ERROR,
        dead_end_detected: true,
        dead_end_reason: `Low success rate: ${successRate.toFixed(2)}`
      };
    } else {
      console.log("⚠️ Acceptable failure rate, attempting recovery...");
      // Could implement recovery logic here
      return {
        current_state: OrchestratorState.COMPLETING
      };
    }
  }

  /**
   * Execute multiple agents in parallel with intelligent batching
   */
  private async executeAgentsInParallel(
    agentNames: string[],
    department: Department,
    state: OrchestratorContext
  ): Promise<Array<PromiseSettledResult<{ agentName: string; output: any }>>> {
    console.log(`🚀 Executing ${agentNames.length} agents in parallel for ${department}`);

    // Analyze agent dependencies to determine execution order
    const { independent, dependent } = this.analyzeAgentDependencies(agentNames, department);

    // Execute independent agents in parallel first
    const independentPromises = independent.map(agentName =>
      this.executeSingleAgent(agentName, department, state)
    );

    // Wait for independent agents to complete
    const independentResults = await Promise.allSettled(independentPromises);

    // Execute dependent agents sequentially (they may need results from independent agents)
    const dependentResults: Array<PromiseSettledResult<{ agentName: string; output: any }>> = [];
    for (const agentName of dependent) {
      try {
        const result = await this.executeSingleAgent(agentName, department, {
          ...state,
          // Include results from completed independent agents
          results: {
            ...state.results,
            ...this.extractCompletedResults(independentResults)
          }
        });
        dependentResults.push({
          status: 'fulfilled',
          value: { agentName, output: result }
        });
      } catch (error) {
        dependentResults.push({
          status: 'rejected',
          reason: error
        });
      }
    }

    return [...independentResults, ...dependentResults];
  }

  /**
   * Execute a single agent with error handling
   */
  private async executeSingleAgent(
    agentName: string,
    department: Department,
    state: OrchestratorContext
  ): Promise<any> {
    const agentChain = this.agentChains.get(agentName);

    if (!agentChain) {
      throw { agentName, error: `Agent chain ${agentName} not found` };
    }

    // Check budget before execution
    const estimatedTokens = estimateTokensForTask('general', JSON.stringify(state).length);
    const budgetCheck = shouldContinueWorkflow(state, estimatedTokens);

    if (!budgetCheck.should_continue) {
      throw {
        agentName,
        error: `Budget exhausted before executing ${agentName}: ${budgetCheck.reason}`
      };
    }

    console.log(`🤖 Executing LangChain agent: ${agentName} (parallel)`);

    // Prepare input for agent chain
    const input = this.prepareAgentInputForChain(agentName, department, state);

    // Execute agent using LangChain chain (highest level agentic execution)
    const output = await agentChain.invoke(input);

    return output;
  }

  /**
   * Analyze agent dependencies to determine parallel execution strategy
   */
  private analyzeAgentDependencies(
    agentNames: string[],
    department: Department
  ): { independent: string[]; dependent: string[] } {
    // Define dependency rules based on agent types and department
    const dependencyMap: Record<string, string[]> = {
      // Market intelligence agents can run in parallel
      [Department.MARKET_INTELLIGENCE]: [],

      // Creative agents have some dependencies
      [Department.CREATIVE]: [
        'asset_repurposing_agent' // depends on: copywriter_agent, visual_concept_agent
      ],

      // Distribution agents can mostly run in parallel
      [Department.DISTRIBUTION]: [],

      // Campaign agents have sequential dependencies
      [Department.MOVES_CAMPAIGNS]: [
        'move_designer_agent', // depends on: campaign_architect_agent
        'channel_mix_strategist_agent', // depends on: move_designer_agent
        'budget_allocation_agent' // depends on: channel_mix_strategist_agent
      ],

      // Analytics agents can run in parallel
      [Department.ANALYTICS]: [],

      // Safety agents can run in parallel
      [Department.SAFETY_QUALITY]: []
    };

    const dependentAgents = dependencyMap[department] || [];
    const independent = agentNames.filter(name => !dependentAgents.includes(name));
    const dependent = agentNames.filter(name => dependentAgents.includes(name));

    console.log(`📊 ${department}: ${independent.length} independent, ${dependent.length} dependent agents`);

    return { independent, dependent };
  }

  /**
   * Extract successful results from parallel execution
   */
  private extractCompletedResults(
    results: Array<PromiseSettledResult<{ agentName: string; output: any }>>
  ): Record<string, any> {
    const completed: Record<string, any> = {};

    for (const result of results) {
      if (result.status === 'fulfilled') {
        const { agentName, output } = result.value;
        completed[agentName] = {
          output: output.output || output.returnValues?.output,
          intermediate_steps: output.intermediateSteps,
          execution_time: output.execution_time,
          success: output.success
        };
      }
    }

    return completed;
  }

  /**
   * Handle dead-end scenarios
   */
  private async handleDeadEnd(state: OrchestratorContext): Promise<Partial<OrchestratorContext>> {
    console.log("💀 Handling dead end scenario");

    // Log dead end for analysis
    console.error(`Dead end detected: ${state.dead_end_reason}`);

    // Could implement fallback strategies, partial results, etc.

    return {
      current_state: OrchestratorState.ERROR,
      execution_metadata: {
        ...state.execution_metadata,
        current_step: "Dead end reached",
        progress_percentage: 100
      }
    };
  }

  /**
   * Finalize successful workflow
   */
  private async finalizeWorkflow(state: OrchestratorContext): Promise<Partial<OrchestratorContext>> {
    console.log("🎉 Finalizing workflow");

    // Compile final results
    const finalPackage = this.compileFinalPackage(state);

    return {
      current_state: OrchestratorState.COMPLETING,
      execution_metadata: {
        ...state.execution_metadata,
        current_step: "Workflow completed",
        progress_percentage: 100
      },
      results: {
        ...state.results,
        final_package: finalPackage
      }
    };
  }

  // =====================================================
  // ROUTING LOGIC
  // =====================================================

  private routeInitialState(state: OrchestratorContext): string {
    return "initialize";
  }

  private routeAfterInitialize(state: OrchestratorContext): string {
    if (state.execution_plan.length > 0) {
      return state.execution_plan[0].department;
    }
    return "dead_end_handler";
  }

  private routeDepartmentComplete(department: Department, state: OrchestratorContext): string {
    const deptIndex = state.execution_plan.findIndex(p => p.department === department);
    if (deptIndex < state.execution_plan.length - 1) {
      return state.execution_plan[deptIndex + 1].department;
    }
    return "validate";
  }

  private routeAfterValidation(state: OrchestratorContext): string {
    if (state.dead_end_detected) {
      return "dead_end_handler";
    }
    return "finalize";
  }

  // =====================================================
  // HELPER METHODS
  // =====================================================

  private prepareAgentInput(agent: BaseAgent, state: OrchestratorContext): any {
    // Base context available to all agents
    const baseInput = {
      user_id: state.user_id,
      goal: state.goal,
      campaign_context: state.campaign_context,
      icp_context: state.icp_context,
      workflow_state: state.current_state
    };

    // Add department-specific context
    switch (agent.department) {
      case Department.MARKET_INTELLIGENCE:
        return {
          ...baseInput,
          research_query: this.extractResearchQuery(state),
          existing_intelligence: state.results.market_intel_agent || {}
        };

      case Department.OFFER_POSITIONING:
        return {
          ...baseInput,
          market_data: state.results.market_intel_agent,
          positioning_goal: this.extractPositioningGoal(state)
        };

      // Add other departments...
      default:
        return baseInput;
    }
  }

  private extractResearchQuery(state: OrchestratorContext): string {
    // Extract research needs from goal and context
    return `${state.goal} - ${JSON.stringify(state.icp_context || {})}`;
  }

  private extractPositioningGoal(state: OrchestratorContext): string {
    // Extract positioning requirements
    return state.goal;
  }

  private isCriticalAgent(agentName: string): boolean {
    // Define which agents are critical for workflow success
    const criticalAgents = [
      'orchestrator',
      'market_intel_agent',
      'positioning_architect_agent',
      'move_designer_agent'
    ];
    return criticalAgents.includes(agentName);
  }

  /**
   * Prepare agent input for LangChain chain execution
   */
  private prepareAgentInputForChain(agentName: string, department: Department, state: OrchestratorContext): any {
    // Base context available to all agents
    const baseInput = {
      user_id: state.user_id,
      goal: state.goal,
      campaign_context: state.campaign_context,
      icp_context: state.icp_context,
      workflow_state: state.current_state,
      input: this.buildAgentSpecificPrompt(agentName, department, state)
    };

    return baseInput;
  }

  /**
   * Build agent-specific prompt for LangChain execution
   */
  private buildAgentSpecificPrompt(agentName: string, department: Department, state: OrchestratorContext): string {
    const baseContext = `User Goal: ${state.goal}
Campaign Context: ${JSON.stringify(state.campaign_context || {})}
ICP Context: ${JSON.stringify(state.icp_context || {})}
Workflow Progress: ${state.execution_metadata?.progress_percentage || 0}% complete

Available Results from Previous Agents:
${Object.entries(state.results).map(([agent, result]) =>
  `${agent}: ${JSON.stringify(result).substring(0, 200)}...`
).join('\n')}

`;

    switch (agentName) {
      case 'market_intel_agent':
        return `${baseContext}
Execute comprehensive market intelligence analysis. Focus on:
- Market size and growth trends
- Key competitors and their positioning
- Customer pain points and buying behavior
- Market opportunities and threats
- Data sources and confidence levels

Provide specific, actionable insights that will inform our positioning and offer strategy.`;

      case 'competitor_intelligence_agent':
        return `${baseContext}
Conduct deep competitor analysis. Focus on:
- Competitor positioning and differentiation
- Product offerings and pricing strategy
- Marketing channels and messaging
- Customer feedback and market perception
- Potential threats and opportunities

Provide intelligence that can be directly used to refine our competitive advantage.`;

      default:
        return `${baseContext}
Execute your specialized role as ${agentName} in the ${department} department.
Provide detailed, actionable outputs that advance our marketing objectives.`;
    }
  }

  /**
   * Estimate cost for agent execution
   */
  private estimateCost(agentName: string, tokenUsage: number): number {
    // Use the router to get model config and estimate cost
    const model = modelRouter.getModelForAgent(agentName);
    const modelName = agentName.includes('heavy') ? 'gemini-2.0-flash-thinking-exp-01-21' :
                     agentName.includes('reasoning') ? 'gemini-2.5-pro-preview-06-05' :
                     agentName.includes('general') ? 'gemini-2.5-flash-preview-05-20' : 'gemini-1.5-flash';

    return modelRouter.estimateCost(
      modelName as any,
      Math.ceil(tokenUsage * 0.6), // Input tokens estimate
      Math.ceil(tokenUsage * 0.4)  // Output tokens estimate
    );
  }

  private calculateProgress(
    executionPlan: OrchestratorContext['execution_plan'],
    completed: string[],
    failed: string[]
  ): number {
    const totalAgents = executionPlan.reduce((sum, dept) => sum + dept.agents.length, 0);
    const processedAgents = completed.length + failed.length;
    return Math.round((processedAgents / totalAgents) * 95); // Leave 5% for finalization
  }

  private estimateCompletionTime(executionPlan: OrchestratorContext['execution_plan']): string {
    // Rough estimation: 5-10 min per department
    const deptCount = executionPlan.length;
    const estimatedHours = (deptCount * 7.5) / 60; // 7.5 min avg per dept
    return new Date(Date.now() + estimatedHours * 60 * 60 * 1000).toISOString();
  }

  private compileFinalPackage(state: OrchestratorContext): any {
    // Compile all results into final deliverable
    return {
      goal: state.goal,
      completed_at: new Date().toISOString(),
      departments_executed: state.execution_plan.map(p => p.department),
      key_outputs: {
        market_intelligence: state.results.market_intel_agent,
        positioning: state.results.positioning_architect_agent,
        moves: state.results.move_designer_agent,
        creative_assets: state.results.creative_director_agent,
        distribution_plan: state.results.distribution_strategist_agent
      },
      metrics: {
        total_agents: state.completed_agents.length + state.failed_agents.length,
        success_rate: state.completed_agents.length / (state.completed_agents.length + state.failed_agents.length),
        token_usage: state.token_budget.used
      }
    };
  }

  // =====================================================
  // PUBLIC API
  // =====================================================

  /**
   * Execute a workflow
   */
  async executeWorkflow(
    userId: string,
    goal: string,
    context?: {
      campaign_context?: Record<string, unknown>;
      icp_context?: Record<string, unknown>;
    }
  ): Promise<OrchestratorContext> {
    const initialState: OrchestratorContext = {
      user_id: userId,
      goal: goal,
      campaign_context: context?.campaign_context || {},
      icp_context: context?.icp_context || {},
      current_state: OrchestratorState.INITIALIZING,
      execution_plan: [],
      completed_agents: [],
      failed_agents: [],
      results: {},
      dead_end_detected: false,
      dead_end_reason: undefined,
      token_budget: {
        total: 0,
        used: 0,
        remaining: 0,
        last_checkpoint: 0
      },
      execution_metadata: {
        start_time: new Date().toISOString(),
        estimated_completion: undefined,
        current_step: undefined,
        progress_percentage: 0
      }
    };

    const app = this.graph.compile();
    const rawFinalState = await app.invoke(initialState);

    // Validate and normalize the final state to ensure schema compliance
    const finalState = toOrchestratorContext(rawFinalState);

    console.log("🏁 Workflow execution completed");
    return finalState;
  }

  /**
   * Get registered agents
   */
  getRegisteredAgents(): string[] {
    return Array.from(this.agentExecutors.keys());
  }

  /**
   * Get workflow status
   */
  getWorkflowStatus(workflowId: string): any {
    // Could implement status tracking
    return budgetMiddleware.getBudgetStatus(workflowId);
  }
}

// =====================================================
// GLOBAL ORCHESTRATOR INSTANCE
// =====================================================

export const orchestrator = new RaptorFlowOrchestrator();

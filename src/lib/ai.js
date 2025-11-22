import { getVertexAIUrl, TASK_TYPES } from '../utils/vertexAI';

// AI-powered answer suggestions
export const generateAnswerSuggestions = async (question, partialAnswer, answers) => {
  try {
    const url = getVertexAIUrl(TASK_TYPES.CREATIVE_FAST);
    const context = Object.keys(answers).length > 0
      ? `Based on previous answers:\n${JSON.stringify(answers, null, 2)}\n\n`
      : '';

    const systemInstruction = `You are a helpful business strategist. The user is answering: "${question.prompt}". ${partialAnswer ? `They've started with: "${partialAnswer}".` : ''} Provide 2-3 concise, specific suggestions to help them complete their answer. Keep suggestions under 50 words each.`;

    const payload = {
      contents: [{ parts: [{ text: context + systemInstruction }] }],
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "ARRAY",
          items: { type: "STRING" }
        },
        maxOutputTokens: 500,
        temperature: 0.7
      }
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) return [];
    const data = await response.json();
    const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!jsonText) return [];
    return JSON.parse(jsonText);
  } catch (error) {
    console.warn('Answer suggestions failed:', error);
    return [];
  }
};

// AI-powered ICP generation from onboarding data
export const generateICPFromAnswers = async (answers) => {
  try {
    const url = getVertexAIUrl(TASK_TYPES.CREATIVE_REASONING);

    // Convert answers to a more readable format for the AI
    let contextString = "Analyze the following business onboarding data and generate an Ideal Customer Profile (ICP):\n\n";
    
    // Handle both raw answers object and array of questions if available
    // If we just have the answers object, we iterate through keys
    for (const [key, value] of Object.entries(answers)) {
       if (typeof value === 'object' && value !== null) {
          contextString += `${key}: ${JSON.stringify(value)}\n`;
       } else {
          contextString += `${key}: ${value}\n`;
       }
    }

    const systemInstruction = `
    Based on this business data, generate 1-3 detailed Ideal Customer Profiles (ICPs).
    Each ICP should include:
    - Name/Label for the cohort
    - Industry and company size
    - Key characteristics and behaviors
    - Pain points they're trying to solve
    - Why they're a good fit
    - Detailed psychographics and demographics suitable for the cohort builder

    Return as a JSON array of cohort objects.
    `;

    const payload = {
      contents: [{ parts: [{ text: contextString + systemInstruction }] }],
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "ARRAY",
          items: {
            type: "OBJECT",
            properties: {
              name: { type: "STRING" },
              executiveSummary: { type: "STRING" },
              demographics: {
                type: "OBJECT",
                properties: {
                  companySize: { type: "STRING" },
                  industry: { type: "STRING" },
                  revenue: { type: "STRING" },
                  location: { type: "STRING" }
                }
              },
              buyerRole: { type: "STRING" },
              psychographics: {
                type: "OBJECT",
                properties: {
                  values: { type: "ARRAY", items: { type: "STRING" } },
                  decisionStyle: { type: "STRING" },
                  priorities: { type: "ARRAY", items: { type: "STRING" } }
                }
              },
              painPoints: { type: "ARRAY", items: { type: "STRING" } },
              goals: { type: "ARRAY", items: { type: "STRING" } },
              behavioralTriggers: { type: "ARRAY", items: { type: "STRING" } },
              communication: {
                type: "OBJECT",
                properties: {
                  channels: { type: "ARRAY", items: { type: "STRING" } },
                  tone: { type: "STRING" },
                  format: { type: "STRING" }
                }
              },
              budget: { type: "STRING" },
              timeline: { type: "STRING" },
              decisionStructure: { type: "STRING" }
            }
          }
        },
        maxOutputTokens: 4000,
        temperature: 0.8
      }
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`ICP generation failed: ${response.status}`);
    const data = await response.json();
    const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!jsonText) throw new Error("No ICP content generated");
    return JSON.parse(jsonText);
  } catch (error) {
    console.error('ICP generation failed:', error);
    return [];
  }
};

// AI-powered competitive positioning insights
export const generatePositioningInsights = async (answers) => {
  try {
    const url = getVertexAIUrl(TASK_TYPES.REASONING);

    const businessDescription = answers['q1'] || answers.businessDescription || '';
    const positioning = answers['q6'] || answers.market_position?.positioning || '';

    const systemInstruction = `
    Analyze this business and provide strategic positioning insights:
    Business: ${businessDescription}
    Current Positioning: ${positioning}

    Provide:
    1. Key differentiators (3-5 points)
    2. Competitive advantages
    3. Positioning gaps or opportunities
    4. Market positioning strategy recommendations

    Be specific, actionable, and concise.
    `;

    const payload = {
      contents: [{ parts: [{ text: systemInstruction }] }],
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "OBJECT",
          properties: {
            differentiators: { type: "ARRAY", items: { type: "STRING" } },
            advantages: { type: "ARRAY", items: { type: "STRING" } },
            gaps: { type: "ARRAY", items: { type: "STRING" } },
            recommendations: { type: "ARRAY", items: { type: "STRING" } }
          }
        },
        maxOutputTokens: 1500,
        temperature: 0.7
      }
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`Positioning insights failed: ${response.status}`);
    const data = await response.json();
    const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!jsonText) throw new Error("No insights generated");
    return JSON.parse(jsonText);
  } catch (error) {
    console.error('Positioning insights failed:', error);
    return null;
  }
};

// Generate follow-up questions
export const generateVertexAIQuestions = async (answers, initialQuestions) => {
  // Use general purpose model for onboarding question generation
  const url = getVertexAIUrl(TASK_TYPES.GENERAL_PURPOSE);
  let contextString = "Here is the client's onboarding intake so far:\n\n";

  if (initialQuestions) {
    initialQuestions.forEach(q => {
        if (q.type === 'multi') {
        q.fields.forEach(field => {
            const ans = answers[field.id] || "Not answered";
            contextString += `Question: ${field.label}\nAnswer: ${ans}\n\n`;
        });
        } else if (q.type === 'map') {
        const loc = answers[q.id];
        const locStr = loc ? (loc.address || `${loc.lat}, ${loc.lng}`) : "Not provided";
        contextString += `Question: ${q.prompt}\nAnswer: ${locStr}\n\n`;
        } else {
        const ans = answers[q.id] || "Not answered";
        contextString += `Question: ${q.prompt}\nAnswer: ${ans}\n\n`;
        }
    });
  } else {
      // Fallback if initialQuestions not provided
      contextString += JSON.stringify(answers, null, 2);
  }

  const systemInstruction = `
    You are an expert brand strategist reviewing a new client's intake form.
    Your goal is to identify 1-3 critical gaps, vague statements, or areas that need specific clarification to build a marketing strategy.
    
    Tone: Professional, "Normal Human", concise, slightly editorial. Not robotic.
    
    Task: Generate 1 to 3 follow-up questions based on their answers.
    - If they were vague about their customer, ask for specifics.
    - If they didn't mention constraints, ask about them.
    - If they didn't mention competitors, ask who they lose deals to.
    
    Return strictly a JSON array of objects. No markdown formatting.
  `;

  const payload = {
    contents: [{
      parts: [{ text: contextString + "\n\n" + systemInstruction }]
    }],
    generationConfig: {
      responseMimeType: "application/json",
      responseSchema: {
        type: "ARRAY",
        items: {
          type: "OBJECT",
          properties: {
            category: { type: "STRING" },
            title: { type: "STRING" },
            prompt: { type: "STRING" },
            placeholder: { type: "STRING" }
          },
          required: ["category", "title", "prompt", "placeholder"]
        }
      }
    }
  };

  const delays = [1000, 2000, 4000, 8000, 16000];
  
  for (let i = 0; i < delays.length; i++) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error(`API Error: ${response.status}`);
      const data = await response.json();
      const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
      
      if (!jsonText) throw new Error("No content generated");
      return JSON.parse(jsonText);
    } catch (error) {
      console.warn(`Vertex AI Attempt ${i + 1} failed:`, error);
      if (i === delays.length - 1) throw error; 
      await new Promise(resolve => setTimeout(resolve, delays[i]));
    }
  }
};

// Generate cohort from specific inputs (for CohortsBuilder)
export const generateCohortFromInputs = async (inputs) => {
    // Convert inputs to the format expected by generateICPFromAnswers
    // inputs object from CohortsBuilder: businessDescription, productDescription, targetMarket, etc.
    
    // Reuse the generic ICP generation but with these specific inputs
    const icps = await generateICPFromAnswers(inputs);
    if (icps && icps.length > 0) {
        return icps[0]; // Return the first/best match
    }
    throw new Error("Could not generate cohort from inputs");
};

// Compute psychographics based on cohort data
export const computePsychographics = async (cohort) => {
    try {
      const url = getVertexAIUrl(TASK_TYPES.CREATIVE_REASONING);
      
      const systemInstruction = `
      Analyze this customer cohort and generate deep psychographic insights.
      Cohort: ${JSON.stringify(cohort)}
      
      Return a JSON object with:
      - values (array of strings)
      - decisionStyle (string)
      - personalityTraits (array of strings)
      - interests (array of strings)
      - painPsychology (object with primaryFear, motivation, emotionalDriver)
      - contentPreferences (object with format, tone, channels)
      `;
  
      const payload = {
        contents: [{ parts: [{ text: systemInstruction }] }],
        generationConfig: {
          responseMimeType: "application/json",
          responseSchema: {
            type: "OBJECT",
            properties: {
              values: { type: "ARRAY", items: { type: "STRING" } },
              decisionStyle: { type: "STRING" },
              personalityTraits: { type: "ARRAY", items: { type: "STRING" } },
              interests: { type: "ARRAY", items: { type: "STRING" } },
              painPsychology: {
                type: "OBJECT",
                properties: {
                  primaryFear: { type: "STRING" },
                  motivation: { type: "STRING" },
                  emotionalDriver: { type: "STRING" }
                }
              },
              contentPreferences: {
                type: "OBJECT",
                properties: {
                  format: { type: "STRING" },
                  tone: { type: "STRING" },
                  channels: { type: "ARRAY", items: { type: "STRING" } }
                }
              }
            }
          },
          maxOutputTokens: 1500,
          temperature: 0.7
        }
      };
  
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
  
      if (!response.ok) throw new Error(`Psychographics computation failed: ${response.status}`);
      const data = await response.json();
      const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
      if (!jsonText) throw new Error("No content generated");
      return JSON.parse(jsonText);
    } catch (error) {
      console.error('Psychographics computation failed:', error);
      // Fallback to some default data if AI fails
      return {
        values: cohort.psychographics?.values || ['Efficiency', 'Innovation'],
        decisionStyle: cohort.psychographics?.decisionStyle || 'Analytical',
        personalityTraits: ['Professional', 'Goal-oriented'],
        interests: ['Industry Trends', 'Best Practices'],
        painPsychology: {
          primaryFear: 'Falling behind',
          motivation: 'Growth',
          emotionalDriver: 'Success'
        },
        contentPreferences: {
            format: 'Case Studies',
            tone: 'Professional',
            channels: ['LinkedIn', 'Email']
        }
      };
    }
  };

// Generate market alternatives based on user's business context
export const generateMarketAlternatives = async (answers) => {
  try {
    const url = getVertexAIUrl(TASK_TYPES.CREATIVE_REASONING);
    
    const businessDescription = answers['q1'] || answers.businessDescription || '';
    const offer = answers['q2'] || answers.productDescription || '';
    const targetMarket = answers['q4'] || answers.targetMarket || '';
    
    const systemInstruction = `
    Based on this business information:
    - Business: ${businessDescription}
    - Offer: ${offer}
    - Target Market: ${targetMarket}
    
    Generate 4-6 specific alternatives that customers might consider instead of this business.
    These should be realistic competitors or alternative solutions in their market.
    
    For each alternative, provide:
    - id: a short kebab-case identifier
    - label: descriptive name (3-5 words max)
    - x: position on price axis (-2 to +2, where -2 is much cheaper, +2 is much more expensive)
    - y: position on service axis (-2 to +2, where -2 is self-serve/DIY, +2 is done-for-you/high-touch)
    
    Make positions spread across the map to show market diversity.
    `;

    const payload = {
      contents: [{ parts: [{ text: systemInstruction }] }],
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "ARRAY",
          items: {
            type: "OBJECT",
            properties: {
              id: { type: "STRING" },
              label: { type: "STRING" },
              x: { type: "NUMBER" },
              y: { type: "NUMBER" }
            },
            required: ["id", "label", "x", "y"]
          }
        },
        maxOutputTokens: 1000,
        temperature: 0.8
      }
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`Market alternatives generation failed: ${response.status}`);
    const data = await response.json();
    const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!jsonText) throw new Error("No alternatives generated");
    return JSON.parse(jsonText);
  } catch (error) {
    console.error('Market alternatives generation failed:', error);
    // Fallback to generic alternatives
    return [
      { id: 'diy', label: 'DIY tools / software', x: -1.5, y: -1.8 },
      { id: 'freelancers', label: 'Freelancers / contractors', x: -0.5, y: 0.3 },
      { id: 'agencies', label: 'Full-service agencies', x: 1.2, y: 1.5 },
      { id: 'nothing', label: 'Do nothing', x: -1.8, y: -1.2 }
    ];
  }
};

// Generate price comparison options tailored to their market
export const generatePriceOptions = async (answers, alternatives) => {
  try {
    const url = getVertexAIUrl(TASK_TYPES.CREATIVE_FAST);
    
    const businessDescription = answers['q1'] || answers.businessDescription || '';
    const offer = answers['q2'] || answers.productDescription || '';
    
    const systemInstruction = `
    Based on this business and the alternatives they face:
    - Business: ${businessDescription}
    - Offer: ${offer}
    - Alternatives: ${JSON.stringify(alternatives)}
    
    Generate 5 price comparison options that are specific to their market context.
    Each option should have:
    - value: numeric position (-2 to +2)
    - label: descriptive label that makes sense for their industry
    
    Options should range from "much cheaper than alternatives" to "much more expensive than alternatives".
    Make the language natural and specific to their context.
    `;

    const payload = {
      contents: [{ parts: [{ text: systemInstruction }] }],
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "ARRAY",
          items: {
            type: "OBJECT",
            properties: {
              value: { type: "NUMBER" },
              label: { type: "STRING" }
            },
            required: ["value", "label"]
          }
        },
        maxOutputTokens: 500,
        temperature: 0.7
      }
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`Price options generation failed: ${response.status}`);
    const data = await response.json();
    const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!jsonText) throw new Error("No price options generated");
    return JSON.parse(jsonText);
  } catch (error) {
    console.error('Price options generation failed:', error);
    // Fallback to generic options
    return [
      { value: -2, label: 'Much cheaper' },
      { value: -1, label: 'A bit cheaper' },
      { value: 0, label: 'About the same' },
      { value: 1, label: 'A bit more expensive' },
      { value: 2, label: 'Much more expensive' }
    ];
  }
};

// Generate service level options for their industry
export const generateServiceOptions = async (answers) => {
  try {
    const url = getVertexAIUrl(TASK_TYPES.CREATIVE_FAST);
    
    const businessDescription = answers['q1'] || answers.businessDescription || '';
    const offer = answers['q2'] || answers.productDescription || '';
    
    const systemInstruction = `
    Based on this business:
    - Business: ${businessDescription}
    - Offer: ${offer}
    
    Generate 4 service level options that describe the spectrum of service/support in their industry.
    Each option should have:
    - value: numeric position (-2 to +2, where -2 is self-serve/DIY, +2 is done-for-you/high-touch)
    - label: descriptive label specific to their industry (5-7 words max)
    
    Make labels natural and relevant to how they'd describe service levels in their market.
    `;

    const payload = {
      contents: [{ parts: [{ text: systemInstruction }] }],
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "ARRAY",
          items: {
            type: "OBJECT",
            properties: {
              value: { type: "NUMBER" },
              label: { type: "STRING" }
            },
            required: ["value", "label"]
          }
        },
        maxOutputTokens: 400,
        temperature: 0.7
      }
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`Service options generation failed: ${response.status}`);
    const data = await response.json();
    const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!jsonText) throw new Error("No service options generated");
    return JSON.parse(jsonText);
  } catch (error) {
    console.error('Service options generation failed:', error);
    // Fallback to generic options
    return [
      { value: -2, label: 'Mainly a self-serve tool' },
      { value: -1, label: 'Tool + some support' },
      { value: 0, label: 'Done-with-you' },
      { value: 2, label: 'Fully done-for-you / very high support' }
    ];
  }
};

// Generate specialization options based on their target market
export const generateSpecializationOptions = async (answers) => {
  try {
    const url = getVertexAIUrl(TASK_TYPES.CREATIVE_FAST);
    
    const businessDescription = answers['q1'] || answers.businessDescription || '';
    const bestFit = answers['q4'] || answers.targetMarket || '';
    const badFit = answers['q5'] || '';
    
    const systemInstruction = `
    Based on this business:
    - Business: ${businessDescription}
    - Best Fit Customers: ${bestFit}
    - Bad Fit Customers: ${badFit}
    
    Generate 3 specialization level options that describe how focused/niche vs broad their offering is.
    Each option should have:
    - value: identifier ('niche', 'medium', or 'broad')
    - label: descriptive label specific to their market (8-12 words max)
    
    Make labels reflect actual customer types they described, not generic terms.
    - 'niche' should reference their specific best-fit customer
    - 'medium' should reference a broader but still defined segment
    - 'broad' should reference the widest applicable market
    `;

    const payload = {
      contents: [{ parts: [{ text: systemInstruction }] }],
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "ARRAY",
          items: {
            type: "OBJECT",
            properties: {
              value: { type: "STRING" },
              label: { type: "STRING" }
            },
            required: ["value", "label"]
          }
        },
        maxOutputTokens: 400,
        temperature: 0.7
      }
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`Specialization options generation failed: ${response.status}`);
    const data = await response.json();
    const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!jsonText) throw new Error("No specialization options generated");
    return JSON.parse(jsonText);
  } catch (error) {
    console.error('Specialization options generation failed:', error);
    // Fallback to generic options
    return [
      { value: 'niche', label: 'Built for a specific type of customer' },
      { value: 'medium', label: 'Works for lots of different businesses' },
      { value: 'broad', label: 'Works for almost anyone' }
    ];
  }
};

// Generate reasoning for price positioning
export const generatePriceReasoning = async (answers, selectedPosition, alternatives) => {
  try {
    const url = getVertexAIUrl(TASK_TYPES.CREATIVE_FAST);
    
    const offer = answers['q2'] || answers.productDescription || '';
    const businessDescription = answers['q1'] || answers.businessDescription || '';
    
    const systemInstruction = `
    Based on this business information:
    - Business: ${businessDescription}
    - Offer: ${offer}
    - Selected Price Position: ${selectedPosition} (scale: -2 to +2)
    - Market Alternatives: ${JSON.stringify(alternatives)}
    
    Generate a brief, natural explanation (1-2 sentences) for why this price position makes sense.
    Reference specific details from their offer description if possible.
    Be conversational and insightful, not robotic.
    `;

    const payload = {
      contents: [{ parts: [{ text: systemInstruction }] }],
      generationConfig: {
        responseMimeType: "text/plain",
        maxOutputTokens: 200,
        temperature: 0.7
      }
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`Price reasoning generation failed: ${response.status}`);
    const data = await response.json();
    const reasoning = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!reasoning) throw new Error("No reasoning generated");
    return reasoning.trim();
  } catch (error) {
    console.error('Price reasoning generation failed:', error);
    // Fallback reasoning
    return "Based on your offer description, we placed you at this price point relative to typical alternatives in your market.";
  }
};

// Generate reasoning for service positioning
export const generateServiceReasoning = async (answers, selectedPosition) => {
  try {
    const url = getVertexAIUrl(TASK_TYPES.CREATIVE_FAST);
    
    const offer = answers['q2'] || answers.productDescription || '';
    const businessDescription = answers['q1'] || answers.businessDescription || '';
    const timeSpent = answers['q7b'] || '';
    
    const systemInstruction = `
    Based on this business information:
    - Business: ${businessDescription}
    - Offer: ${offer}
    - Time Available: ${timeSpent}
    - Selected Service Position: ${selectedPosition} (scale: -2 to +2, where -2 is self-serve, +2 is high-touch)
    
    Generate a brief, natural explanation (1-2 sentences) for why this service level position makes sense.
    Reference specific details from their offer or time commitment if possible.
    Be conversational and insightful, not robotic.
    `;

    const payload = {
      contents: [{ parts: [{ text: systemInstruction }] }],
      generationConfig: {
        responseMimeType: "text/plain",
        maxOutputTokens: 200,
        temperature: 0.7
      }
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`Service reasoning generation failed: ${response.status}`);
    const data = await response.json();
    const reasoning = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!reasoning) throw new Error("No reasoning generated");
    return reasoning.trim();
  } catch (error) {
    console.error('Service reasoning generation failed:', error);
    // Fallback reasoning
    return "Based on your offer description, we placed you at this service level relative to typical alternatives in your market.";
  }
};
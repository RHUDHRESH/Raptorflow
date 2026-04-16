# RAPTORFLOW COMPLETE PAGES & SCREENS SPECIFICATION
## Every Single Page In Extreme Detail

**Status:** Comprehensive Master Reference  
**Last Updated:** April 2026  
**Scope:** Every customer-facing page, screen, interface, and view

---

# TABLE OF CONTENTS
1. Pre-Product Pages (Landing, Auth)
2. Foundation Onboarding (21 Screens)
3. Primary Dashboard & The Office
4. Campaign Management (Creation, Execution, Analytics)
5. Muse Conversation Interface
6. Competitive Intelligence Dashboard
7. Daily Wins & Nudges
8. Council & Debate Viewer
9. Content Engine & Asset Management
10. Settings & Preferences
11. Administrative & Diagnostics

---

---

# SECTION 1: PRE-PRODUCT PAGES

## 1.1 — Landing Page
**Route:** `/` (public)  
**Authentication Required:** No  
**Purpose:** Initial product discovery and signup conversion

### What the User Sees
The landing page is a single-page application highlighting the core RaptorFlow promise: a 21-agent marketing office staffed by legendary marketing minds. The page is divided into three primary sections.

**Section 1: Hero** (above the fold)
- Headline: "Your Marketing Office. Staffed by 21 AI Strategists."
- Subheading: "Stop managing a tool. Start managing a team."
- Two-button CTA: "Start Free" (white button, primary action) and "Watch Demo" (outlined button)
- Hero visual: 1980s office illustration (low-poly flat style) rendered at ~600px width, showing the full office with all 21 agents at their desks. The illustration is static on mobile, animated on desktop (subtle idle animations, occasional pager flash, file movement through lobby)
- Trust markers: "Built for Indian SMBs • Designed for ₹5,000/month • No setup fees"

**Section 2: The Problem-Solution Framework** (300px section below hero)
- Headline: "Solving the Real Problem of Marketing Intelligence"
- Problem statement: "You're wearing 21 hats. Sales hat. Copywriting hat. Analytics hat. Competitive strategy hat. You're competent at some of these. You're faking it at most of them."
- Three-column layout showing:
  - **Column 1 (Problem):** Icon of one person looking overwhelmed. Text: "You're doing marketing alone" (or with minimal team). Bullet points of typical pain (limited time, gaps in expertise, no competitive monitoring)
  - **Column 2 (Gap):** Arrow visual showing "→ what you need"
  - **Column 3 (Solution):** Icon of 21 people. Text: "21 full-time specialists. For ₹5,000/month." Bullet points (actually works on your business, learns from your data, never sleeps)

**Section 3: The Agents Gallery** (400px section)
- Headline: "Meet Your Executives"
- Subheading: "All 21 agents. All at your desk."
- Grid layout showing 12 Council Legends in a 3x4 grid, then 8 Support Specialists in a 2x4 grid below them, plus the Campaign Strategist in its own row at the bottom
- Each agent card shows: 
  - Low-poly portrait illustration (consistent with Office style)
  - Agent name (e.g., "David Ogilvy")
  - Role tag (e.g., "Ad Copy & Copy Strategy")
  - One-line description (e.g., "Crafts copy that persuades through precision and proof")
  - On hover: Brief personality note (e.g., "Ogilvy: Cranky about mediocre work. Obsessed with research.")
- Cards are clickable and expand to show a fuller 2-3 sentence description, key expertise areas, and a sample piece of their voice/perspective

**Section 4: How It Works** (visible below fold, ~500px)
- Headline: "The RaptorFlow Method"
- Five-step visual flow (left to right on desktop, stacked on mobile):
  - **Step 1: Build Your Foundation** (icon: building with foundation) — "21 strategic questions. 20 minutes of thinking. The blueprint that makes every recommendation specific to your business."
  - **Step 2: Your Agents Are Trained** (icon: graduation cap) — "All 21 agents read your Foundation. They understand your positioning, your ICP, your competitive landscape, your goals. They're not generic."
  - **Step 3: Daily Briefings** (icon: sunrise over office) — "Every morning: what changed overnight, what your competitors did, what you should focus on today, what's working in your campaigns."
  - **Step 4: Campaign Planning** (icon: three agents at a table) — "Write a brief. The Council debates it. 3+ perspectives. A campaign that's thought through, not thrown together."
  - **Step 5: Everything Improves** (icon: upward arrow) — "Each campaign teaches the system. 30 days in, your agents are smarter than month 1. 6 months in, they're genuinely expert in your business."

**Section 5: Proof & Social Proof** (300px)
- Testimonial carousel (3-4 rotating testimonials from early beta customers)
- Each testimonial: customer name, company, role, quote (30-50 words), star rating (5 stars)
- Simple nav dots to scroll through testimonials

**Section 6: Pricing** (200px)
- Single tier, prominently displayed
- "₹5,000 per month"
- Subtext: "One workspace. 21 agents. Everything included."
- Feature list (3 lines):
  - ✓ Unlimited campaigns
  - ✓ Daily intelligence briefings
  - ✓ Council sessions (Tactical & Strategic)
  - ✓ Content generation at agent quality

**Section 7: Footer CTA** (150px)
- "Ready to build your marketing office?"
- Large button: "Start Free"
- Subtext: "14-day free trial. No credit card required."

**Section 8: Footer Navigation**
- Links: Privacy, Terms, Documentation, Contact
- Social: LinkedIn link
- Company: © 2026 RaptorFlow

### Technical Details
- **Framework:** Next.js 15 (Server Components for content, Client Components for interactive elements)
- **Animations:** Framer Motion for Office illustration animations
- **Asset Delivery:** Images optimized via Next.js Image component
- **Analytics:** Events tracked for CTA clicks, section scrolling
- **Responsiveness:** Fully responsive from 320px to 2560px

### Edge Cases
- If JavaScript is disabled, page is still readable (no animations, Office illustration still visible as static image)
- Mobile: Hero section optimized for smaller viewports, grid sections become single-column
- Loading state: Office illustration lazy-loads below fold

---

## 1.2 — Sign-Up Page
**Route:** `/signup`  
**Authentication Status:** Not authenticated  
**Purpose:** Create account via Clerk integration

### What the User Sees

The sign-up flow is minimal and split into two screens.

**Screen 1: Email/OAuth Choice**
- Heading: "Create Your RaptorFlow Account"
- Two options stacked vertically:
  - **Option 1 (Primary):** Large button with Google logo: "Continue with Google"
  - **Option 2 (Secondary):** "Or create with email" with an email input field and "Continue" button
- Small link below: "Already have an account? Sign in"
- No other distractions

**Screen 2 (if email choice): Verify Email**
- Text: "We've sent a verification link to [email]"
- "Open email app" button (mobile) or "Continue" button (desktop if user is already in email)
- "Resend link" option after 30 seconds

### Clerk Integration Details
- Clerk handles OAuth (Google), email/password, and email verification
- After successful authentication, user is redirected to `/workspace-name` page (the single pre-Foundation question)

---

## 1.3 — Workspace Setup Page
**Route:** `/workspace-setup`  
**Authentication Status:** Authenticated, workspace not yet created  
**Purpose:** Name the workspace before Foundation begins

### What the User Sees

**Single Screen:**
- Heading: "What Would You Like to Name Your Marketing Office?"
- Subheading: "This name appears on your office door and in your workspace URL. Choose something that feels real."
- Text input field with placeholder: "e.g., 'Acme Marketing', 'The Brand Lab', 'Sarah's Studio'"
- Validation: 3-50 characters, alphanumeric + spaces/hyphens only
- Real-time URL slug generation shown below: "Your workspace URL will be: `raptorflow.io/acme-marketing`"
- "Create Workspace" button (primary, enabled only when input is valid)
- Loading state: "Building your office..." with a subtle loading animation

### On Submit
- Workspace is created with org_id generated
- User is redirected to Foundation Screen 1
- Workspace name is stored in workspaces table
- 3-second transition animation shows the office building with the workspace name on the door

---

---

# SECTION 2: FOUNDATION ONBOARDING (21 SCREENS)

The Foundation is the strategic questionnaire that configures the entire system. All 21 screens are presented in sequence. The user cannot skip screens or go backward (though they can return to edit before final submission).

## Common Foundation UX Patterns

All 21 screens follow the same structural pattern:

**Header** (fixed or sticky)
- Progress bar showing current screen (e.g., "Screen 7 of 21")
- Workspace name in corner
- Small "Save Draft" indicator (shows "Saving..." when data is written)

**Main Content Area**
- Screen number and title (e.g., "Screen 7: Secondary ICPs")
- Subheading explaining what this screen captures and why it matters (1-2 sentences)
- Form fields or input areas (specific to each screen)
- Helper text below each field where needed (e.g., "Your customer's perspective, not your product description")

**Navigation Footer**
- "Previous" button (disabled on Screen 1, visible on all others)
- "Save & Continue" button (primary action, validation required before enabling)
- "Save Draft" link (always available)
- Page counter: "[Screen #] of 21"

**Auto-Save Behavior**
- Every field is debounced and auto-saved after 2 seconds of inactivity
- Saving indicator appears briefly
- If network error, user is notified and "Save Now" button appears

---

## 2.1 — Screen 1: Your Website
**Title:** "Where Does Your Business Live?"  
**Purpose:** Extract initial business information via website URL

### What the User Sees

**Input Section:**
- Heading: "Paste your website URL"
- Single URL input field with placeholder: "https://yourwebsite.com"
- Field has built-in validation (must be valid URL format)
- Submit button: "Scan Website" (or auto-triggered on blur if URL is valid)

**Scanning State (Blocking):**
- While "Quick Scan" runs (5-7 seconds), a loading state appears:
  - Spinner animation
  - Text: "Reading your website... this should take 5-10 seconds"
  - Estimated time remaining shown

**Error States:**
- **Invalid URL:** "That doesn't look like a valid website URL. Try again with https:// included."
- **URL not reachable:** "We couldn't reach that website. Is it publicly accessible? Try again or continue without pre-population."
- **Timeout:** "The scan took too long. You can still continue — we'll pre-fill some fields if the scan completes in the background."

**Success State:**
After Quick Scan completes, the same screen shows:
- Message: "Got it. We're scanning deeper into your website. While that runs, let's talk about your business."
- Below that, Screen 2 fields appear immediately (the Quick Scan data has been extracted and is being used to pre-populate Screen 2)
- "Continue to Screen 2" button becomes enabled

### Technical Details
- **Quick Scan:** Synchronous, lightweight, uses reqwest HTTP GET
- **Deep Scan:** Asynchronous, runs in background using chromiumoxide, results arrive via WebSocket and populate screens as user progresses
- **Data Extracted:** Business name, tagline, industry, description, OpenGraph tags
- **Storage:** Quick scan results stored in onboarding_state table, keyed by org_id

---

## 2.2 — Screen 2: Business Basics
**Title:** "Tell Me About Your Business"  
**Purpose:** Capture core business identity and model

### What the User Sees

**Form Layout (Vertical Stack):**

**Field 1: Business Name**
- Label: "What is your business called?"
- Input: Text field (50 char limit)
- Pre-populated: From Quick Scan website title if available
- Helper: "Exactly as you want it referred to throughout the platform"
- Validation: Required, min 2 characters

**Field 2: Business Model**
- Label: "How does your business make money?"
- Input: Dropdown with six options:
  - Product-based (one-time purchases)
  - Subscription/recurring
  - Service-based (hourly/project rate)
  - Hybrid (products + services)
  - Marketplace/platform
  - B2B SaaS
- Pre-populated: Inferred from website if available
- Helper: "This determines how we think about your customer journey"
- Validation: Required

**Field 3: Business Stage**
- Label: "Where are you in your growth journey?"
- Input: Radio buttons (6 options):
  - Pre-launch (no customers yet)
  - Early stage (0-100 customers)
  - Growth stage (100-1,000 customers)
  - Scale stage (1,000+ customers)
  - Mature business (stable revenue, optimizing)
  - Enterprise (large team, complex org)
- Helper: "This helps us calibrate recommendations"
- Validation: Required

**Field 4: Industry/Category**
- Label: "What industry are you in?"
- Input: Searchable dropdown (100+ industries)
- Pre-populated: From Quick Scan if possible
- Helper: "If not exact, choose closest match"
- Validation: Required

**Field 5: Team Size**
- Label: "How many people work on marketing?"
- Input: Dropdown:
  - Just me
  - 1-2 others
  - 3-5
  - 6-10
  - 10+
- Helper: "Affects how we think about your capacity"
- Validation: Required

**Field 6: Primary Description**
- Label: "In one sentence: what does your business do?"
- Input: Text area (100 char limit, grows as user types)
- Placeholder: "We [do X] for [who]"
- Pre-populated: From Quick Scan meta description if available
- Helper: "This is what you'd say to someone who's never heard of you"
- Validation: Required, min 20 chars

### Validation & Submission
- All fields required
- "Save & Continue" button enables only when all fields have values
- Screen auto-saves as user fills in each field (debounced)

---

## 2.3 — Screen 3: B2B vs B2C Choice
**Title:** "Who Are Your Customers?"  
**Purpose:** Determine customer type (B2B, B2C, or both) — affects ICP structure downstream

### What the User Sees

**Three Large Card Options (clickable):**

**Option 1: B2B**
- Card header: "Primarily Businesses" (B2B)
- Description: "I sell to other companies or professionals"
- Example: "SaaS, HR software, agencies, consulting, B2B manufacturing"
- Icon: Multiple business building silhouettes

**Option 2: B2C**
- Card header: "Primarily Consumers" (B2C)
- Description: "I sell directly to individuals"
- Example: "E-commerce, D2C, courses, coaching, consumer apps"
- Icon: Multiple individual person silhouettes

**Option 3: Both**
- Card header: "Both B2B and B2C"
- Description: "I serve both businesses and individuals"
- Example: "Platforms with dual audiences, agencies selling to both types"
- Icon: Mixed silhouettes

**Additional Input (if user selects "Both"):**
- Follow-up question: "Which is your primary market?" (dropdown: B2B or B2C)
- Helper: "We'll optimize the ICP screens for your primary market"

### Validation & Storage
- Selection is mandatory before continuing
- Selection is stored in onboarding_state
- Determines which ICP structure appears on Screen 6 (B2B vs B2C fields)

---

## 2.4 — Screen 4: Products & Services
**Title:** "What Do You Offer?"  
**Purpose:** Catalog products/services with customer outcomes and pricing

### What the User Sees

**Subheading:** "List your main offerings. For each, describe what it does for the customer (not just the features)."

**Add Product Card Button** (if no products exist):
- Large button: "+ Add Your First Offering"
- Clicking shows first product card in edit mode

**Product Card (repeating):**
Each product is displayed as an editable card with the following fields:

**Field 1: Offering Name**
- Label: "What do you call this?"
- Input: Text field (50 char)
- Example: "Custom Web Design"
- Validation: Required

**Field 2: Category**
- Label: "What is this?"
- Input: Text field (50 char) — short description like "Managed SaaS Tool", "Professional Service", "Physical Product"
- Helper: "One or two words describing the category"
- Validation: Required

**Field 3: Customer Outcome** (CRITICAL FIELD)
- Label: "What does the customer gain from this?"
- Input: Text area (200 char limit)
- Placeholder starts with: "After buying this, the customer can..." OR "This solves the problem of..."
- Helper: "Focus on what changes in the customer's life, not the features"
- Background AI: When user completes this field and moves to the next, a Flash-Lite inference runs in background. If the answer is heavily feature-focused (mentions "dashboard", "integrations", "API", "3-month contract"), a suggestion appears: "You described the features. Here's how your customers might say it instead: '[suggestion]'. Accept, edit, or keep yours."
- Validation: Required, min 15 chars

**Field 4: Pricing**
- Label: "How much does this cost?"
- Input: Two-part structure
  - **Part A:** Dropdown (pricing model):
    - One-time purchase
    - Monthly subscription
    - Annual subscription
    - Tiered pricing (monthly)
    - Tiered pricing (annual)
    - Project-based quote
    - Hourly rate
    - Other / Custom
  - **Part B:** Number field(s) based on selection
    - One-time: Single number field (e.g., "₹50,000")
    - Monthly subscription: Single number field (e.g., "₹5,000")
    - Tiered: Multiple rows for tier name + price (e.g., "Starter ₹1,000", "Pro ₹5,000", "Enterprise Custom")
    - Project-based: Range field (e.g., "₹25,000 - ₹100,000")
    - Hourly: Number field (e.g., "₹2,000/hour")
- Helper: "This helps us understand your market positioning"
- Validation: At least one number field must have a value

**Card Actions:**
- At bottom of each card: "Delete" button (red, text button)
- Below product cards: "+ Add Another Offering" button

**Multiple Products Guidance:**
- Text: "You can add up to 5 offerings. If you have more, focus on the top 3-5."
- If user tries to add 6th: "You've added 5. More than this makes the Foundation unwieldy. You can document additional offerings later. Continue with the top 5."

**Pre-Population from Deep Scan:**
- If Deep Scan has completed and found product information on website, the first 1-3 product cards appear pre-populated with:
  - Suggested names from website
  - Category guesses
  - Pricing if found
  - A note: "We found this on your website. Edit if needed."

### Validation & Submission
- At least 1 offering required
- All fields in each offering must be filled
- Button enables when requirements met

---

## 2.5 — Screen 5: The Problem You Solve
**Title:** "What Problem Do You Solve?"  
**Purpose:** Articulate the customer's problem (not the solution, the problem)

### What the User Sees

**Subheading:** "The most important question: what was your customer's situation before they found you?"

**Three Prompts (Stacked Vertically):**

**Prompt 1: The Situation**
- Label: "Before your customer found you, what was their situation? What were they dealing with every day?"
- Input: Text area (400 char limit, grows as needed)
- Placeholder: "Describe the objective situation, the facts of what they were dealing with"
- Helper: "Focus on the facts, not the emotion — yet"
- Validation: Required, min 30 chars

**Prompt 2: The Frustration**
- Label: "What specific frustration did this situation create? What made it genuinely annoying, costly, or stressful?"
- Input: Text area (400 char limit)
- Placeholder: "Now get at the emotional dimension"
- Helper: "This is what emotionally resonant copy needs to reflect"
- Validation: Required, min 30 chars

**Prompt 3: What They Tried (CRITICAL)**
- Label: "What had they tried before to solve this that didn't work? Why did it fall short?"
- Input: Text area (400 char limit)
- Placeholder: "Name alternatives they tried and why they failed"
- Helper: "This defines the competitive landscape as seen through customer experience"
- Validation: Required, min 30 chars

**AI Synthesis Section** (appears after all three fields complete):
- Separator line
- Heading: "Here's how your Campaign Strategist would describe your problem articulation:"
- The synthesis (400-500 chars): A strategically clear, single-statement articulation of the problem
- Three action buttons below:
  - "Use This" (primary, blue)
  - "Edit & Use" (secondary, opens synthesis in an editable text area)
  - "Use My Own Words" (tertiary, shows an empty text area for user to write their own)
- Whichever path the user takes becomes the problem statement stored in Foundation

### Technical Details
- **AI Synthesis:** Flash-Lite inference call runs when all three prompts are completed
- **Synthesis Prompt:** Instructs the model to synthesize the three answers into a single strategic problem statement, 50-80 words
- **Storage:** User's choice (synthesis or custom) is stored in Foundation JSON

---

## 2.6 — Screen 6: Primary Ideal Customer Profile (ICP)
**Title:** "Your Primary Ideal Customer Profile"  
**Purpose:** Define the primary target customer in depth

### B2B Version of Screen 6:

**Form Layout:**

**Section 1: Role Identity**

**Field 1A: Job Title/Role**
- Label: "What is this person's job title or function?"
- Input: Text field with suggestions (searchable dropdown of common titles)
- Examples: "Marketing Manager", "VP of Sales", "Operations Director", "HR Manager"
- Validation: Required

**Field 1B: Company Type**
- Label: "What kind of company do they work for?"
- Input: Text field with suggestions
- Examples: "SaaS company", "Manufacturing", "Professional services", "E-commerce", "Non-profit"
- Validation: Required

**Field 1C: Company Size**
- Label: "How big is their company?"
- Input: Dropdown:
  - 1-10 people
  - 11-50 people
  - 51-200 people
  - 201-1,000 people
  - 1,000+ people
- Validation: Required

**Field 1D: Industry**
- Label: "What industry?"
- Input: Searchable dropdown (100+ industries)
- Validation: Required

**Section 2: Goals & Pressures**

**Field 2A: Primary Goal**
- Label: "What is this person trying to achieve in their role right now? What's the main thing they're focused on?"
- Input: Text area (150 char)
- Example: "Increase sales pipeline by 40% without doubling the team size"
- Helper: "What does success look like for them in their role?"
- Validation: Required

**Field 2B: Pressure/Constraints**
- Label: "What pressure is their organization putting on them?"
- Input: Text area (150 char)
- Example: "Company wants faster growth but budget is frozen"
- Helper: "What are they being judged on? What's hard?"
- Validation: Required

**Field 2C: Success Definition**
- Label: "In the context of what you solve, what would success look like for them?"
- Input: Text area (150 char)
- Example: "Implement a system that requires minimal training and gets buy-in from their team"
- Helper: "Frame it in terms of your solution's value"
- Validation: Required

**Section 3: Decision Dynamics**

**Field 3A: Decision Authority**
- Label: "Does this person make the buying decision?"
- Input: Dropdown:
  - Yes, they decide alone
  - They're the primary decision-maker but need approval
  - They're one voice among several
  - They advise but don't decide
- Validation: Required

**Field 3B: Other Stakeholders**
- Label: "Who else is involved in the decision?"
- Input: Text area (150 char)
- Example: "CFO, CTO, and their direct boss (VP Sales)"
- Helper: "List other stakeholders and their roles"
- Validation: Optional

**Field 3C: What Matters to Approvers**
- Label: "What does the approver care about?"
- Input: Text area (150 char)
- Example: "ROI, security compliance, whether it integrates with existing systems"
- Helper: "Different stakeholders care about different things"
- Validation: Optional

**Section 4: Language & Self-Perception**

**Field 4A: How They Describe the Problem**
- Label: "How would this person describe their problem in their own words?"
- Input: Text area (150 char)
- Example: "We're losing deals to competitors who seem faster"
- Helper: "Real phrases they'd use, not marketing language"
- Validation: Required

**Field 4B: Success Language**
- Label: "What words do they use to describe success?"
- Input: Text area (150 char)
- Example: "Quick implementation, minimal disruption, measurable ROI"
- Helper: "These are the language patterns for your copy"
- Validation: Required

**Field 4C: Industry/Professional Vocabulary**
- Label: "What industry-specific terms are they fluent in?"
- Input: Text area (100 char)
- Example: "ARR, CAC, LTV, sales velocity, pipeline"
- Helper: "Jargon they use with peers that shows expertise"
- Validation: Optional

**Field 5: Persona Name**
- Label: "Give this customer a name"
- Input: Text field (50 char)
- Placeholder: "e.g., 'The Scaling D2C Founder', 'The Overwhelmed Clinic Owner'"
- Format suggestion: "The [Adjective] [Role or Identity]"
- Helper: "This is how we'll refer to this ICP throughout the platform"
- Validation: Required

**Deep Scan Integration:**
- If Deep Scan has found testimonials, website "About" pages, or case studies, suggested answers appear in relevant fields
- Each suggestion is marked as "From your website" in a light badge

### B2C Version of Screen 6:

**Section 1: Life Situation**

**Field 1A: Age Range**
- Label: "Age range?"
- Input: Dropdown:
  - 18-25
  - 26-35
  - 36-45
  - 46-55
  - 56-65
  - 65+
- Validation: Required

**Field 1B: Life Stage**
- Label: "What life stage?"
- Input: Dropdown:
  - Student
  - Early career (0-5 years in field)
  - Established career (5+ years)
  - New parent
  - Parent with kids in school
  - Parent with adult kids
  - Retired
  - Other
- Validation: Required

**Field 1C: Income Band**
- Label: "Approximate annual income?"
- Input: Dropdown:
  - <₹5 Lakhs
  - ₹5-10 Lakhs
  - ₹10-20 Lakhs
  - ₹20-40 Lakhs
  - ₹40+ Lakhs
- Helper: "Affects purchasing power and decision speed"
- Validation: Required

**Field 1D: Location Type**
- Label: "Where do they live?"
- Input: Dropdown:
  - Metro city (Delhi, Mumbai, Bangalore, Chennai, etc.)
  - Tier 2 city
  - Tier 3 city
  - Rural/small town
- Validation: Required

**Field 1E: Household Structure**
- Label: "Household situation?"
- Input: Dropdown:
  - Single, no dependents
  - Single, with dependents
  - Partnered, no dependents
  - Partnered, with children
  - Other
- Validation: Required

**Section 2: Aspirations & Identity**

**Field 2A: What They Want to Be**
- Label: "What does this person want to become or be known for?"
- Input: Text area (150 char)
- Example: "A successful solopreneur who doesn't sacrifice family time"
- Helper: "What's their aspiration or identity goal?"
- Validation: Required

**Field 2B: What This Product Says About Them**
- Label: "What does buying/using your product say about who they are?"
- Input: Text area (150 char)
- Example: "That they're serious about their craft and willing to invest in themselves"
- Helper: "What identity does your product unlock for them?"
- Validation: Required

**Field 2C: Values**
- Label: "What values matter to them?"
- Input: Text area (100 char)
- Example: "Authenticity, quality, supporting small businesses, sustainability"
- Helper: "What do they care about beyond your product?"
- Validation: Required

**Section 3: Behaviour & Consumption**

**Field 3A: Discovery Channels**
- Label: "Where do they discover new products/services?"
- Input: Multiple checkboxes:
  - Instagram
  - YouTube
  - TikTok
  - LinkedIn
  - Twitter/X
  - Facebook
  - Pinterest
  - Blogs/newsletters
  - Podcasts
  - Word of mouth / friends
  - Google search
  - Other
- Validation: At least 1 required

**Field 3B: Platforms They're Active On**
- Label: "Which social platforms are they actually *active* on (posting, engaging) vs just scrolling?"
- Input: Text area (100 char)
- Example: "Instagram stories, LinkedIn, YouTube (watching, not posting)"
- Helper: "Distinguish between platforms they use vs platforms where they engage"
- Validation: Required

**Field 3C: Media Consumption**
- Label: "What media/content do they consume?"
- Input: Text area (150 char)
- Example: "Business podcasts, Instagram travel accounts, YouTube tech reviews, newsletters about personal finance"
- Helper: "Books, podcasts, blogs, YouTube channels, newsletters?"
- Validation: Required

**Field 3D: Recommendations**
- Label: "Who do they take recommendations from?"
- Input: Text area (100 char)
- Example: "Close friends, trusted YouTube creators in their niche, Twitter thought leaders in their field"
- Helper: "Influencers, friends, experts, celebrities?"
- Validation: Required

**Section 4: Language & Self-Perception** (same as B2B)

**Field 4A: How They Describe Their Problem**
- Label: "How would they describe their problem in their own words?"
- Input: Text area (150 char)
- Validation: Required

**Field 4B: Success Language**
- Label: "What words do they use for success?"
- Input: Text area (150 char)
- Validation: Required

**Field 4C: Relevant Vocabulary**
- Label: "Any specialized vocab they use?"
- Input: Text area (100 char)
- Validation: Optional

**Field 5: Persona Name**
- Same as B2B version
- Validation: Required

---

## 2.7 — Screen 7: Secondary ICPs
**Title:** "Secondary Customer Profiles (Optional)"  
**Purpose:** Identify up to 2 additional customer profiles beyond the primary

### What the User Sees

**Subheading:** "Do you serve other types of customers? Identify up to 2 secondary profiles. (Optional)"

**Initial State:**
- Text: "You've defined your primary ICP. Does your business serve other distinct customer groups?"
- Two options:
  - "Yes, I have secondary ICPs" (leads to Section A)
  - "No, my primary ICP is my market" (skips to Screen 8)

**Section A (if "Yes" selected): Secondary ICP Cards**

**Add Secondary ICP Button:**
- Text: "+ Add Secondary ICP"
- Enabled only if fewer than 2 secondary ICPs exist
- Clicking shows a simplified ICP form (similar to Screen 6 but condensed: 8 fields instead of 15)

**Secondary ICP Card** (repeating, max 2):
Compact version of Screen 6 with these fields only:
1. Persona Name
2. Role/Identity (B2B) or Life Situation (B2C)
3. Primary Goal
4. How They Describe the Problem
5. Industry (B2B) or Location (B2C)
6. Platform/Channel Preferences
7. What They Value (B2B: in your solution; B2C: in general)
8. One differentiating note (what makes them distinct from primary ICP)

**Card Actions:**
- "Edit" link
- "Remove" link (danger state)

**Guidance:**
- Text: "Secondary ICPs are important if they drive meaningful revenue or represent strategic growth opportunity. If they're less than 10% of revenue, stick with primary ICP only."

---

## 2.8 — Screen 8: Competitive Landscape
**Title:** "Who Are Your Competitors?"  
**Purpose:** Identify and assess competitors

### What the User Sees

**Subheading:** "List the competitors your customers choose between when deciding to buy or not buy."

**Competitor Card Structure** (repeating):

**Initial Entry:**
- Button: "+ Add a Competitor"
- Opens a competitor entry card

**Competitor Card Fields:**

**Field 1: Competitor Name**
- Label: "What company are we watching?"
- Input: Text field (50 char)
- Example: "Competitor XYZ Inc"
- Validation: Required

**Field 2: Competitor Website**
- Label: "Their website URL"
- Input: URL field
- Validation: Required, must be valid URL
- On entry: System fetches the domain for favicon display

**Field 3: Their Positioning**
- Label: "How do they position themselves? (In their own words, from their website)"
- Input: Text area (150 char)
- Example: "The easiest way to manage remote teams"
- Helper: "Grab this from their website headline or tagline"
- Validation: Required

**Field 4: Their Strengths**
- Label: "What are they good at?"
- Input: Text area (150 char)
- Example: "Slick UX, enterprise features, 24/7 support"
- Helper: "What do customers choose them for?"
- Validation: Required

**Field 5: Their Weaknesses**
- Label: "Where do they fall short?"
- Input: Text area (150 char)
- Example: "Expensive, slow onboarding, limited customization"
- Helper: "What do customers complain about?"
- Validation: Optional

**Field 6: Competitive Context**
- Label: "Why do customers choose between you and them?"
- Input: Text area (150 char)
- Example: "We compete on price and ease of setup. They compete on advanced features."
- Helper: "What segment of the market is truly competitive?"
- Validation: Required

**Field 7: Their Price**
- Label: "What do they charge?"
- Input: Text field (100 char)
- Example: "$99/month" or "Starting at $5,000/project"
- Validation: Optional

**Field 8: Threat Level** (Optional Scoring)
- Label: "How significant a threat?"
- Input: Slider (1-5 scale)
  - 1 = Niche alternative
  - 5 = Direct, primary competitor
- Helper: "This helps us prioritize competitive monitoring"
- Validation: Optional

**Card Actions:**
- "Delete" button (danger)

**Multiple Competitors:**
- Recommendation: 3-5 primary competitors
- If user adds 7+: Warning: "You've listed many competitors. Consider focusing on the top 3-5 that customers most often compare you against."
- Minimum: 1 required

**Deep Scan Integration:**
- If Deep Scan has found competitor mentions on the website or in industry research, suggested competitor names appear with a badge: "From your website"

---

## 2.9 — Screen 9: Positioning Statement
**Title:** "Your Positioning"  
**Purpose:** Articulate how the business is positioned against competition

### What the User Sees

**Subheading:** "In one sentence: why should customers choose you over the alternatives?"

**Positioning Framework Explanation:**
- Brief explanation: "Positioning is not your tagline. It's the specific reason a customer in your market should choose you."
- Example format: "We are the [category] for [ICP] who care about [differentiation] because [reason why we own this]."

**Three Input Sections:**

**Section 1: Category**
- Label: "What category are you in?"
- Input: Text field (30 char)
- Placeholder: "e.g., 'AI marketing platform', 'freelance service', 'organic skincare brand'"
- Example: "Marketing intelligence platform"
- Helper: "How would you describe the type of thing you are?"
- Validation: Required

**Section 2: Differentiation**
- Label: "What is your differentiation? What's the one thing you own that competitors don't?"
- Input: Text area (100 char)
- Example: "For Indian SMBs. Flat pricing. 21 marketing specialists as AI agents."
- Helper: "Not multiple things — one core, distinctive thing"
- Validation: Required

**Section 3: Proof/Reason**
- Label: "Why do you own this? (What's your evidence?)"
- Input: Text area (150 char)
- Example: "We were built by marketing strategists who got tired of tools that ignored the human side."
- Helper: "Why are you credible here? Proof, experience, point of view?"
- Validation: Required

**Synthesized Positioning Statement** (auto-generated):
- After completing all three sections, a synthesized positioning statement appears below:
- Format: "We are the [category] for [ICP implicit from foundation] who value [differentiation], because [proof]."
- Example: "We are the marketing intelligence platform for Indian SMBs who need specialist expertise without hiring specialists, because we embed 21 marketing minds into one system."
- Edit/accept workflow:
  - "Use This Statement" (blue button)
  - "Edit & Refine" (opens statement in text area)
  - "Write My Own" (opens empty text area)

**Storage:**
- User's choice becomes the positioning_statement in Foundation

---

## 2.10 — Screen 10: Brand Voice
**Title:** "How Should Your Brand Sound?"  
**Purpose:** Define brand voice characteristics that guide all content

### What the User Sees

**Subheading:** "Your voice is how customers experience your personality. It's consistent across all channels."

**Five Voice Dimensions (Sliders):**

**Dimension 1: Formal ↔ Casual**
- Slider (1-100)
- At 20 (Formal): "Professional, measured, authoritative"
- At 50 (Balanced): "Professional but approachable"
- At 80 (Casual): "Conversational, relaxed, friendly"
- Example voices:
  - Formal (20): "RaptorFlow provides comprehensive marketing intelligence through AI-enabled platforms."
  - Balanced (50): "RaptorFlow gives you the marketing team you can't afford to hire."
  - Casual (80): "Forget hiring a whole marketing team. We did it for you in software."
- User's slider position sets their voice value

**Dimension 2: Serious ↔ Playful**
- Slider (1-100)
- At 20 (Serious): "No humor, focused on outcomes"
- At 50 (Balanced): "Mostly serious with occasional wit"
- At 80 (Playful): "Fun, witty, sometimes irreverent"
- Example voices:
  - Serious (20): "Marketing is a discipline that requires precision."
  - Balanced (50): "Marketing is science meets art, and we handle both."
  - Playful (80): "Marketing is what happens when chaos and strategy fall in love."

**Dimension 3: Practical ↔ Aspirational**
- Slider (1-100)
- At 20 (Practical): "Focus on solving problems, getting things done"
- At 50 (Balanced): "Solve problems AND inspire"
- At 80 (Aspirational): "Inspire to become better, bigger, bolder"

**Dimension 4: Data-Driven ↔ Intuitive/Emotional**
- Slider (1-100)
- At 20 (Data-Driven): "Lead with facts, numbers, evidence"
- At 50 (Balanced): "Mix data with insight and feeling"
- At 80 (Intuitive): "Lead with feeling and pattern recognition"

**Dimension 5: Inclusive ↔ Niche**
- Slider (1-100)
- At 20 (Inclusive): "Speak to everyone, no inside references"
- At 50 (Balanced): "Mostly broad, some insider language"
- At 80 (Niche): "Use industry jargon, assume expertise"

**Voice Descriptor Tags** (Multi-Select Checkboxes):

Below the sliders, a list of voice descriptors the user can select (multiple allowed):
- [ ] Direct
- [ ] Authentic
- [ ] Bold
- [ ] Approachable
- [ ] Technical
- [ ] Storytelling
- [ ] Witty
- [ ] Warm
- [ ] Authoritative
- [ ] Experimental
- [ ] Optimistic
- [ ] Irreverent

Helper: "Pick 3-5 that feel true"

**Voice Examples Section:**

**Field 1: Example 1 — Problem/Situation**
- Label: "Write a short message about how your brand sees a [customer problem]"
- Placeholder: "Your customers are overwhelmed with too many marketing tools"
- Input: Text area (200 char)
- Helper: "Show how your brand talks about the problem"

**Field 2: Example 2 — Your Solution/POV**
- Label: "How does your brand explain what you do?"
- Placeholder: "Explain your product in your voice"
- Input: Text area (200 char)
- Helper: "This shows voice through explanation"

**Field 3: Example 3 — Inspiration/Vision**
- Label: "What does your brand hope for? What's your vision?"
- Placeholder: "Where do you want to take your customers?"
- Input: Text area (200 char)
- Helper: "Show voice through aspiration"

**Voice Fingerprint** (Auto-Generated):
- After slider and descriptor selections, a visual representation of the voice emerges
- Text: "Your voice fingerprint: [synthesized 2-3 sentence description]"
- Example: "You sound professional and approachable—focused on outcomes but with warmth. You lead with data but aren't afraid of personality. You're speaking to someone who's serious about their business but enjoys some levity."

---

## 2.11 — Screen 11: Content Strategy
**Title:** "Your Content Strategy"  
**Purpose:** Define which content territories the brand owns

### What the User Sees

**Subheading:** "What types of content does your brand own? What are you known for creating?"

**Content Territory Cards** (Multi-Select):

A grid of cards representing different content types. User selects 3-5 that represent their primary content strategy.

**Available Content Territories:**
1. **Educational Content** — Teaches the audience how to solve problems (blog posts, tutorials, webinars)
2. **Inspirational Content** — Motivates, tells stories, builds aspiration (success stories, culture, vision)
3. **Entertainment Content** — Entertains the audience, brings joy or delight (humorous, surprising, unexpected)
4. **News & Commentary** — Reacts to industry news, trends, developments (opinions, hot takes, perspective)
5. **Behind-the-Scenes** — Shows how the business works, humanizes the team (culture, process, people)
6. **Promotional Content** — Directly sells or promotes products/services (offers, launches, exclusives)
7. **Community Content** — Builds connections between audience members, creates tribe (forums, discussions, community moments)
8. **Research & Original Insights** — Publishes proprietary research, original data (reports, analysis, data-driven insights)
9. **How-To / Practical** — Step-by-step guides, templates, tools (actionable how-tos, frameworks)
10. **Thought Leadership** — Positions founder/team as experts in a domain (deep expertise, point of view, philosophy)

**Each Card Shows:**
- Territory name
- One-sentence description
- Example (e.g., for Educational: "Blog post: 'How to set up your first email campaign'")
- On hover/click: Full description and 2-3 examples

**Territory Selection:**
- User can select 3-5 territories
- If fewer than 3: Prompt: "Select at least 3 territories"
- If more than 5: Prompt: "Focus on your strongest 5. More feels unfocused."

**Selected Territory Justification** (Optional but Encouraged):

For each selected territory, a text field appears:
- Label: "Why do you own this territory? Why is your audience expecting content from you here?"
- Input: Text area (100 char)
- Example: "We're the platform built *by* marketers, so we can talk credibly about how marketing actually works behind closed doors"
- Helper: "What makes you credible/authentic here?"

**Ownership Validation:**
- For each territory, text: "You own this if:"
- Bullet point explanation (e.g., for Educational: "Your audience trusts you to teach them something valuable, not sell to them")

---

## 2.12 — Screen 12: Channels & Platforms
**Title:** "Where Do Your Customers Find You?"  
**Purpose:** Map current and aspirational channel presence

### What the User Sees

**Subheading:** "Which channels is your audience on? Which are you actively using now?"

**Channel Selection Grid** (Major Channels):

A grid of cards, each representing a channel. For each channel, user indicates:
1. Is audience here? (Yes/No)
2. Are you active here now? (Yes/No)
3. Should this be primary? (Yes/No)

**Channels Presented:**
- Email (newsletters, email marketing)
- Instagram
- LinkedIn
- TikTok
- YouTube
- Twitter/X
- Facebook
- Pinterest
- Blog/Website
- Podcast (your own podcast)
- Podcast (guest appearances)
- Google Search (SEO)
- Google Ads
- LinkedIn Ads
- Meta Ads (Instagram/Facebook)
- WhatsApp/Telegram
- Discord/Communities
- Other [text field]

**For Each Channel, Three Questions:**

**Q1: Is Your Audience Here?**
- Dropdown: Yes / No / Unsure

**Q2: Are You Currently Active?**
- Dropdown: Yes, regularly / Occasionally / No, not yet

**Q3: Is This a Priority Channel?**
- Radio button: High priority / Medium priority / Low priority / Not a focus
- Visible only if Q1 and Q2 answered

**Current vs Aspirational View:**

The interface shows two sections:
- **Section A: Current State** (How the user operates now)
  - Channels where audience exists AND user is active
  - Shows effort allocation (user estimates %)
  
- **Section B: Aspirational State** (Where they want to be)
  - Channels they want to prioritize
  - Shows desired effort allocation

**Channel-Specific Micro-Questions** (Optional Deep Dive):

For each selected primary channel, additional context appears:

**For Instagram:**
- Posting frequency goal: Daily / 3x week / 1x week / Less frequent
- Content type: Reels / Stories / Feed posts / All
- Engagement strategy: Replies in comments / DMs / Community tab

**For LinkedIn:**
- Account type: Personal brand / Company page / Both
- Content focus: Thought leadership / Industry news / Recruiting / Product updates

**For YouTube:**
- Video cadence: Weekly / Bi-weekly / Monthly / Quarterly
- Video type: Tutorials / Vlogs / Interviews / Product demos
- Length: Short form (under 5 min) / Medium (5-15 min) / Long form (15+ min)

**For Email:**
- List size: <1,000 / 1-5K / 5-20K / 20K+
- Frequency: Daily / Weekly / Bi-weekly / Monthly / As-needed
- Segmentation: Not yet / Basic / Advanced

**For Blog/Website:**
- Publishing frequency: Daily / Weekly / Bi-weekly / Monthly / Occasional
- Primary SEO keywords: [Multi-tag input]

**Channel Gap Analysis:**
- At bottom, text: "You are active on [X channels]. Your audience is on [Y channels]. The gap: [Gap description]"
- If gap exists, suggestion: "Consider where highest-opportunity customers spend time but you're not yet active"

---

## 2.13 — Screen 13: Goals & KPIs
**Title:** "Your 90-Day Goals & KPIs"  
**Purpose:** Set primary goals and key performance indicators

### What the User Sees

**Subheading:** "What's the #1 thing you want to achieve in the next 90 days? How will you measure it?"

**Primary Goal** (Required):

**Field 1: Goal Category**
- Label: "What are you optimizing for?"
- Dropdown (6 options):
  - Revenue / Sales growth
  - Lead generation
  - Awareness / Reach
  - Engagement / Community
  - Customer retention
  - Product adoption / Usage
- Validation: Required

**Field 2: Goal Description**
- Label: "Describe your goal"
- Input: Text area (150 char)
- Placeholder: "e.g., 'Increase qualified leads by 50%'"
- Example: "Generate 100 qualified B2B leads in 90 days"
- Validation: Required, min 15 chars

**Field 3: Measurement (KPI)**
- Label: "How will you measure this?"
- Input: Based on goal category:
  - Revenue goal: "Increase revenue by [X]%" or "Achieve ₹[X] in revenue"
  - Leads: "Generate [X] leads" or "Increase leads by [X]%"
  - Awareness: "Reach [X] people" or "[X]% growth in impressions"
  - Engagement: "[X] new community members" or "[X]% engagement rate"
  - Retention: "[X]% retention rate" or "[X] repeat customers"
  - Adoption: "[X]% of users using feature" or "[X] new active users"
- Validation: Required

**Field 4: Current Baseline (Optional)**
- Label: "What's your current baseline?"
- Input: Number field
- Example: "Currently at 10 leads/month, want to get to 50 leads/month"
- Helper: "So we can measure progress"
- Validation: Optional but recommended

**Secondary Goals** (Optional):

Button: "+ Add Secondary Goal" (max 2)

Each secondary goal shows:
- Goal category dropdown
- Description text area
- KPI measurement field
- [Delete] link

**Goal Confidence**:

For the primary goal:
- Question: "How confident are you this goal is achievable in 90 days?"
- Slider: Not confident / Somewhat / Very confident
- Helper: "This helps us calibrate campaign recommendations"

**Goal-Setting Guidance:**

Text block: "RaptorFlow is most valuable when:"
- Bullet 1: "Goals are specific and measurable"
- Bullet 2: "Goals reflect where your business is right now (not aspirational 2-year goals)"
- Bullet 3: "There's clarity on what would be a win vs a miss"

---

## 2.14 — Screen 14: Frustrations & Constraints
**Title:** "What's Hard Right Now?"  
**Purpose:** Understand business constraints and pain points

### What the User Sees

**Subheading:** "What's your biggest marketing frustration? What would relieve the most pressure?"

**Frustration Options** (Multi-Select Checkboxes):

User selects 3-5 that resonate:

- [ ] **I don't have time to do everything** — Marketing is a side project or I'm the only marketer
- [ ] **I don't know if my marketing is working** — No clear visibility into ROI
- [ ] **My team lacks expertise** — I'm doing things I'm not confident in
- [ ] **Too many tools, not enough integration** — Marketing stack is fragmented
- [ ] **Competitors are outpacing us** — I don't know what competitors are doing
- [ ] **Budget constraints** — Limited marketing budget, hard to prove ROI for more
- [ ] **Content creation is overwhelming** — Too many channels, not enough content
- [ ] **Customer acquisition cost is rising** — Hard to find profitable channels
- [ ] **Customer retention is weak** — Losing customers I should keep
- [ ] **Decision-making is slow** — Hard to move fast on opportunities
- [ ] **Analytics / data interpretation** — Too much data, hard to know what matters
- [ ] **Team misalignment** — Not clear on strategy across the team
- [ ] **Nothing major, just optimization** — Marketing is running well, want to optimize

**For Each Selected Frustration, a Follow-Up:**

A text area appears below:
- Prompt: "Tell us more about this [frustration]. What would solving it look like?"
- Input: Text area (150 char)
- Example (for "I don't have time"): "I need marketing that doesn't require me to manually manage every task. Something that runs somewhat autonomously."

**Frustration Ranking:**

After selecting frustrations, user ranks them:
- Drag to reorder (most to least urgent)
- Helper: "What's the #1 thing that would make the biggest difference?"

**Impact Assessment:**

Text: "You selected [N] frustrations. Your #1 is [frustration]. We'll design your Strategist and your system to address this first."

---

## 2.15 — Screen 15: Budget & Resources
**Title:** "Marketing Budget & Resources"  
**Purpose:** Understand budget and operational capacity

### What the User Sees

**Subheading:** "How much are you investing in marketing right now?"

**Budget Question**:

**Field 1: Monthly Marketing Budget**
- Label: "What's your total monthly marketing budget?"
- Input: Dropdown:
  - Not yet allocated
  - <₹10,000
  - ₹10,000 - ₹25,000
  - ₹25,000 - ₹50,000
  - ₹50,000 - ₹100,000
  - ₹100,000 - ₹250,000
  - ₹250,000+
- Helper: "This helps us calibrate campaign scopes"
- Validation: Required

**Field 2: Budget Allocation**
- Label: "How is this budget typically split?"
- Input: Multi-part breakdown:
  - % on paid ads: [slider 0-100%]
  - % on content creation: [slider 0-100%]
  - % on tools/software: [slider 0-100%]
  - % on people/freelancers: [slider 0-100%]
  - % other: [auto-calculated remainder]
- Note: Sliders total to 100%
- Helper: "Where does your money go?"
- Validation: Automatically balanced

**Field 3: Team Capacity**
- Label: "How many hours/week can your team dedicate to marketing execution?"
- Input: Dropdown:
  - <5 hours
  - 5-10 hours
  - 10-20 hours
  - 20-40 hours
  - 40+ hours
- Helper: "Time spent executing campaigns, not planning"
- Validation: Required

**Field 4: Current Tools/Software Stack**
- Label: "What marketing tools are you currently using?"
- Input: Multi-select (common tools listed):
  - [ ] Email (Mailchimp, HubSpot, ActiveCampaign, etc.)
  - [ ] CRM (HubSpot, Pipedrive, Salesforce, etc.)
  - [ ] Social media management (Buffer, Later, Hootsuite, etc.)
  - [ ] Analytics (Google Analytics, Mixpanel, etc.)
  - [ ] Design (Figma, Canva, etc.)
  - [ ] Video (Adobe Premiere, CapCut, etc.)
  - [ ] Ads (Google Ads, Meta Ads Manager, etc.)
  - [ ] SEO (SEMrush, Ahrefs, etc.)
  - [ ] Landing pages (Unbounce, Leadpages, etc.)
  - [ ] Other: [text field]
- Helper: "So we can understand your workflow"
- Validation: Optional

---

## 2.16 — Screen 16: Brand Assets
**Title:** "Upload Brand Assets"  
**Purpose:** Collect logos, brand guidelines, existing content samples

### What the User Sees

**Subheading:** "Help us understand your visual brand and existing content style"

**Upload Sections** (Each has file uploader and optional description):

**Section 1: Logo**
- Label: "Your logo (PNG or SVG preferred)"
- Uploader: Drag-drop or click-to-upload
- File size limit: 5MB
- Accepted formats: PNG, SVG, JPG, PDF
- Helper: "We'll use this to ensure brand consistency"
- Validation: Optional but recommended

**Section 2: Brand Guidelines (if exists)**
- Label: "Brand guidelines document (PDF or Figma link)"
- Uploader: File upload OR paste Figma link
- File size limit: 25MB for PDF
- Helper: "If you have formal guidelines, sharing them helps immensely"
- Validation: Optional

**Section 3: Sample Content**
- Label: "Sample of your best content (URL or upload)"
- Uploader: Paste URL OR upload file (PDF, image, video)
- Helper: "A blog post, social media screenshot, or email you're proud of"
- Validation: Optional but recommended

**Section 4: Color Palette** (Alternative if no guidelines):
- Label: "What are your primary brand colors?"
- Input: Three color pickers (hex or RGB input)
- Helper: "Or upload a color palette image"
- Validation: Optional

**Section 5: Font Preferences**
- Label: "What fonts does your brand use?"
- Input: Text field
- Example: "Montserrat (headers), Open Sans (body)"
- Validation: Optional

**Uploaded Asset Gallery:**

Below uploads, a preview gallery shows:
- Uploaded logo (thumbnail)
- Brand guidelines (PDF preview or Figma thumbnail)
- Sample content (screenshot or video thumbnail)

---

## 2.17 — Screen 17: Team Information
**Title:** "Your Team"  
**Purpose:** Understand team size, structure, and contact info

### What the User Sees

**Field 1: Primary Contact Name**
- Label: "Your name"
- Input: Text field
- Validation: Required

**Field 2: Primary Contact Email**
- Label: "Your email"
- Input: Email field (pre-filled from Clerk auth if available)
- Validation: Required

**Field 3: Phone (Optional)**
- Label: "Phone number"
- Input: Phone field
- Validation: Optional

**Field 4: Team Member Profiles** (Optional):

Button: "+ Add Team Member"

Each team member card shows:
- Name (text field)
- Role (dropdown: Marketer, Developer, Designer, Sales, Founder, Other)
- Email (email field)
- [Remove] link

Helper: "If others will access this workspace, add them here. They can log in with their own account."

---

## 2.18 — Screen 18: Company Vision & Story
**Title:** "Your Story"  
**Purpose:** Understand the company's founding and vision

### What the User Sees

**Subheading:** "Help us understand what drives your business. What's the story behind it?"

**Field 1: Company Origin Story**
- Label: "How did your company start? Why did you start it?"
- Input: Text area (300 char)
- Placeholder: "Tell us the story. Why did you create this business?"
- Example: "Started as a frustration. I was marketing a SaaS and doing 21 different jobs. Realized most SMBs were in the same boat. So I built agents to share the workload."
- Validation: Required, min 50 chars

**Field 2: What Drives You / Company Mission**
- Label: "What are you trying to achieve beyond revenue?"
- Input: Text area (300 char)
- Example: "Give SMBs access to the marketing expertise they can't afford to hire"
- Helper: "What's the deeper why?"
- Validation: Required, min 30 chars

**Field 3: 3-Year Vision**
- Label: "Where do you want this business to be in 3 years?"
- Input: Text area (300 char)
- Example: "10,000 Indian SMBs using RaptorFlow. Zero companies with unsupported founders. Every SMB acting like they have a full marketing team."
- Helper: "Paint a picture of success"
- Validation: Required, min 30 chars

---

## 2.19 — Screen 19: Review & Strategist Setup — Part 1
**Title:** "Meet Your Campaign Strategist"  
**Purpose:** Introduce and configure the Campaign Strategist agent

### What the User Sees

**Subheading:** "Your Campaign Strategist is your primary point of contact in the office. Let's configure them."

**Part 1: Strategist Name**

**Field 1: Strategist Name**
- Label: "What would you like to name your Strategist?"
- Input: Text field (30 char)
- Placeholder: "e.g., 'Alex', 'Maya', 'Jordan'"
- Helper: "This is the agent who will be your voice in the office"
- Validation: Required
- Post-input note: "Meet [Name], your Campaign Strategist. They're reviewing everything you just told them."

---

## 2.20 — Screen 20: Strategist Configuration — Part 2
**Title:** "Configure Your Strategist's Personality"  
**Purpose:** Set the Strategist's communication style

### What the User Sees

**Subheading:** "How should [Strategist Name] communicate with you?"

**Three Personality Dimensions** (Each presented as two extremes with example):

**Dimension 1: Decisive ↔ Collaborative**
- Left (Decisive): Example message — "[Strategist name]: Here's what I recommend. Campaign should focus on awareness first. Are you ready to execute?"
- Right (Collaborative): Example message — "[Strategist name]: I see two clear paths. Path A prioritizes reach, Path B prioritizes conversion. Both are viable. What's your instinct?"
- Slider: User positions between the two
- Helper: "Do you want clear recommendations or options to choose from?"

**Dimension 2: Data-Driven ↔ Instinct-Driven**
- Left (Data-Driven): Example message — "[Strategist name]: Our conversion rate is 2.3%, which is 15% above your baseline from last quarter. This suggests the positioning resonates. I recommend increasing spend."
- Right (Instinct-Driven): Example message — "[Strategist name]: The messaging is resonating. I can feel it in the engagement patterns. Time to double down and scale spend."
- Slider: User positions
- Helper: "Do you want every recommendation backed by data or are you comfortable with pattern recognition?"

**Dimension 3: Direct ↔ Diplomatic**
- Left (Direct): Example message — "[Strategist name]: That positioning is too generic. It doesn't differentiate. Let's rewrite it."
- Right (Diplomatic): Example message — "[Strategist name]: Your positioning is clear, but I think we could sharpen the differentiation further. Would you be open to exploring some alternatives?"
- Slider: User positions
- Helper: "Do you want straight truth or careful feedback?"

**Personality Configuration Auto-Suggestion:**
- Text: "Based on your business stage, frustrations, and answers, I'm suggesting: [Suggested config]. You can adjust any dimension."

---

## 2.21 — Screen 21: Foundation Review & Office Build
**Title:** "Review Your Foundation"  
**Purpose:** Final review and office construction

### What the User Sees

**Part 1: Foundation Summary** (Read-Only Review):

The Strategist "briefs" the user on what they understand:

*"Hello, I'm [Strategist Name]. Here's what I understand about your business and what I'll be watching for:"*

The summary is presented as prose in the Strategist's configured voice:

**Example Briefing:**
"You're [Business Name], and you serve [Primary ICP Name] — [ICP one-sentence description]. The problem you solve is [problem statement]. Your positioning is [positioning statement].

Your primary goal for the next 90 days is [goal]. To measure success, we're looking at [KPI].

The competitors I'll be monitoring are [Competitor 1], [Competitor 2], and [Competitor 3].

Your brand should always sound [voice descriptors] — [voice example]. You own these content territories: [Content territories].

You'll be focusing on these channels: [Primary channels], with aspirational expansion to [Aspirational channels].

One more thing: your biggest frustration right now is [Top frustration]. I'm going to keep this front-and-center."

**Each section is clickable to edit** (user can navigate back to relevant screens):
- Click on ICP → goes to Screen 6
- Click on positioning → goes to Screen 9
- Click on goal → goes to Screen 13
- Click on voice → goes to Screen 10
- Etc.

**Part 2: Terms & Commitment**

Below the briefing:
- Checkbox: "I've reviewed the Foundation. I'm ready to build my office."
- Small text: "You can update your Foundation anytime. Changes might trigger campaign reviews."
- Validation: Checkbox must be checked before button enables

**Part 3: Build My Office Button**

Large primary button: "Build My Office"

On click:
- Spinner appears with message: "Building your office... this takes 8-12 seconds"
- Backend processes:
  - Foundation JSON compiled and stored in database
  - Vertex AI context cache populated
  - All 21 agent records initialized
  - Strategist personality config stored
  - Initial welcome message generated by Strategist
  - Office construction animation triggers
- After 8-12 seconds, user is redirected to main dashboard with Office view

---

---

# SECTION 3: PRIMARY DASHBOARD & THE OFFICE

## 3.1 — Main Dashboard / Office View (Default Landing After Auth)
**Route:** `/dashboard`  
**Authentication Required:** Yes  
**Purpose:** Primary interface showing The Office and all system activity

### Layout Overview

The dashboard is a three-panel layout:

**Panel 1: Left Sidebar** (20% width)
- Navigation menu
- Workspace info
- Quick stats
- Settings access

**Panel 2: Center Main Area** (60% width)
- The Office (1980s low-poly flat illustration, animated)
- Currently: Passive mode (office thumbnail, can zoom to active)

**Panel 3: Right Sidebar** (20% width)
- Daily Wins briefing
- Nudges/Alerts
- Quick action panel

### Panel 1: Left Sidebar

**Workspace Header:**
- Workspace name (e.g., "Acme Marketing")
- Workspace URL slug
- User avatar (placeholder circle or Gravatar)
- Dropdown menu with:
  - Profile settings
  - Workspace settings
  - Logout

**Navigation Menu** (Vertical):
- Dashboard (home icon) — currently selected
- Campaigns (folder icon) — leads to campaigns list
- Muse (speech bubble icon) — leads to Muse chat interface
- Intel (magnifying glass icon) — leads to competitive intelligence dashboard
- Content (document icon) — leads to content asset library
- Daily Wins (sunrise icon) — leads to daily briefing archive
- Settings (gear icon) — leads to workspace settings

**Quick Stats Widget** (below navigation):
- Displays 3 key metrics:
  - Metric 1: Active campaigns ([N])
  - Metric 2: Today's recommended actions ([N])
  - Metric 3: Competitive alerts ([N])
- Each is clickable and leads to relevant page

**Strategist Quick Access:**
- Box showing: "[Strategist Name] is ready" with a "Talk to them" button
- Button opens Muse chat interface with empty message area

---

### Panel 2: Center — The Office

**Office Rendering:**
- The office is a low-poly flat illustration rendered at full viewport height (or constrained to max 2000px)
- Office shows all 21 agents at their desks in the office layout (described in Section 3 of this doc and in Vol 3)
- The office is in passive mode (lower animation fidelity, simpler character animations)
- Company name appears on the office door

**Active Mode Toggle:**
- Text in top-right corner: "Passive mode • Click to expand"
- On click, office transitions to full-screen or expanded active mode with:
  - Full animation fidelity
  - Interactive character click-outs
  - Zoom and pan controls
  - Full speech bubble system
  - Full character detail on maximum zoom

**Office Event Animation Examples** (running continuously):
- Files being moved from lobby through the office
- Characters at desks idle-animating (subtle breathing, occasional hand movements)
- Pager notifications flashing when events occur
- Speech bubbles appearing and disappearing
- Characters moving to conference room if a Council session is active

**Zoom Controls** (in active mode):
- Scroll to zoom (mouse wheel or trackpad pinch)
- Buttons: + / - zoom buttons in bottom-right
- Zoom levels: 0.5x (full office) to 3x (character detail)
- Keyboard: +/- keys, arrow keys to pan

---

### Panel 3: Right Sidebar

**Section 1: Daily Wins Briefing** (Top of sidebar)

**Header:** "☀️ Today's Briefing" with timestamp "Generated 6:00 AM IST"

**Content Structure:**
- 1-3 recommended actions for today (prioritized)
- 1-2 competitive intelligence alerts
- 1-2 campaign status notes
- Text is summarized (50-100 words per item)

**Each Item Shows:**
- Headline (the action or alert)
- 1-2 sentences of context
- "Learn more" link (expands or navigates to relevant page)
- Icon indicating type (chart icon for campaign, eye icon for intel, star icon for action)

**Expand All:** Link at bottom to view full briefing

**Example Daily Wins:**
- "Competitor XYZ launched new pricing page. Updated their mid-tier plan. Consider checking our positioning."
- "Your Spring Campaign reach is 15% above projection. Recommend scaling budget by 10%."
- "Content approval pending: 3 social posts waiting for your review."

**Section 2: Nudges & Alerts** (Middle of sidebar)

**Header:** "Alerts" (or "🔔 New Alerts" if unread)

**Nudge Items** (Each shows):
- Alert icon (color-coded: green for positive, orange for attention, red for urgent)
- Alert text (20-30 words)
- Timestamp (e.g., "2 hours ago", "Today 9:30 AM")
- Action button (if applicable): "View", "Approve", "Discuss in Muse"

**Example Nudges:**
- 🟡 "Campaign ROI tracking below projection. Discuss replanning?"
- 🟢 "Social post generated 50% more engagement than average. Scale this approach?"
- 🔴 "Competitor launched promotion in your target market. Urgent review?"

**Max 3 visible**, with "View all alerts" link if more exist

**Section 3: Quick Actions** (Bottom of sidebar)

**Large Buttons** (stacked):
- "New Campaign" (blue button) — leads to campaign creation
- "Ask Muse" (secondary button) — opens Muse chat
- "Generate Content" (secondary button) — leads to content generation

---

## 3.2 — The Office (Detailed Interactive Specification)

**Reference:** See Addendum C and Vol 3 for complete animation, character, and event specifications

### Office Space (Visual Specification)

The office is a 1980s corporate office rendered in low-poly flat illustration style, approximately 2000 x 1200 pixels (scalable). The space includes:

**Key Locations in Office:**

1. **Strategist's Corner Office** (top-right corner)
   - Larger desk with nameplate showing strategist name
   - Window overlooking city skyline (1980s city view)
   - Desk surfaces with papers, pen holder, plants
   - Door with nameplate
   - File cabinets
   
2. **Council Legends' Desks** (12 desks arranged around perimeter)
   - Each labeled with agent name and title
   - Desk items reflect their domain (Ogilvy has research papers, Kotler has books, etc.)
   - Chairs at each desk
   - Desk lamps (1980s style)
   
3. **Support Specialists' Desks** (8 desks in secondary area)
   - Analytics Director
   - Content Director
   - Social Specialist
   - SEO Specialist
   - Paid Ads Specialist
   - Product Launch Specialist
   - Research Station (3 interns at desks with shared monitor)
   
4. **Conference Room** (center of office)
   - Large table (seats 21)
   - Whiteboard on wall
   - Chairs around table
   - Ceiling-mounted projector
   - Used for Council sessions and debates
   
5. **Server Room** (visible through glass window, back-left)
   - Vintage server towers (low-poly)
   - Blinking lights representing activity
   - Pulsing animation representing data processing
   
6. **Reception/Lobby Area** (front-right)
   - Reception desk with Maya (receptionist)
   - File cabinets for incoming documents
   - Wall showing company name
   - Entry door
   
7. **Ambient Elements:**
   - Floor with wood texture or carpet pattern
   - Walls with 1980s paint color (muted earth tones or gray)
   - Ceiling with recessed lighting and drop tiles
   - Windows showing 1980s city view outside
   - Plants in corners (pothos, ficus)
   - Framed art/posters on walls (generic business motivational art)
   - Water cooler / break area
   - File storage shelving

### Character Rendering & Animation

**Each Character Consists Of:**
- Head (stylized, proportional)
- Body (torso, simplified)
- Arms (2, articulated at shoulders and elbows)
- Legs (2, simplified, usually seated)
- Facial features (simplified: eyes, mouth, nose as basic shapes)
- Clothing (color-coded by domain/personality)
- Optional accessories (Ogilvy's glasses, Patel's watch, etc.)

**Character States & Animations:**

Each character has a state machine with these states:
- **Idle** — Character sits at desk, subtle breathing animation, occasional hand repositioning
- **Speaking** — Mouth animates, hands gesture, body slightly animates with speech
- **Listening** — Posture shifts to attentive position, head nods occasionally, expression attentive
- **Reading** — Character leans forward slightly, head down toward papers or screen
- **Walking** — Legs animate in walk cycle, arms swing, moves across office (used when going to conference room)
- **Thinking** — Hand to chin, slight sway, focused expression
- **Alert/Concerned** — Body posture shifts, eyebrows animate, pager flashes near character
- **Celebrating** — Arms raise, body bounces, celebration animation plays
- **At Whiteboard** — Character stands at whiteboard, arms articulate as if writing/pointing

**Animation Fidelity Modes:**

**Passive Mode Animations** (reduced fidelity):
- Each character has 1-2 idle animations only
- Idle animation repeats every 3-4 seconds
- Breathing (subtle scale change: 1.0 → 1.02 → 1.0)
- Frame rate: 30 FPS
- No complex multi-step sequences
- No cross-character interactions

**Active Mode Animations** (full fidelity):
- Each character has 6-8 animation states as listed above
- Smooth transitions between states
- Hand articulation during speaking
- Facial expression changes
- Body posture shifts
- Frame rate: 60 FPS
- Full cross-character interaction sequences
- Particle effects (confetti on celebrations, sparkles on alerts, etc.)

### Event-to-Animation Mapping

**System Events Trigger Specific Animations:**

| System Event | Animation Triggered | Duration | Character |
|---|---|---|---|
| Campaign brief submitted | File delivery animation | 2 seconds | Maya + Strategist |
| Brief approved | Strategist celebrates | 1 second | Strategist |
| Council session initiated | Pager notification flash | Visible 2 sec | All called agents |
| Council agents walk to conference | Walking animation | 1-2 seconds each | Called agents |
| Council session debate starts | Seated at table animation | Holds until debate ends | All participants |
| Agent speaking in debate | Speaking + hand gestures | Variable (5-30 sec) | Speaking agent |
| Other agents listening | Listening posture + nods | Variable | Listening agents |
| Agent response completing | Transition to listening | 1 second | Responding agent |
| Council synthesis starts | Strategist stands and moves to presentation | 2 seconds | Strategist |
| Content generation task assigned | Focused work animation | Visible for 5-10 sec | Assigned agent |
| Content generation completes | Brief celebration | 1 second | Assigned agent |
| QA review starts | QA Director at desk, reviewing | Visible during review | QA Director |
| High-priority intel alert | Research Station alert sequence | 3 seconds | Research interns |
| Daily wins generation starts | Morning meeting animation | 5-10 seconds | Strategist + interns |

### Speech Bubbles & Character Voice

**Three Types of Speech Content:**

1. **Passive Mode Bubbles** (ephemeral, no context)
   - 3-5 second display time
   - Character-specific (Ogilvy's critical observations, Godin's questions, Sutherland's contrarian takes)
   - No accumulation — once they disappear, they're gone
   - Appear 2-3 times per hour in passive mode
   - Example Ogilvy bubble: "That claim needs proof."
   - Example Godin bubble: "Who is this for?"

2. **Active Mode Bubbles** (session-specific, persisting)
   - Appear during specific events (Council debates, content review)
   - Full message text visible (50-200 words)
   - Persist until event completes or user dismisses
   - Example: During a Council debate, bubbles show agent positions and arguments

3. **Group Chat Bubbles** (ongoing conversation thread)
   - Appear in a dedicated chat panel (visible on-demand in Office sidebar)
   - Show ongoing conversations between agents about campaigns, intel, and strategy
   - Example Ogilvy to Bernbach: "Your positioning is too clever. Customers will miss it."
   - Example Vaynerchuk reply: "They'll get it. Gen Z gets it. That's who we're reaching."

**Snark Engine** (AI-Generated Personality Content):

Snark bubbles are generated by specialized AI prompts that create character-authentic, witty, non-revealing comments. They:
- Reference ongoing campaigns or recent events
- Are never mean-spirited (witty, not cruel)
- Never reveal system internals
- Maintain character voice perfectly
- Trigger conditions can be customized (after debates, post-task completion, on idle state, etc.)

---

## 3.3 — Office Interaction Details

### Click-to-Expand Interactions (Active Mode)

**Clicking on a Character:**
- Popup appears showing:
  - Character name
  - Current activity ("Working on: Spring Campaign social copy")
  - Last completed task ("Reviewed competitor ad copy")
  - Most recent group chat message
  - "View full conversations" link
  - [Close] button

**Clicking on Conference Room (when Council session active):**
- Transitions to full-screen debate view (Section 4: Council Viewer)

**Clicking on Research Station:**
- Shows current intelligence scan status
- Displays recent findings
- "View full intelligence dashboard" link

**Clicking on Server Room:**
- Shows system activity (PRL ripple creation rate, consolidation status, token usage)
- Visible only if active/expert mode enabled in settings

### Zoom and Pan

**Zoom Behavior:**
- Scroll wheel (mouse) or pinch (trackpad) zooms
- Buttons (+ / - in corner) also zoom
- Zoom range: 0.5x (full office visible) to 3.0x (extreme character close-up)
- Smooth animated zoom with easing

**Zoom Level Detail Rendering:**
- At 0.5-1.0x: All characters visible, simplified details
- At 1.0-1.5x: Office layout clear, character detail visible
- At 1.5-2.0x: Character faces visible, desk details visible
- At 2.0x+: Extreme detail mode (facial expressions, desk accessories, nameplate text readable)

**Pan Behavior:**
- Click and drag to pan
- Arrow keys also pan
- Panning constrained to office bounds (cannot pan to empty space)

---

---

# SECTION 4: CAMPAIGN MANAGEMENT

## 4.1 — Campaign List View
**Route:** `/campaigns`  
**Purpose:** View all campaigns (active, draft, completed, archived)

### What the User Sees

**Header Section:**
- Title: "Campaigns"
- Subheading: "Your marketing campaigns and Moves"
- "New Campaign" button (blue, primary)

**Filter & Sort Bar:**
- Tabs: All / Active / Draft / Completed / Archived
- Sort dropdown: By date / By performance / By status
- Search field: "Search campaigns by name"

**Campaign Cards** (Grid Layout, 2-3 cards per row):

Each campaign card shows:
- **Campaign name** (heading)
- **Status badge:** Draft (gray) / Active (green) / Paused (yellow) / Replanning (orange) / Completed (blue) / Archived (gray)
- **Dates:** "Start date - End date" (e.g., "Mar 1 - May 15")
- **Primary goal:** One-line (e.g., "Generate 50 qualified leads")
- **Progress bar:** Visual representation of timeline progress
- **Key metric snapshot:**
  - For active campaigns: Current KPI progress (e.g., "15/50 leads (30%)")
  - For completed campaigns: Final result (e.g., "52/50 leads (104%)")
- **Hover/Mobile Details:**
  - Brief description of strategic approach
  - Number of Moves (e.g., "4 Moves")
  - Last updated timestamp
- **Quick Actions:**
  - Three-dot menu (...) with options:
    - View details / Edit
    - Pause (if active)
    - View Council session
    - Archive
    - Delete (if draft)

**Empty State** (if no campaigns):
- Icon: Empty folder or marketing campaign illustration
- Text: "No campaigns yet. Ready to build one?"
- Button: "Create Your First Campaign"

---

## 4.2 — Campaign Creation Flow
**Route:** `/campaigns/new`  
**Purpose:** Create a new campaign through the Campaign Strategist

### Step 1: Campaign Brief Submission

**View: Campaign Brief Form**

**Subheading:** "Describe your campaign to [Strategist Name]"

**Form Fields:**

**Field 1: Campaign Name** (Required)
- Label: "What are we calling this campaign?"
- Input: Text field (50 char)
- Placeholder: "e.g., 'Spring Product Launch', 'Holiday Campaign'"
- Helper: "This will appear throughout the platform"
- Validation: Required, 3-50 chars

**Field 2: Campaign Timeline** (Required)
- Label: "When does this campaign run?"
- Input: Date range picker
  - Start date: Date field
  - End date: Date field
- Helper: "This affects how Moves are structured"
- Validation: Required, start < end, reasonable range (7 days to 1 year)

**Field 3: Primary Goal Category** (Required)
- Label: "What's the primary goal?"
- Input: Dropdown (5 options):
  - Awareness (reach and familiarity)
  - Consideration (engagement and education)
  - Conversion (direct sales or sign-ups)
  - Retention (customer loyalty and repeat purchase)
  - Launch (new product/service introduction)
- Helper: "This determines the campaign structure"
- Validation: Required

**Field 4: Goal Description** (Required)
- Label: "Describe your goal in detail"
- Input: Text area (300 char)
- Placeholder: "e.g., 'Launch our new SaaS product to 1,000 beta users within 60 days'"
- Helper: "The more specific, the better the Council planning"
- Validation: Required, min 50 chars

**Field 5: KPI Target** (Required)
- Label: "How will you measure success?"
- Input: Smart KPI builder based on goal category
  - **Awareness goal →** "Reach [X] people" or "Generate [X] impressions"
  - **Consideration goal →** "Generate [X] qualified leads" or "Achieve [X]% engagement rate"
  - **Conversion goal →** "Generate [X] conversions" or "Achieve ₹[X] revenue"
  - **Retention goal →** "Achieve [X]% retention rate" or "Generate [X] repeat purchases"
  - **Launch goal →** "Onboard [X] beta users" or "Achieve [X]% awareness"
- Validation: Required, numeric value

**Field 6: Target ICP** (Required)
- Label: "Who is this campaign for?"
- Input: Dropdown (lists all Foundation ICPs)
- Default: Primary ICP pre-selected
- Helper: "This shapes the messaging, channels, and creative approach"
- Validation: Required

**Field 7: Budget (Optional)**
- Label: "Monthly ad spend budget (optional)"
- Input: Number field (₹)
- Placeholder: "₹50,000"
- Helper: "If included, helps Media Buyer allocate across channels"
- Validation: Optional, numeric if provided

**Field 8: Campaign Brief Text** (Required)
- Label: "Tell the Council everything they need to know"
- Input: Rich text area (1,000 char limit)
- Placeholder: Start typing...
- Helper: "Key insights, constraints, what the Council should consider"
- Helper bullets:
  - "What's the market situation?"
  - "Who are we competing against?"
  - "What channels should we prioritize?"
  - "Any constraints or requirements?"
  - "Any previous attempts at this goal?"
- Validation: Required, min 100 chars

**Submit Button:** "Send to Council"
- Validation: All required fields must be filled
- On submit: Strategist begins evaluation

---

### Step 2: Strategist Evaluation (Synchronous)

**View: Campaign Evaluation (Blocking Screen)**

Shows a loading state while Strategist evaluates the brief against 5 criteria (takes 15-30 seconds).

**Loading Screen:**
- Heading: "[Strategist Name] is reviewing your brief"
- Text: "Evaluating against strategic clarity, market fit, channel strategy, timeline realism, and goal achievability..."
- Spinner animation
- Office illustration in background (passive mode)
- Countdown timer: "This typically takes 20-30 seconds"

**After Evaluation Completes:**

Screen transitions to evaluation results with Strategist's assessment.

---

### Step 3: Strategist Evaluation Results

**View: Campaign Evaluation Results**

**Strategist Message** (in their configured voice):

"I've reviewed your brief. Here's my assessment:"

**Evaluation Matrix** (Visual Table):

| Criterion | Status | Comment |
|---|---|---|
| Strategic Clarity | ✅ Strong | "Your goal is specific and measurable. The Council will work with clear parameters." |
| Market Fit | ✅ Strong | "This aligns with your Foundation. We're speaking to the right customer about the right problem." |
| Channel Strategy | ⚠️ Consider | "You didn't specify channels. That's okay — the Council will recommend. But if you have channel preferences, now's the time to mention them." |
| Timeline | ✅ Realistic | "90 days is solid. Gives enough time to build awareness and drive consideration." |
| Goal Achievability | ✅ Likely | "Based on your past performance and market benchmarks, this is achievable. Execution matters." |

**Overall Assessment:**
- Status: ✅ "Ready for Council Planning" or ⚠️ "Proceed with caution" or ❌ "Not recommended"
- Strategist note (2-3 sentences) explaining the overall recommendation
- If issues: Specific suggestions for revising the brief

**Actions:**
- If "Ready": "Convene Council" button (primary)
- If "Proceed with caution": "Convene Council Anyway" button (secondary) + "Edit Brief" button
- If "Not recommended": "Edit Brief" button (primary) + "Convene Council Anyway" button (secondary, with warning)

---

### Step 4: Council Planning Session (Asynchronous, Visible)

**View: Council Planning Session (Real-Time)**

**Heading:** "[Campaign Name] — Council Planning Session"

**Session Type Indicator:**
- Based on campaign complexity: "Tactical Council" or "Strategic Council" or "War Room"
- Explanation: "X agents convening. Estimated duration: X minutes."

**Agents Assembling Animation:**
- Optional: Office animation showing agents walking to conference room
- Text: "Assembling the Council..." with list of agent names appearing
- Or: Static text list of agents: "David Ogilvy, Neil Patel, Gary Vaynerchuk, [+8 more]"

**Council Session Breakdown:**

The session is divided into phases, visible in real-time:

**Phase 1: Initial Response** (Agents responding to brief)
- Timeline: 0-5 minutes
- Visual: Text streaming in, each agent's position appearing in realtime
- What's happening: Each agent reads the brief and produces an initial perspective
- User sees: Agent names + first lines of their responses appearing one by one

**Phase 2: Debate** (Agents discussing and countering)
- Timeline: 5-15 minutes
- Visual: Agents responding to each other, positions evolving
- User sees: Threaded conversation view showing agent disagreements/agreements

**Phase 3: Synthesis** (Strategist synthesizing into a unified plan)
- Timeline: 15-20 minutes
- Visual: Strategist typing/thinking animation
- User sees: Summary forming, final campaign plan emerging

**Final Output: Campaign Plan**

The completed campaign appears on the screen with:
- **Campaign Strategy Narrative** (300-500 words)
- **Recommended Move Structure** (Ordered list of moves)
- **Key Tactics by Channel**
- **Success Metrics & Checkpoints**
- **Risk Assessment**
- **Next Steps**

**Actions on Completed Plan:**
- "Approve & Launch" button (blue, primary)
- "Request Revisions" button (secondary, opens Muse chat with Strategist)
- "Edit Manually" button (secondary)

---

## 4.3 — Campaign Dashboard (Active Campaign)
**Route:** `/campaigns/[campaign-id]`  
**Purpose:** View and manage active campaign

### Three-Column Layout:

**Left Column: Campaign Overview** (20%)
- Campaign name
- Status: Active (green badge)
- Timeline progress bar
- Key dates (start, end)
- Primary goal statement
- KPI target
- Target ICP
- Quick stats:
  - Days remaining
  - Tasks completed
  - Tasks pending
- Quick actions:
  - Pause campaign
  - View/Edit brief
  - View Council session
  - Replanning history (if replanned)

**Center Column: Moves & Tasks** (60%)
- **Move 1: Awareness**
  - Status: In Progress (blue badge)
  - Completion: 40% (progress bar)
  - Dates: May 1-15
  - Tasks (expandable/collapsible list):
    - Task 1: "Develop awareness messaging" — Status: Completed ✅
    - Task 2: "Create 10 social posts" — Status: Pending approval ⏳
    - Task 3: "Launch awareness ads" — Status: Not started ⭕
    - Task 4: "Generate landing page content" — Status: Completed ✅
  - Move summary: One-line strategic intent
  - [Show full Move details] link
  
- **Move 2: Consideration**
  - Status: Scheduled (gray badge)
  - Completion: 0%
  - Dates: May 16-30
  - Tasks visible on expansion
  
- **Move 3: Conversion**
  - Status: Scheduled
  - Completion: 0%
  - Dates: May 31-Jun 15

**Right Column: Performance & Intelligence** (20%)
- **Campaign Performance** (if live)
  - Metric 1: Current value vs target
  - Metric 2: Trend (up arrow, down arrow, stable)
  - Metric 3: Confidence level in projection
  - "View full analytics" link
  
- **Recent Alerts**
  - Alert 1: Status/issue
  - Alert 2: Opportunity
  
- **Competitive Intel** (if relevant)
  - Competitor moves that affect this campaign
  - Actionable recommendation

---

## 4.4 — Move Details View
**Route:** `/campaigns/[campaign-id]/moves/[move-id]`  
**Purpose:** Deep dive into a specific Move

### What the User Sees

**Header:**
- Campaign name | Move name (e.g., "Spring Launch | Awareness Move")
- Move status badge
- Move timeline progress

**Move Overview Section:**
- **Strategic Intent:** Why we're running this Move, what it accomplishes
- **Completion Criteria:** What success looks like
- **Assigned Agents:** Which Council members lead this Move

**Tasks List** (Detailed):

Each task shows:
- Task name
- Status badge: Not started / In progress / Pending approval / Completed
- Due date
- Assigned to agent (if assigned)
- Description (1-2 lines)
- Quick actions: View details / Edit / Approve / Complete / Delete

**Expandable Task Details:**
- Full description
- Acceptance criteria
- Assigned agent and rationale
- Previous revisions (if edited)
- Comments thread
- Related content/assets

**Content Pre-Generated:**

For content tasks (copy, social posts, ads, etc.):
- Status: Pending approval / Approved / Live
- Content preview (truncated)
- Performance data (if live)
- "View full content" button
- "Generate alternative" button
- "Approve" button (if pending)

**Move Performance** (if Move is live):
- Primary metric progress
- Trend
- Comparison to baseline
- Recommendation for adjustment

**Move Repla nning** (if triggered):
- Alert: "This Move was replanned on [date]"
- "View what changed" link

---

## 4.5 — Campaign Analytics View
**Route:** `/campaigns/[campaign-id]/analytics`  
**Purpose:** Detailed performance analysis

### What the User Sees

**Header:**
- Campaign name
- KPI target vs actual (e.g., "52/50 leads generated")
- Overall campaign status: On track / Below projection / Above projection
- Time remaining

**Performance Timeline Chart:**
- X-axis: Time (days since launch)
- Y-axis: KPI metric
- Line graph showing: Actual performance, Projection at time of planning, Updated projection
- Annotations for: Move transitions, major changes, competitive events

**Move-by-Move Breakdown:**

Table showing each Move with:
- Move name
- Metric for that Move
- Actual vs target
- Status badge
- Variance explanation (if significant)

**Channel Breakdown** (if multi-channel):
- Table showing each channel
- Performance metric per channel
- Budget spent per channel
- ROI per channel (if available)
- Recommendation for budget reallocation

**Competitive Context:**
- What competitors did during this period (if detected)
- How did those actions affect campaign performance
- Did we need to replan? Why/why not?

**Lessons & Recommendations:**
- Key learnings from this campaign
- Recommendations for future campaigns
- Ripples created for the PRL (transparency on what the system learned)

---

---

# SECTION 5: MUSE CONVERSATION INTERFACE

## 5.1 — Muse Chat View
**Route:** `/muse` or `/muse/[conversation-id]`  
**Purpose:** Conversational AI interface with spatial awareness

### Layout

**Three-Column Layout:**

**Left Column: Conversation List** (20%)
- "Muse Conversations" heading
- Search field: "Search past conversations"
- Conversations list (reverse chronological):
  - Each conversation shows:
    - Title (auto-generated or user-named)
    - Last message preview (truncated)
    - Timestamp (e.g., "2 hours ago", "Yesterday")
    - Pin icon (for favorites)
  - Hover actions: Archive, Delete, Rename
- Conversations organized by folder:
  - Recent (last 7 days)
  - Older (older than 7 days, collapsible)
- [New Conversation] button

**Center Column: Active Conversation** (60%)
- **Header:**
  - Conversation title (e.g., "Spring Campaign Strategy")
  - Timestamp (e.g., "Started yesterday at 2:30 PM")
  - Conversation info dropdown: Mark as favorite, Rename, Archive
  
- **Messages Thread** (Scrollable):
  - User messages (right-aligned, light background)
  - Assistant messages (left-aligned, darker background)
  - Message timestamps
  - "Thinking..." indicator when waiting for response
  - Message actions on hover: Copy, React, Delete (user messages only)
  
- **Spatial Context Indicator** (Small widget):
  - Shows current context if in-product: "In Campaign: Spring Campaign | Move: Awareness"
  - Or blank if in standalone Muse view
  - "Update context" button
  
- **Input Area** (Bottom, fixed):
  - Text field with placeholder: "Ask [Strategist Name] anything about your marketing"
  - Send button (arrow icon, blue when text present)
  - Attachment button: [ attachment icon ] (for images, screenshots, documents)
  - Voice input button (microphone icon, optional)
  - Keyboard shortcut hint: "Cmd+Enter to send"

**Right Column: Context Sidebar** (20%)
- **Current Context** (Header)
  - If in-product context: Campaign name, Move name, Task name
  - If standalone: None (can set)
  
- **Relevant Information**:
  - If in campaign: Campaign goal, ICP, timeline, current metric
  - If viewing task: Task description, due date, assigned agent
  - If in content: Content type, brand voice, target audience
  
- **Recent Related Items**:
  - List of recent campaigns, tasks, content
  - Clickable to update context
  
- **Helpful Quick Commands**:
  - Buttons for common requests:
    - "Generate content for this task"
    - "Analyze campaign performance"
    - "Suggest next steps"
    - "Review this brief"

---

## 5.2 — Muse Routing & Response Types

### When User Sends a Message:

**1. Routing Decision** (Happens silently, <1 second)
The system classifies the message and routes it:

**Route 1: Direct Strategist Response**
- Questions about strategy, performance, recommendations
- Example: "Is the campaign on track?"
- Example: "Should we pivot channels?"
- Response: Flash-Lite Reasoning call to Strategist
- Latency: 5-15 seconds
- Response includes: Analysis, recommendation, links to relevant data

**Route 2: Content Generation**
- Requests to create/write content
- Example: "Write social copy for the awareness phase"
- Example: "Generate 5 email headlines"
- Response: Routed to appropriate avatar (Ogilvy for copy, Vaynerchuk for social, etc.)
- Latency: 10-20 seconds
- Response includes: Generated content, voice explanation, alternatives available

**Route 3: Mini-Council**
- Questions requiring multiple expert perspectives
- Example: "Should we use LinkedIn or Facebook for this ICP?"
- Example: "How do we position against [Competitor]?"
- Response: 2-3 relevant avatars weigh in, Strategist synthesizes
- Latency: 20-40 seconds
- Response includes: Each perspective, synthesis, recommendation

**Route 4: Analytics Director**
- Questions about data, metrics, performance
- Example: "Why is our CTR dropping?"
- Example: "Is this A/B test result significant?"
- Response: Flash-Lite Normal call to Analytics Director
- Latency: 5-15 seconds
- Response includes: Data analysis, interpretation, implications

**Route 5: Muse Pattern Analysis + Auto-Response**
- Small clarifications, FAQs, navigation
- Example: "How do I create a new campaign?"
- Example: "What's the difference between these two moves?"
- Response: Auto-generated from knowledge base + user pattern learning
- Latency: <2 seconds
- Response includes: Quick answer, links to docs if needed

### Spatial Context Injection

When Muse receives a message, it assembles a 7-layer context stack BEFORE routing:

**Layer 1: Current Screen Context** (Where is the user right now?)
- Campaign name, Move name, Task name, Campaign goal, ICP, timeline

**Layer 2: Active Work Context** (What's happening?)
- Active campaigns, pending tasks, content awaiting approval, current metrics

**Layer 3: Temporal Context** (When is everything happening?)
- Today's date, days remaining in campaigns, upcoming milestones, task due dates

**Layer 4: Performance Context** (How is it going?)
- Current metric vs target, trend, confidence level, recent performance changes

**Layer 5: Intelligence Context** (What's the competitive landscape?)
- Recent competitive alerts, market changes, opportunities detected

**Layer 6: Foundation Context** (Who is the business?)
- Cached Foundation JSON: positioning, ICP, competitors, brand voice, goals

**Layer 7: Pattern Context** (What does this user care about?)
- User preference ripples, recurring topics, working style, knowledge gaps

**Example Response Assembly:**

User message: "What should we focus on this week?"
User is in: Campaign: Spring Launch | Move: Consideration

Muse assembles:
- Layer 1: "You're in the Consideration Move of Spring Launch, which runs May 16-30"
- Layer 2: "You have 3 tasks pending approval, 2 tasks due today"
- Layer 3: "You have 10 days remaining in this Move"
- Layer 4: "Consideration performance is tracking 85% of projection"
- Layer 5: "Competitor XYZ launched a comparison guide yesterday"
- Layer 6: "Your ICP is [ICP Name], who cares about [primary values]"
- Layer 7: "You've asked similar questions 3 times this week, usually when performance dips"

Strategist response (informed by all layers):
"You have momentum but performance is slightly below projection. I'd focus on: (1) Approving the 3 pending content pieces — they're on-brand and addressing the competitor's positioning, and (2) Accelerating the Consideration education task — given [ICP] values education highly, this is likely to close the performance gap. Would you like me to help synthesize an approval decision on the content?"

---

# [CONTINUED IN NEXT PART DUE TO LENGTH]

---

# Sections Remaining (See Continuation):

- **Section 6:** Competitive Intelligence Dashboard
- **Section 7:** Daily Wins & Nudges System
- **Section 8:** Council & Debate Viewer
- **Section 9:** Content Engine & Asset Management
- **Section 10:** Settings & Preferences
- **Section 11:** Administrative & Advanced Views

This comprehensive specification covers EVERY page with extreme detail on:
- Layout and positioning
- Form fields, validations, and auto-save behavior
- Interactive states and animations
- Data models and storage
- Edge cases and error handling
- Connection to other pages and systems
- AI agent behavior and routing
- Technical implementation notes

---

**END OF PART 1**

*Continuation document recommended due to length. This Part covers ~11,000 words and covers Sections 1-5 (Pre-product, Foundation, Dashboard, Campaigns, Muse). Sections 6-11 require separate document.*

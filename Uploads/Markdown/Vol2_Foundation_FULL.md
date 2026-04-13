**RAPTORFLOW**

MASTER DOCUMENT SERIES

**VOLUME TWO**

**The Foundation — All 21 Screens in Complete Detail**

_Every screen, every AI behaviour, every edge case, every data field, every connection to every agent_

CONFIDENTIAL — INTERNAL BLUEPRINT

# **Opening: The Foundation Is Not Onboarding**

Most software products have onboarding. Onboarding is a tax — a necessary cost users pay before they can access what they came for. Good onboarding minimises this tax through skip buttons, sensible defaults, and aggressive brevity. The implicit message of good onboarding is: we know your time is valuable, so we will ask for as little as possible before letting you in.

The Foundation is the opposite design philosophy. The Foundation asks a lot of the user — twenty-one screens worth of thinking, articulation, and strategic clarity. It does this not despite valuing the user's time but because of it. Every minute invested in the Foundation returns compound interest across every subsequent interaction with the system. The Foundation data is injected into every agent context for every campaign, every content generation, every Council debate, every Daily Wins briefing, every Muse conversation, every piece of competitive intelligence, for as long as the user is on the platform. It is the bedrock on which everything else is built.

The design imperative for the Foundation, therefore, is not to minimise its length but to maximise its value per screen. Every screen must give back more than it takes. The user who completes Screen 7 should understand something about their business that they did not understand after Screen 6. The user who finishes Screen 21 should have done more strategic thinking about their business than they have done in months, possibly ever. This is the standard every screen is held to.

This volume describes every one of the twenty-one Foundation screens in complete detail. For each screen, it covers: what the screen is trying to achieve and why it matters, exactly what the user sees and exactly what they are asked to do, what AI is running in the background and what it produces, what the data goes into and where it goes next, what happens when the user answers poorly or not at all, what edge cases the screen must handle gracefully, and how this screen connects to the screens before and after it.

# **Part One: Before the Screens — The Pre-Onboarding Architecture**

## **Chapter 1.1 — The Account Creation Flow**

Before the Foundation begins, the user has created an account. This happens through Clerk, which handles all authentication. The sign-up options are Google OAuth and email plus password. No other options at launch. The choice to offer Google OAuth is deliberate: it reduces friction at the critical moment when a user has arrived with genuine intent and should not be stopped by a complex registration process.

Immediately after authentication, the user is asked one question and one question only before the Foundation begins: what would you like to name your workspace? This name appears in two places — the URL slug of their workspace and, critically, the name on the office building in the visual Office feature. The prompt is careful: it says workspace or company name, not account name or username, because the name should feel like naming something real. The office will carry this name on its door. It should feel like that matters.

After naming the workspace, the user is shown a brief three-second transition: a loading animation of an empty office with the placeholder name on the door, accompanied by the message that they are about to build their marketing office. Then Screen 1 appears. There is no tutorial. There is no feature tour. There is no getting-started checklist. The Foundation starts immediately, because the Foundation is the product.

## **Chapter 1.2 — The Dual Scan System**

The moment the user submits Screen 1 — the URL screen — two processes begin simultaneously. They run in parallel and produce different types of output on different timelines. Understanding both processes completely is essential for understanding how every screen from Screen 2 onward works.

### **The Quick Scan**

The quick scan is synchronous and blocks the transition from Screen 1 to Screen 2 until it completes. Its purpose is to extract the minimum information required to pre-populate Screen 2 in a way that creates the first wow moment of the experience. It must complete in under ten seconds, and should typically complete in five to seven.

The quick scan uses a lightweight reqwest HTTP fetch — not a headless browser, just a simple GET request to the submitted URL. It extracts the page title, meta description, Open Graph tags, any structured data present, and the primary h1 tag. From these signals, it derives: the business name, the primary tagline or value proposition, the industry category, and a brief description of what the business does. These five pieces of information are what pre-populate Screen 2.

If the URL does not resolve — if the server is down, the URL is invalid, or the request times out — the quick scan returns a graceful failure state. Screen 2 appears without pre-population and with a note that the scan could not reach the website. The user fills in the fields manually. The experience degrades gracefully but never breaks.

If the URL resolves but the page has almost no text content — a site that is entirely JavaScript-rendered with no server-side content — the quick scan returns whatever little it could extract plus a note that the site may need additional time to fully analyse. The deep scan will be more important in this case.

### **The Deep Scan**

The deep scan is asynchronous and runs entirely in the background from the moment the URL is submitted. The user never waits for it. It begins its work while the user is progressing through Screens 2, 3, and 4, and its results begin arriving — via WebSocket events that the frontend handles — as the user reaches the screens those results are relevant to.

The deep scan uses chromiumoxide, RaptorFlow's custom headless Chrome implementation, to fully render the website including JavaScript-heavy content. It crawls up to fifty pages following internal links from the homepage, prioritising pages likely to contain strategic information: about pages, product or service pages, pricing pages, case study or testimonial pages, blog posts, and team pages.

For each crawled page, it extracts the full text content, headings structure, any schema markup, pricing signals, testimonial text, team member descriptions, and any claims made about the product or service. The combined extraction from up to fifty pages is then processed by a Flash-Lite inference call that produces structured data in six categories: product and service descriptions, target audience signals from the messaging, brand voice characteristics, competitive positioning language, pricing model and structure, and social proof indicators including testimonial count, client logos, and case study depth.

This structured data is stored in the onboarding state database record for this org and then used to pre-populate fields as the user reaches screens that can benefit from it. The timing is calibrated: by the time most users reach Screen 7 or 8, the deep scan has typically completed and its outputs are available. The user experiences this as suggestions appearing as if by magic — which is essentially what is happening.

### **The Competitor Deep Scan**

When the user adds competitors on Screen 8, a separate competitor deep scan fires for each competitor URL submitted. This is identical in structure to the user's own deep scan but focused on competitor intelligence: positioning language, pricing, product features, audience targeting signals, and any publicly visible performance indicators. Competitor deep scan results feed the Intel pipeline immediately — from the moment they are submitted on Screen 8, those competitors are being tracked by the competitive monitoring system.

# **Part Two: The Twenty-One Foundation Screens**

## **Screen 1 — The URL**

**What This Screen Achieves**

Screen 1 achieves three things simultaneously. It collects the single most information-rich input available at the start of onboarding — a URL that can unlock everything else through scanning. It starts the quick scan and deep scan immediately, so work is happening while the user moves forward. And it creates the first impression of the product: a clean, uncluttered screen that communicates confidence and simplicity without demanding anything from the user before they understand what they are getting into.

**What the User Sees**

A full-screen view with a dark background — not black, but a deep charcoal that feels premium without feeling oppressive. Centred on the screen is the RaptorFlow wordmark at moderate size. Below it, a single line of text: 'What is your business website?' Below that, a single text input field with placeholder text that reads 'yourcompany.com' — not 'https://yourcompany.com', because the presence of the protocol prefix in a placeholder is an unnecessary detail that makes the field feel technical. A single button below the field reads 'Begin building your office'.

Nothing else is on this screen. No explanations of what will happen. No reassurances about data privacy. No indicators of how many screens follow. The simplicity communicates that the system does not need to oversell itself or apologise for asking. It knows what it is doing.

**What Happens When They Submit**

The URL input is validated before submission. The system checks that it is a valid URL structure and that it resolves with a 200 status code. If either check fails, an inline error message appears below the field explaining specifically what went wrong: either 'This does not appear to be a valid URL — try adding https://' or 'We could not reach this website — please check the address and try again.' The error is specific, not generic.

When a valid URL is submitted, the quick scan begins immediately. The button state changes to a loading indicator — not a generic spinner, but a subtle animation that suggests work happening rather than merely loading. The scan result is ready within five to seven seconds. The transition to Screen 2 happens automatically when the scan completes.

**Edge Cases**

If the user has no website, a small text link below the button reads 'I do not have a website yet'. Clicking this takes the user directly to Screen 2 in manual-entry mode — no pre-populated fields, just the empty form they will fill themselves. The deep scan does not run. Everything else proceeds normally.

If the URL submitted is a social media profile rather than a website — a Facebook page URL or an Instagram profile link — the system extracts what it can from the profile page but notes in the Screen 2 pre-population that the analysis is based on a social profile rather than a full website, which may mean less comprehensive results. The user is asked if they have a dedicated website URL.

If the URL submitted is a competitor's website rather than the user's own — which occasionally happens when users are confused or testing — this usually becomes apparent during the Screen 2 confirmation when the user sees the extracted information and realises it describes a different company. They can simply go back and re-enter.

## **Screen 2 — Identity Confirmation**

**What This Screen Achieves**

Screen 2 is the first wow moment. Its purpose is to demonstrate, within thirty seconds of the user submitting their URL, that the system already understands something about their business. The user who sees their company name, their tagline, and a description of what they do — all extracted accurately from their website without them typing a word — receives an immediate signal that this is different from any tool they have tried before. The system is already working.

The secondary purpose of Screen 2 is to collect the user's confirmation and corrections, turning the scanned data into verified data. The scan is not infallible. Websites are imperfect sources of information. The user knows their business better than any scan can. Screen 2 is the handoff from machine inference to human verification.

**What the User Sees**

The screen is divided into two halves with a subtle visual divide. The left half shows what the system found: a card presenting the extracted information with a heading that reads 'Here is what we found about your business'. Below the heading are five pieces of information laid out as field-label pairs: business name, primary description, industry category, business model, and the tagline or value proposition detected from the site. Each field has a confidence indicator — a subtle colour coding that shows whether the system is very confident, moderately confident, or uncertain about each piece of extracted information.

The right half contains the editable version of the same information. The fields are pre-populated with the extracted values but fully editable. The user adjusts anything that is wrong and leaves unchanged anything that is correct. A progress indicator at the top of the screen shows Screen 2 of 21 — the only time the screen number is prominent, because after this point the progress indicator moves to a smaller position and the screens focus entirely on content.

**The Confidence Indicators**

The confidence system is worth describing in detail because it shapes how the user interacts with the pre-populated data. Fields where the extraction is very confident — where the page title, meta description, and h1 tag all agree — appear with a green subtle background. The implicit message is: this is probably right, check it quickly and move on. Fields where signals are mixed or limited — where the industry was inferred from vocabulary rather than stated explicitly — appear with an amber tint. The implicit message is: this might be right, but look at it carefully. Fields where the system had to guess or where no relevant signal was found appear with a question mark icon. The implicit message is: fill this in yourself, we could not get it from the site.

This confidence system prevents the user from blindly accepting all pre-populated data without checking, while also allowing them to move quickly through fields where the system is clearly correct. It is a trust calibration mechanism.

**The Industry Category Field**

The industry category field deserves special attention because it drives several downstream decisions. The system uses a taxonomy of approximately eighty industry categories organised in a two-level hierarchy — broad categories like Retail, Professional Services, Food and Beverage, Technology, and Healthcare, each containing more specific subcategories. The scan attempts to place the business in the most specific applicable subcategory.

If the scan's industry inference is wrong — which happens most often for businesses at the intersection of categories — the user selects the correct category from a searchable dropdown. The selected industry category then shapes the suggestions that appear in later screens: ICP templates, competitor suggestions, keyword suggestions, and content territory suggestions are all calibrated to the selected industry.

**Edge Cases**

A business with multiple distinct product lines or service areas may present confusingly in the scan. The scan extracts what appears to be the primary offering. If the user's business is genuinely multi-faceted — a company that sells both software and provides consulting, for example — Screen 2 shows the primary extraction and offers an option to add additional business lines. The system notes that multiple distinct offerings may benefit from separate onboarding tracks and asks the user whether they want to focus on one area for this Foundation setup.

A business that is very early stage and has a website that is largely placeholder content — coming soon pages, placeholder text — will produce minimal useful scan results. The system presents what little it found, acknowledges the limitation, and asks the user to provide the information manually. This is handled gracefully with specific prompts rather than generic empty fields.

## **Screen 3 — Business Stage and Team**

**What This Screen Achieves**

The strategic advice appropriate for a pre-revenue startup building its first audience is fundamentally different from the advice appropriate for a ten-crore business defending market share. The tone is different, the channels are different, the risk tolerance is different, the timeline for results is different. Screen 3 calibrates the entire system to the business's actual position in its growth journey, so that every recommendation from every agent reflects the reality of where this business is rather than a generic ideal.

**What the User Sees**

Screen 3 presents five stage cards arranged horizontally, each sized to be easily readable and tappable on mobile. The cards are: Pre-revenue — building and not yet selling; Early revenue — annual sales below ten lakh rupees; Growing — annual sales between ten lakh and one crore rupees; Scaling — annual sales between one crore and ten crore rupees; and Established — annual sales above ten crore rupees. Each card has a brief second-line description that helps users self-identify accurately rather than aspirationally.

Below the stage cards, the same card-selection pattern repeats for marketing team size: Solo — handling everything myself; Small team — one to two people handling marketing; Dedicated team — three to five people; and Agency or professional team — more than five people or external agency. This selection determines the complexity level of recommended campaigns and the amount of assumed execution capacity in Move planning.

**Why These Ranges**

The revenue ranges are chosen to reflect genuine strategic inflection points in the Indian SMB journey rather than arbitrary round numbers. Below ten lakh rupees annually, the business is typically in survival mode — the marketing challenge is primarily acquisition at low cost. Between ten lakh and one crore, the business has validated its offering and the marketing challenge shifts to scaling what is working. Between one crore and ten crore, the business is typically managing multiple channels and the challenge becomes coordination and positioning against emerging competitors. Above ten crore, brand management and competitive defence become significant concerns alongside growth.

**How This Data Affects Everything Downstream**

The stage and team size selections affect the system in ways that are not always visible to the user but are constant throughout their experience. A pre-revenue business gets campaign recommendations that emphasise organic reach, community building, and content marketing over paid media — because paid media optimisation requires existing conversion data to work effectively. A scaling business gets recommendations that assume more aggressive paid channel investment is appropriate and that the returns are measurable. A solo operator gets Move structures with five to seven tasks per day maximum — the system does not plan for execution capacity that does not exist. A dedicated team gets Moves that can involve more complex multi-channel coordination.

## **Screen 4 — What You Actually Sell**

**What This Screen Achieves**

Screen 4 collects the most operationally important information in the Foundation: exactly what the business offers, what it does for customers, and what it costs. This is the information that every agent uses as the anchor for every content generation, every campaign strategy, every Council debate, every competitive analysis. Without accurate, specific product and service data, the agents are navigating without a map.

The screen is designed around a tension: most business owners, when asked to describe their products or services, describe them from the inside — in terms of features, specifications, and operational details. What the agents need is an outside view — what the product does in the customer's life, what problem it solves, what changes for the customer after they buy. Screen 4 is structured to elicit the outside view without making the user feel like they are being corrected.

**What the User Sees**

The screen shows a structured card for each product or service, with a plus button to add more. If the deep scan has found product information on the website, the first one to three cards are pre-populated with extracted data and marked as suggestions to confirm. Unpopulated cards show the empty field structure.

Each product or service card contains four fields. The first field is the product or service name — what the business calls it. The second field is a one-sentence description of what it is — what category it belongs to. The third field is a one-sentence description of what it does for the customer — the specific improvement in the customer's situation that results from buying this product. The fourth field is the price point or pricing model — whether it is a fixed price, a subscription, a project-based fee, or a variable-cost service.

**The Outside View Prompt**

The third field — what it does for the customer — is the most important and the hardest for most users to complete well. The field's placeholder text is carefully written to guide without instructing: 'After buying this, the customer can...' or 'This solves the problem of...' These are not mandatory prompts that the user must follow word for word. They are framing devices that push the user toward consequence-focused thinking rather than feature-focused thinking.

When the user completes this field, a Flash-Lite call runs in the background to assess whether the answer is inside-view or outside-view. If the answer describes features rather than consequences — 'includes email marketing, social media scheduling, and analytics dashboard' — the system gently offers an alternative: 'You described the features of your product. Would you like help translating this into customer language? For example: Customers who use this stop spending hours switching between tools and get their marketing done in one place.' The user can accept the suggestion, edit it, or keep their original. The system never forces the outside view. It offers it.

**The Pricing Field**

The pricing field is structured rather than free text. A dropdown first asks for the pricing model: fixed one-time price, monthly subscription, annual subscription, project-based quote, hourly rate, or variable cost. After the model is selected, appropriate number fields appear. For a monthly subscription, one field for the price. For a tiered subscription, fields for each tier. For project-based pricing, a range field showing minimum and maximum typical project size.

This structure serves multiple purposes. It makes the pricing data machine-readable rather than requiring natural language parsing. It enables the Media Buyer agent to make accurate budget allocation recommendations. It enables the Analytics Director to compute meaningful ROI calculations. And it forces the user to articulate their pricing in a consistent structure rather than the vague 'pricing varies' that is common when business owners are uncomfortable with the question.

**Adding Multiple Products**

The plus button for adding additional products is present but not prominent. The system suggests limiting the Foundation to the three to five most important offerings rather than attempting to catalogue every product. If the user adds more than five products, the system notes that comprehensive Foundation setup for very large product catalogues can become unwieldy and suggests identifying the primary offering for this Foundation while noting that additional products can be documented in separate contexts within the platform.

**Deep Scan Connection**

If the deep scan has found pricing information on the website — a pricing page, pricing mentioned in product descriptions, any price signals — that information appears as pre-populated suggestions in the pricing fields with a note that this was found on the website and should be verified for accuracy. This is particularly valuable for businesses with complex tiered pricing that would be tedious to enter manually.

## **Screen 5 — The Problem You Solve**

**What This Screen Achieves**

Screen 5 is the screen that most surprises users, because it asks a question that seems obvious but turns out to be genuinely difficult to answer well. The question is: what problem does your customer have before they find you? Not the problem as the business owner sees it. Not the problem as a marketer would frame it. The actual, lived, frustrating problem as the customer would describe it to a friend.

This information is the foundation of all problem-aware marketing — the category of marketing that speaks directly to a customer's recognised pain rather than trying to create awareness of a problem they have not identified. It is the raw material for ad copy that makes people think 'this is exactly my situation'. It is the basis for ICP research that goes beyond demographics into psychology. It is how agents understand not just who the customer is but what drives them.

**What the User Sees**

Three guided prompts, each with a text area beneath it, arranged vertically on the screen. The prompts are written conversationally, as if a strategist is asking the questions in a meeting. The first prompt: 'Before your customer found you, what was their situation? What were they dealing with every day?' The second prompt: 'What specific frustration did this situation create? What made it genuinely annoying or costly or stressful?' The third prompt: 'What had they tried before that did not work, and why did it fall short?'

The three-prompt structure is deliberate. The first question gets at the objective situation — the facts of what the customer was dealing with. The second gets at the emotional dimension — the felt quality of the problem, which is what emotionally resonant copy needs to reflect. The third gets at the competitive dimension — what alternatives exist and why they fail, which is exactly the differentiation information that agents need to position this business against its competitors.

**The AI Synthesis**

After the user completes all three fields, a Flash inference call runs and produces a synthesis of the problem articulation — a single, clean, strategically clear statement of the problem as a skilled marketer would frame it. This synthesis appears below the three text areas as a suggested distillation: 'Here is how your Campaign Strategist would describe the problem your business solves...'

The synthesis is not a rewrite of what the user wrote. It extracts the core insight from their three answers and expresses it in the language that is most useful for strategic and creative work: specific enough to feel true, broad enough to apply to a market segment rather than just a single customer, emotionally grounded rather than purely functional.

The user can: accept the synthesis and use it as the Foundation's problem statement, edit the synthesis before accepting it, or reject it and use their own words. Whatever they end up with becomes the Foundation's problem articulation — the anchor for ICP development in Screens 6 and 7 and the strategic foundation for all problem-aware marketing the system produces.

**Why the Third Question Matters Most**

The third question — what had they tried before that did not work — is the question that most business owners have never formally asked themselves, and the one that produces the most strategically valuable answers. The answer to this question defines the competitive landscape in terms of customer experience rather than market category. It tells the agents not just who the competitors are but why customers left them, which is the most honest and actionable form of competitive intelligence available.

A business that discovers its customers tried an expensive agency and felt they got generic output that required constant correction has learned something specific: the differentiation language should emphasise specificity, customisation, and the value of a system that learns over time. A business that discovers its customers tried DIY approaches and felt overwhelmed has learned something different: the differentiation language should emphasise the support, the guidance, and the reduction of cognitive load. These are different messages for different situations, and they would not emerge from any other type of data collection.

**Edge Cases**

Some businesses operate in markets where the customer does not strongly recognise the problem before encountering the solution — where awareness of the problem is part of what the marketing must create. In these cases, the third prompt is modified: 'If your customer would not have described themselves as having this problem before they found you, what would they have said they were struggling with instead?' This reframe allows the Foundation to capture the pre-solution framing without requiring the user to force-fit their situation into a problem-aware framework.

## **Screen 6 — The Primary Ideal Customer Profile**

**What This Screen Achieves**

The ICP screen is the single most important screen in the Foundation after the positioning screen. It is the screen that transforms the system from a capable AI tool into a specific marketing intelligence system for this business. Every agent in the office uses the ICP data constantly — Ogilvy uses it to calibrate the language and emotional register of copy, Patel uses it to determine which platform behaviour patterns apply, Godin uses it to identify the tribe dynamics, Cialdini uses it to select which influence principles are most applicable, and so on across all twelve Council avatars.

The ICP screen is designed to collect not just demographic information but the psychographic, behavioural, and linguistic information that distinguishes genuinely useful customer profiles from the demographic personas that most businesses create and then never reference.

**What the User Sees — B2B Mode**

For a business that identified as primarily B2B on Screen 2, the ICP screen presents fields organised around the professional identity of the buyer. The first section is role identity: the buyer's job title or function, the type of company they work for, the size of that company, and the industry it operates in. These are presented as structured inputs with searchable dropdowns for company size and industry.

The second section is goals and pressures: what is this person trying to achieve in their role this quarter, what pressure are they under from their organisation, and what does success look like for them professionally in the context of the problem this business solves? These are free-text fields because the answers are too varied to structure.

The third section is decision dynamics: does this person make the purchasing decision themselves, do they need to get approval, who else is involved in the decision, and what does that approver care about? This section is particularly important for B2B sales because the buying process often involves multiple stakeholders with different concerns, and the marketing must speak to all of them at different stages.

The fourth section is language and self-perception: how would this person describe their problem in their own words — not in the business owner's words or marketing language, but the actual phrases they might use in a conversation? What words do they use to describe success? What industry-specific vocabulary are they fluent in and might respond to in copy?

**What the User Sees — B2C Mode**

For a business that identified as primarily B2C, the ICP screen presents a different field structure oriented around individual life context rather than professional role. The first section is life situation: age range, life stage, income band, location type, and household structure. These are structured selections.

The second section is aspirations and identity: what does this person want to be or become, what does owning or using this product say about who they are, and what values do they hold that this brand should reflect or at minimum not conflict with? These are deep psychographic questions that most marketing tools never ask and most users have never formally articulated.

The third section is behaviour and consumption: where does this person discover new products, which social platforms are they actually active on versus just present on, what media do they consume, and who do they take recommendations from? The distinction between platforms they are active on versus merely present is important — a brand's audience being technically present on LinkedIn does not mean LinkedIn is the right channel if they never actually engage there.

The fourth section is identical to the B2B version: the actual language the customer uses to describe their situation, their problem, and their aspirations.

**The Persona Naming**

After completing all sections, the user names this ICP persona. The name prompt reads: 'Give this customer a name — not a real name, but a description that captures who they are. For example: The Scaling D2C Founder, The Overwhelmed Clinic Owner, or The Aspiring Home Baker.' The suggested format is 'The \[Adjective\] \[Role or Identity\]' but any name the user finds memorable and accurate works.

The persona name appears throughout the platform whenever this ICP is referenced. In Muse conversations, the Strategist might say 'thinking about what The Scaling D2C Founder cares about...' In Council debates, agents might refer to 'the primary persona's typical objection at this stage...' The naming makes the ICP feel like a real entity rather than an abstract segment, which keeps the reference grounded when agents discuss it.

**The Deep Scan Contribution**

If the deep scan found testimonials, case study descriptions, or 'who this is for' sections on the website, those appear as suggested additions to the ICP fields. A testimonial from a manufacturing company's operations director becomes a suggested answer to the 'role identity' field. The language a customer used in a testimonial to describe their problem populates the language section. This contribution from the deep scan is one of the most practically valuable uses of the scanning infrastructure — real customer voice is almost always more accurate and more useful than the business owner's reconstruction of customer voice.

**Edge Cases**

When the business serves customers that span multiple distinct profiles — a software company that sells to both HR managers and finance directors, or a restaurant that serves both corporate lunch customers and family dinner customers — Screen 6 focuses on the primary ICP with the explicit note that secondary ICPs can be added on Screen 7. The primary ICP is the one who represents the highest proportion of revenue or the best growth opportunity, as the user judges.

When the business is genuinely pre-customer — a startup that has not yet served its first paying customer — the ICP fields are completed based on the target customer as the founder imagines them. The system notes that ICP data from hypothetical customers is less reliable than data from actual customer experience and suggests updating the Foundation as real customer relationships develop. The Foundation version history tracks this evolution.

## **Screen 7 — Secondary ICPs**

**What This Screen Achieves**

Not every business serves a single type of customer. A law firm might serve both individual clients and corporate clients. A fitness app might serve both beginners and serious athletes. A marketing platform might serve both solopreneurs and teams. Screen 7 captures secondary ICPs so that the agents can target communications appropriately when campaigns are designed for specific audience segments rather than the broad customer base.

**What the User Sees**

Screen 7 begins with a message from the Campaign Strategist — the first time the Strategist appears as a distinct voice in the onboarding: 'Now that I understand your primary customer, are there other types of customers worth building campaigns for? Many businesses serve more than one audience, and I can create much better campaigns when I know about all of them.'

Below this message, a card shows a summary of the primary ICP from Screen 6, and a plus button offers the option to add a secondary ICP. Adding a secondary ICP opens a version of the same field structure from Screen 6 but shorter — it focuses on what is different about this audience rather than repeating all the fields. The fields are: how is this person different from the primary ICP, what is their primary goal, and what different message would resonate with them versus the primary persona.

A skip button is clearly visible and not hidden or de-emphasised. The system genuinely means it when it says this screen is optional. Many businesses have one primary ICP that accounts for the vast majority of their value, and adding secondary ICPs with insufficient data would create noise rather than signal in the agent context.

**Maximum ICPs**

The system accepts up to four ICPs in total: one primary and up to three secondary. Beyond four, the Foundation context becomes complex enough that agents have difficulty maintaining consistent ICP-appropriate messaging without explicit ICP targeting on each campaign. More than four ICPs is a signal that the business has not yet found its focus, and the Campaign Strategist — through Muse — will gently surface this observation once the Foundation is complete.

## **Screen 8 — The Competitive Landscape**

**What This Screen Achieves**

Screen 8 introduces the competitive intelligence dimension of the Foundation and simultaneously activates the intelligence pipeline for the first time. Every competitor URL submitted on this screen becomes a monitored entity — from this moment forward, the intelligence system begins tracking their website, social media, ad library, and SEO footprint. The quality and specificity of the competitor data entered here directly determines the quality of the competitive intelligence the system will produce for this business.

**What the User Sees**

Three input fields for competitor URLs, each with a scan preview that activates as the URL is entered. As the user types or pastes a competitor URL, the quick scan runs and returns basic information within five to seven seconds: the competitor's business name, their primary tagline or positioning statement, and a one-sentence description of what they offer. This preview appears directly below the URL field before the user moves to the next one.

The preview serves two purposes. It confirms to the user that the URL is correct and pointing to the right company. And it gives the user an immediate comparison between the competitor's positioning language and what they entered for themselves in earlier screens — a first pass at understanding where they are positioned relative to the competitive set.

Below the three competitor URL fields is a question that asks about indirect competitors — businesses that solve the same problem in a different way. The example given is specific and helps users understand the distinction: 'If you sell project management software, a spreadsheet template might be an indirect competitor because it solves the same problem even though it is not in the same product category.' This question frequently surfaces competitors that the user had not thought to name explicitly but that are genuinely relevant to the competitive analysis.

**The Competitor Deep Scans**

For each competitor URL submitted, a deep scan equivalent to the user's own deep scan runs asynchronously. The competitor deep scan crawls the competitor's website looking specifically for: positioning language and differentiation claims, pricing structure and model, product or service features, target audience signals in messaging, social proof elements, and content strategy indicators. All of this data is stored in the competitor intelligence database and forms the baseline for the ongoing competitive monitoring.

The competitor deep scan also captures the current state of the competitor's website content — this becomes the T-zero snapshot against which all future changes are measured in the website change detection monitoring. From this moment forward, when the monitoring system detects that the competitor changed their pricing page or updated their homepage messaging, it is comparing against this initial scan.

**What Happens If the User Cannot Name Competitors**

Some users — particularly those in very new markets, those who have never formally analysed their competitive landscape, or those who have genuinely novel offerings — cannot readily name competitors. The system handles this with a combination of AI suggestion and a skip option.

The AI suggestion draws on the industry category from Screen 2, the product description from Screen 4, and the ICP from Screen 6 to generate a list of likely competitors: 'Based on what you have told us, you might compete with companies like these. Select any that are genuinely relevant.' This suggestion list is not definitive — it is a starting point for a user who needs prompting. The user selects relevant competitors, modifies the list, or skips entirely.

If the user skips Screen 8 entirely, the competitive intelligence features of the platform still function — they simply do not run for any specific competitors. The AI search intelligence, which monitors industry trends and competitor mentions broadly rather than tracking specific companies, continues to provide value. The specific competitor monitoring — ad library tracking, website change detection, social monitoring for named companies — does not run. The user can always return to add competitors from the Foundation settings.

## **Screen 9 — Competitive Differentiation**

**What This Screen Achieves**

Knowing who your competitors are is tactical. Understanding how you are genuinely different from them, and honestly assessing where they are stronger, is strategic. Screen 9 is the screen that most directly forces strategic clarity, because it requires the user to make claims about their differentiation and then immediately tests those claims against the obvious pushback.

**What the User Sees**

For each competitor named on Screen 8, a structured comparison section appears. Each section has two parts. The first part asks: 'Why would a customer choose you over this competitor?' Below this question are two sub-questions: 'What can you do that this competitor cannot, or does not do as well?' and 'What is the proof of this claim — what evidence do you have that this advantage is real?'

The second part asks: 'Where is this competitor stronger than you?' Below this question: 'What do they do well that you do not fully match?' and 'How do you compensate for or work around this weakness in your positioning?'

The structure of asking for weaknesses as well as strengths is the most important design decision in Screen 9. Most systems and most marketing exercises focus exclusively on strengths. This creates positioning that is aspirational rather than honest — positioning that the business owners know is true but that sophisticated buyers can see through. Agents that know honest competitive weaknesses can develop positioning that acknowledges the weakness strategically rather than pretending it does not exist or being caught off guard when a prospect raises it.

**The AI Devil's Advocate**

After the user completes the differentiation claim for each competitor, the system runs a brief Flash-Lite inference call that plays devil's advocate: 'A skeptical buyer comparing you to this competitor might say...' and then generates the most obvious objection to the differentiation claim. This objection appears below the user's claim with a prompt: 'How would you respond to this objection?'

This devil's advocate mechanism produces two benefits simultaneously. It stress-tests the differentiation claim — a claim that cannot withstand an obvious objection is not a strong differentiator and needs to be refined. And it generates the actual objection-handling language that the agents need for persuasive copy and strategic positioning. The user's response to the objection is exactly the language that turns a weak positioning claim into a compelling one.

**Edge Cases**

When the user identifies a competitor as much larger and much better resourced than their own business — a common situation for startups competing against established players — the differentiation exercise takes on a specific character. The system recognises this dynamic from the company size data extracted during the competitor deep scan and prompts accordingly: 'This competitor has significant advantages in scale and resources. The strongest differentiation strategy against a larger competitor is often specificity — being the best option for a very specific customer in a way they are not positioned to match. What specific customer situation do you serve better than they do, even if you serve it at smaller scale?'

## **Screen 10 — The Positioning Statement**

**What This Screen Achieves**

Screen 10 is where everything from the previous nine screens converges into the single most important strategic artifact in the Foundation: the positioning statement. This is not a tagline and it is not a mission statement. It is the strategic sentence or two that defines, with precision, who the business serves, what problem it solves, what category it occupies, what specific benefit it delivers, and how it is different from the alternatives. Every agent reads this statement in every session. Every campaign, every piece of content, every Council debate synthesis is filtered through it.

**The Draft Generation**

The system generates a draft positioning statement from the accumulated Foundation data before the user reaches this screen, so that when they arrive, they are editing rather than composing from scratch. The draft follows the structure: 'For \[ICP Name\] who \[specific situation from Screen 5\], \[Business Name\] is the \[category\] that \[primary benefit from Screen 4\]. Unlike \[primary competitor from Screen 8\], we \[key differentiation from Screen 9\].'

This structure is the classic positioning template, and it is used here not because it is the only valid positioning structure but because it is the one that most reliably surfaces the strategic clarity or lack thereof in the Foundation data. When the template produces an awkward result — when any of the blanks is difficult to fill in a compelling way — it reveals a gap in the Foundation data or a strategic ambiguity that needs to be resolved before the positioning will be clear.

**The Workshop Interface**

The screen is divided into two areas. The left area shows the generated draft, with each component of the structure highlighted in a different colour so the user can see clearly which part of the statement corresponds to which earlier input. The right area is an editing workspace where the user can modify the draft.

The editing workspace is not a simple text field. It is a structured editor that maintains the positioning template structure while allowing the user to modify each component. Changing the ICP description updates only that component. Changing the benefit description updates only that component. This structure prevents the positioning statement from drifting into tagline territory — sentences that sound good but do not actually position the business against any specific alternative.

**The AI Workshop Partner**

As the user edits, the system provides real-time feedback on the positioning quality. Feedback is specific rather than generic: 'The benefit description here — 'better results' — is too generic to create meaningful differentiation. Consider replacing it with a specific outcome that is measurable and that your competitor cannot claim. For example: 'fifty percent faster campaign setup' or 'the only system that learns your specific audience and gets smarter each month.' Feedback appears as subtle inline suggestions that the user can accept, dismiss, or use as inspiration for their own phrasing.

The Flash model also monitors for the most common positioning mistakes: benefit descriptions that describe features rather than outcomes, category definitions that are too broad to differentiate or too narrow to be credible, ICP descriptions that are too general to be useful, and differentiation claims that are easily replicated by competitors and therefore not real differentiation. When these problems are detected, the feedback is specific and solution-oriented rather than merely critical.

**Locking the Positioning**

When the user is satisfied with the positioning statement — when it reads as true, specific, and differentiated — they confirm it. The confirmation is slightly formal: the button reads 'Lock this positioning' rather than 'Continue' or 'Next'. This formality is intentional: the positioning statement is the most important strategic decision they are making in the Foundation, and the language reinforces that.

A locked positioning statement can be updated later from Foundation settings. But changing it triggers the same downstream impact assessment that any Foundation change triggers — showing the user what campaigns reference this element, which agent memories might be inconsistent with the new positioning, and whether a Council review of current strategy would be advisable. Changing the positioning statement mid-campaign is a significant decision and the system treats it as one.

## **Screen 11 — Brand Personality**

**What This Screen Achieves**

A positioning statement defines what the business says. Brand personality defines how it says it. These are related but distinct. The same positioning — 'the marketing intelligence system for Indian SMBs that learns your business' — could be expressed by a formal, authoritative voice that emphasises expertise and credibility, or by a casual, energetic voice that emphasises accessibility and excitement, or by a warm, collaborative voice that emphasises partnership and support. All three expressions of the same positioning would produce completely different consumer impressions. Screen 11 makes the brand voice choice explicit.

**The Slider System**

Five dimensional sliders form the core of Screen 11. Each slider sits between two described poles rather than between abstract positive and negative ends. The five dimensions are: Formal at one end and Casual at the other; Technical at one end and Accessible at the other; Conservative at one end and Bold at the other; Serious at one end and Playful at the other; and Authoritative at one end and Collaborative at the other.

Each slider position is accompanied by a short description of what content at that position actually sounds like. At the Formal end of the first dimension: 'Addresses audiences respectfully and professionally, avoids contractions, maintains consistent structure.' At the Casual end: 'Speaks like a knowledgeable friend, uses contractions freely, may use colloquialisms appropriate to the audience.' The descriptions help users calibrate their selections against actual output rather than abstract personality labels.

**The Live Example System**

This is the feature that makes Screen 11 memorable. As the user adjusts any slider, a panel on the right side of the screen shows three live examples of content written at the current slider configuration: a sample social media caption, a sample ad headline, and a sample email opening line. These examples are generated by a Flash-Lite call that fires with every slider adjustment. They update in near real-time — within one to two seconds of the slider being moved.

The live examples transform an abstract personality calibration exercise into a concrete output preview. When a user slides from Formal toward Casual and watches the social caption go from 'We are pleased to announce the launch of our enterprise solution...' to 'We just dropped something you are going to love...', they can immediately feel the difference and decide where they want to land. This feedback loop produces much more accurate brand voice calibration than asking users to select adjectives or choose between personality archetypes.

**The Descriptor Tag Cloud**

Below the sliders, a tag cloud of brand personality descriptors allows the user to select three to five words that feel most true to the brand. The tags include: Authoritative, Warm, Direct, Inspiring, Practical, Edgy, Premium, Approachable, Expert, Honest, Ambitious, Dependable, Creative, Analytical, Empathetic, Bold, Trustworthy, Innovative, Grounded, and Energetic. The user can also type in custom descriptors that are not in the pre-built list.

The selected descriptors serve a different function from the sliders. The sliders calibrate the dimensional qualities of the voice. The descriptors capture the aspirational identity of the brand — the words that, if used by a customer to describe the brand, would indicate that the brand's marketing was working as intended. Together, sliders and descriptors create a more complete voice profile than either alone.

**Voice Fingerprint Generation**

When the user confirms their selections, the combined slider configuration and descriptor tags are processed into a voice fingerprint: a vector embedding of the brand voice profile that is used for semantic similarity scoring against all generated content. Content that scores high similarity to this fingerprint passes the brand voice check. Content that scores low fails and is either auto-revised or flagged for review. The voice fingerprint is the technical implementation of the brand voice standard.

## **Screen 12 — Voice in Practice**

**What This Screen Achieves**

The slider configuration from Screen 11 defines the desired brand voice in abstract dimensions. Screen 12 provides three specific examples of that voice in practice, written by the user themselves. These examples serve as the ground truth for voice calibration — they are more reliable than any algorithm's interpretation of the slider settings because they represent the actual output the user considers to be on-brand.

**The Three Writing Exercises**

Exercise one: 'In one sentence, describe what your business does as if you were explaining it to someone you just met at a dinner party.' This prompt is chosen because the dinner party context invites the user's natural, unguarded voice — the version of their business description that has not been polished into corporate language. The answer to this question is often the most authentic version of the business's value proposition, and it is frequently more effective in marketing than the carefully crafted language on the website.

Exercise two: 'Write a social media post announcing that you just helped a customer achieve a great result. You are genuinely excited about it.' The emotion-inviting framing — the explicitly noted genuine excitement — is important because it gives the user permission to be enthusiastic in a way that corporate writing culture sometimes suppresses. The resulting text captures how the brand sounds at its most human and most compelling.

Exercise three: 'A potential customer just said your price is too high. Write your response to them.' This exercise is the most revealing of the three, because it captures the brand voice under mild pressure. Does the brand get defensive? Does it immediately apologise and offer a discount? Does it confidently redirect the conversation to value? Does it ask a question to understand the objection better? All of these are legitimate brand choices, and the choice made here reveals something fundamental about the brand's self-perception and customer relationship philosophy.

**What Happens With These Examples**

The three writing samples are embedded and stored alongside the voice fingerprint from Screen 11. They become few-shot examples that are injected into content generation prompts — the agent tasked with generating copy for this brand sees these three examples as demonstrations of the brand's voice and uses them as stylistic anchors. They are also used to validate the accuracy of the voice fingerprint: if the examples score poorly against the fingerprint derived from the sliders, the fingerprint is recalibrated to align with the examples, because the examples represent the actual voice rather than the abstract description of it.

## **Screen 13 — Content Territories**

**What This Screen Achieves**

Content territories define the topical universe within which the brand will create content. They answer the question: what subjects does this brand have the right to talk about, and why? This boundary matters because the most common mistake in content strategy is creating content about topics that are interesting to the brand but irrelevant to the ICP, or topics that are relevant to the ICP but which the brand has no credible claim to address.

**What the User Sees**

The screen presents a grid of topic territory cards, generated by the system from the Foundation data accumulated so far: industry, ICP, positioning, and product descriptions. Each card shows a topic area and a brief reason for why this territory is suggested. The user selects the territories that feel right — three to seven is the recommended range — and deselects those that do not fit.

The generated suggestions are organised into three tiers that appear visually distinct. The first tier is core territories: topics that are directly related to the business's product or service. For a marketing intelligence platform, this tier might include digital marketing strategy, paid advertising optimisation, and competitive analysis. These are the territories where the brand has the most obvious right to speak.

The second tier is adjacent territories: topics that the ICP cares about that are related to but not directly about the product. For the same marketing platform, adjacent territories might include small business growth, entrepreneurship, and operational efficiency. These territories allow the brand to reach the ICP through their broader interests rather than only when they are actively thinking about marketing.

The third tier is culture territories: topics related to the values and identity the brand wants to be associated with. For a brand positioning around empowering small businesses, culture territories might include founder stories, Indian entrepreneurship, and business resilience. These territories are the most optional and the most risky — they can build brand affinity powerfully when done well, and can feel inauthentic and off-brand when done poorly.

**The Ownership Question**

For each selected territory, the user answers a brief follow-up: 'Why does your brand have the right to talk about this?' The answers do not need to be long — a sentence or two is sufficient. But the act of answering forces the user to connect each content territory to something the business genuinely knows or does or stands for. This prevents the content territory selection from becoming a wishful list of interesting topics rather than a realistic map of where the brand can create value.

## **Screen 14 — Marketing Channels**

**What This Screen Achieves**

Channel strategy in RaptorFlow is not about what channels exist in the world. It is about what channels this business will realistically use, what their current position on each channel is, and what their ambitions are for each channel in the next quarter. This distinction matters because agents designing campaigns for a business that has never run a Meta ad need to design different campaigns than agents working with a business that has been running sophisticated Meta campaigns for three years and has significant retargeting audiences built up.

**What the User Sees**

Two sequential interactions on the same screen. The first asks: which of these channels does your business currently use for marketing? A grid of channel cards is presented — Meta Ads, Google Ads, LinkedIn Ads, Instagram organic, LinkedIn organic, YouTube, Email marketing, WhatsApp Business, SEO and content, Events and offline, and Referral and word of mouth. The user selects all that currently receive any meaningful time or money. Meaningful is defined in the helper text as at least once a month with some intentionality — not just the Facebook page that occasionally gets a boost when someone remembers.

The second interaction asks: which channels would you like to be active on in the next ninety days, even if you are not currently using them? This second selection can overlap with the first but often extends it — a business currently focused on Instagram organic might want to add Meta Ads in the next quarter, or a business doing only paid search might want to add email marketing.

**Channel-Specific Micro-Questions**

For each channel selected in either question, a brief follow-up appears. For Meta Ads: are you running campaigns currently, and if so what is the monthly spend? For Google Ads: are you running search campaigns, display campaigns, or both? For email marketing: which platform are you using and approximately how large is your list? For SEO: do you have a blog or content hub, and how regularly are you publishing?

These micro-questions are small data points that produce large downstream impacts. The Media Buyer agent uses the ad spend data to calibrate budget allocation recommendations. The Muse AI uses the email list size to calibrate the ambition of email campaign recommendations. The SEO tracker uses the publishing frequency to understand the baseline from which any content strategy improvements will be measured.

## **Screen 15 — Goals and KPIs**

**What This Screen Achieves**

Every other screen in the Foundation describes what the business is. Screen 15 describes what the business wants to become in the next ninety days, and in quantifiable terms. This transformation from description to aspiration — from identity to ambition — is the final piece that allows the agents to evaluate whether their recommendations are working. Without clear, measurable goals attached to specific numbers and timelines, the Daily Wins briefing has nothing to report against, and the Analytics Director has no baseline for assessing performance.

**The Goal Selection**

The primary goal question asks the user to select from six categories: increase website traffic, generate more leads, drive more direct sales, grow brand awareness and following, improve customer retention, or successfully launch something new. These six cover the full spectrum of marketing objectives that most SMBs face. The user selects their primary goal — the one objective that, if achieved in the next ninety days, would represent unambiguous success.

After selecting the primary goal category, specific numerical targets are set. Traffic goals: current monthly visitors and target monthly visitors. Lead goals: current monthly leads and target monthly leads. Sales goals: current monthly marketing-attributed revenue and target. Awareness goals: current followers or reach and target. Retention goals: current churn rate and target churn rate. Launch goals: the launch date and the specific metric that will define a successful launch.

The system does not suggest what targets the user should set. It cannot know what is ambitious for a specific business without much more context than the Foundation provides. What it does is flag obviously problematic targets. A target of zero to ten thousand website visitors in thirty days for a business with no existing SEO presence receives a note: 'This target would require either significant paid traffic investment or a viral content event. Is this the right timeframe, or would a more gradual ramp-up better reflect realistic expectations?' The system raises the question without making the decision.

**Secondary Goals**

Beyond the primary goal, the user can define up to two secondary goals. Secondary goals receive less weight in the Daily Wins briefing and campaign planning, but they are tracked and reported. A business primarily focused on lead generation might have customer retention as a secondary goal — the system watches both, prioritises recommendations around the primary, but surfaces relevant retention opportunities when they arise.

**The Budget Question**

The final element of Screen 15 is the marketing budget question. Specifically: what is the monthly budget available for paid advertising? This is not what the user is paying for RaptorFlow — it is their ad spend budget for campaigns. The question is accompanied by helper text explaining why it matters: budget size affects which channel mix is realistic, what campaign timeline is appropriate, and how the Media Buyer allocates spend across the channels identified on Screen 14.

The budget answer is stored in the Foundation and used by agents exclusively for calibrating recommendations. It is never shared externally and never affects the subscription price. Budget ranges are offered as a selector — below ten thousand rupees per month, ten to fifty thousand, fifty to two lakh, two to ten lakh, above ten lakh — rather than a specific number field, because most users are uncomfortable specifying an exact budget number but comfortable selecting a range.

## **Screen 16 — Keywords and SEO**

**What This Screen Achieves**

Screen 16 activates the SEO monitoring component of the intelligence pipeline. Every keyword the user identifies on this screen becomes a tracked data point — the system begins monitoring SERP rankings for these keywords for both the user's domain and the competitor domains identified on Screen 8 from the moment the Foundation is complete.

**The Keyword Collection**

The screen presents an input field for keywords with a suggestion system that runs based on the accumulated Foundation data. As the user starts typing, the system suggests completions based on the industry, ICP, and product descriptions. The user can accept suggestions, ignore them and type their own, or start from the suggestions and modify them.

The system also generates a list of suggested keywords proactively: fifteen to twenty suggestions organised into three intent categories. Informational intent keywords are searches made by someone researching the problem — they are in the awareness stage. Commercial intent keywords are searches made by someone evaluating solutions — they are in the consideration stage. Transactional intent keywords are searches made by someone ready to buy — they are in the decision stage. This categorisation helps users build a keyword set that covers the full customer journey rather than focusing only on the highest-intent terms that are also the most competitive.

**SEO Reality Check**

For each keyword the user selects, the system runs a quick assessment of current ranking difficulty — a simple calculation based on the average domain authority of the pages currently ranking in the top ten positions for that keyword. Keywords where the competitive bar is very high receive a note: 'This keyword is highly competitive. Ranking well for it would require significant content investment over time. It is worth tracking, but a more achievable near-term strategy might focus on \[lower-competition alternative\].' This reality check sets expectations without discouraging ambition.

## **Screen 17 — Existing Assets**

**What This Screen Achieves**

Screen 17 prevents the most common inefficiency in AI-assisted marketing: generating things that already exist. By inventorying what the business already has, the agents can build on existing assets rather than duplicating them, and can reference existing proof points and social proof in their work rather than having to manufacture or omit them.

**The Asset Inventory**

A checklist of common marketing asset types with file upload options for each. Brand guidelines and logo files — uploaded files are processed to extract the colour palette and primary font, which are stored in the Foundation for reference in design direction. Existing advertising creative — any ads that have run before, successful or not, uploaded as reference material for the agents. Customer testimonials — text or PDF testimonials that can be quoted in copy with appropriate attribution. Case studies — documents that can be referenced as proof points. Product photography or video — uploaded to S3 and referenced in Foundation for use in content guidance. Email templates — HTML files processed to extract the template structure and design standards.

Social media handles are collected at the bottom of this screen. Instagram handle, LinkedIn company page URL, Facebook page URL, YouTube channel, Twitter or X handle, and any other relevant platforms. These are added to the social monitoring stack immediately — from this moment forward, these accounts are monitored for post performance metrics that inform the content recommendations and competitive benchmarking.

## **Screen 18 — Current Frustrations**

**What This Screen Achieves**

This is the screen that most directly shapes the early experience of using the product, because it tells the system what the user needs most urgently. The frustration data adjusts the priority weighting of features and recommendations so that users encounter the capabilities most relevant to their specific pain points first, rather than getting a generic onboarding experience regardless of their situation.

**What the User Sees**

A multi-select question with a clean card-based interface: 'What is your biggest marketing frustration right now? Select all that apply.' The options are: I do not know what to post or write; Creating content takes too long; My ads are not converting to sales; I cannot tell what is working and what is not; I struggle to keep up with what competitors are doing; I have no time for strategy because execution takes everything; I cannot afford the level of expertise I need; and I feel overwhelmed and do not know where to start.

Below the multi-select options, a free-text field invites additional context: 'If there is something specific frustrating you about your marketing right now that is not captured above, describe it here.' This field produces data that frequently surfaces frustrations specific to the user's industry or situation that the generic options miss.

**How Frustration Data Shapes the Experience**

The frustration selections create a personalised configuration of the early product experience. A user who selected 'I do not know what to post' will find that Muse's first proactive recommendation is a content calendar suggestion. A user who selected 'My ads are not converting' will find that the first Daily Wins briefing after campaign launch focuses heavily on conversion analysis and the Media Buyer's recommendations. A user who selected 'I struggle to keep up with competitors' will find that the Intel dashboard is prominently surfaced and the first Nudge they receive will be competitive intelligence.

This personalisation is not just about showing different features first. It shapes the language the Campaign Strategist uses. A user whose primary frustration is overwhelm gets a Strategist who is more step-by-step and reassuring. A user whose primary frustration is lack of results gets a Strategist who is more direct and data-forward. The frustration data feeds into the Strategist's personality expression system alongside the personality calibration from Screen 21.

## **Screen 19 — Existing Tools**

**What This Screen Achieves**

Screen 19 establishes the operational context of the business's current marketing technology stack. RaptorFlow does not integrate with any of these tools at launch. But knowing what tools the user works with shapes the recommendations: agents do not suggest workflows that duplicate tools the user already has, do not recommend features that conflict with established tools, and can calibrate the migration effort required to consolidate certain functions into RaptorFlow over time.

**The Tools Checklist**

Organised in four categories. Analytics and tracking: Google Analytics, Meta Pixel, Google Search Console. Advertising management: Meta Ads Manager, Google Ads, LinkedIn Campaign Manager. Email marketing: Mailchimp, Klaviyo, Brevo, or other. Design and content creation: Canva, Adobe Express, other. CRM and customer management: any CRM platform in use, including the business owner's perception of what it does. Social media management: any scheduling or management tools. The user checks all that currently apply.

For the CRM field specifically, a follow-up question asks how the business currently tracks its customer relationships and sales pipeline. This is not asking about software — it is asking about the process, because many Indian SMBs track relationships in spreadsheets, WhatsApp threads, or simply in the business owner's memory. The honest answer to this question frequently reveals that CRM is a significant operational gap that future RaptorFlow development could address.

## **Screen 20 — Reference Brands**

**What This Screen Achieves**

Reference brands reveal aesthetic and strategic sensibility. The brands a founder admires tell the agents something about the marketing culture the founder wants to build — their sense of quality, their relationship with convention, their comfort with boldness, their appreciation for craft. These signals complement and sometimes override the explicit personality slider settings from Screen 11.

**What the User Sees**

A clean input asking for two or three brands, not necessarily competitors, not necessarily in their industry, whose marketing the user genuinely admires. The prompt is specific about what 'admires' means in this context: brands whose ads make you want to buy something, brands whose social content you actually read, brands whose campaigns you find interesting or beautiful or smart. The reference should be genuine — not a brand the user thinks they should admire, but one they actually do.

After each brand is entered, the system does a quick search to confirm it can identify the brand and surface a brief description. The user confirms the identification — 'Yes, this is the Zoho I mean' — and optionally adds a note about specifically what they admire about that brand's marketing: 'Their product-led content, the way they make complex software feel accessible.'

**How Reference Brands Are Used**

The reference brand data is processed in two ways. First, the brands are analysed for their communication characteristics: their tonal register, their content format preferences, their visual language signals, their narrative approach, their relationship with the consumer. These characteristics are compared against the brand personality configuration from Screen 11 to identify any gaps or confirmations. Where they confirm the slider settings — the reference brands are consistently casual and energetic, and the slider configuration is casual and energetic — the Foundation gains confidence. Where they conflict — the reference brands are premium and restrained but the slider configuration is bold and playful — the system surfaces this discrepancy and asks the user to resolve it.

Second, the reference brand analysis feeds into content generation as stylistic guidance. When a Council avatar is generating campaign concepts, the reference brand analysis informs the aesthetic ambition level, the narrative complexity, and the degree of creative risk that would feel appropriate for this brand. A business that admires Apple and Dove will get different creative direction than a business that admires Zoho and Freshworks, even if their slider configurations are similar.

## **Screen 21 — The Campaign Strategist**

**What This Screen Achieves**

Screen 21 is the culmination of the Foundation and the most emotionally significant moment in the entire onboarding experience. It is where the Campaign Strategist — the user's primary point of contact, the agent they will interact with every day for as long as they use the product — comes into existence. It is the moment where the Foundation transitions from data collection to the birth of a relationship.

**Part One: Naming the Strategist**

The first decision on Screen 21 is the name. The prompt reads: 'Your Campaign Strategist is about to come to life. What would you like to call them?' Below the prompt is a name input field — not a dropdown, not a selection from predefined options, a free text field where the user enters any name they choose.

The name does not have to be a human name. Some users name their Strategist after a marketing legend they admire. Some use their own name with a qualifier. Some create a name from their brand identity — a company called Kite Analytics might name their Strategist 'Kira'. The system accepts any name and immediately uses it throughout the remainder of Screen 21 and everywhere in the product thereafter.

The psychological significance of naming should not be underestimated. Naming an entity is an act of relationship. Users who have named their Campaign Strategist refer to that Strategist by name in conversation with others — 'I asked Riya about the competitor pricing and she recommended...' This reference pattern is observable in user behaviour data from analogous products and it is a strong predictor of sustained engagement.

**Part Two: Personality Calibration**

After naming the Strategist, the user calibrates their personality on three dimensions. The dimensions are presented as a brief description of what each end of the spectrum looks and feels like in practice, illustrated with a short example message from the Strategist at each end.

Dimension one: Decisive vs Collaborative. Decisive means the Strategist presents a clear recommendation and expects the user to implement or push back. Collaborative means the Strategist presents options, explains trade-offs, and asks the user to weigh in before settling on a direction. Example messages at each end show the difference concretely.

Dimension two: Data-driven vs Instinct-driven. Data-driven means the Strategist grounds every recommendation in specific evidence and is explicit about when evidence is absent. Instinct-driven means the Strategist incorporates qualitative judgment and pattern recognition more freely alongside quantitative evidence. Neither is right for all users — some users are comforted by data backing, others find excessive data references tedious.

Dimension three: Direct vs Diplomatic. Direct means the Strategist says what they think without softening, including when they think the user is making a mistake. Diplomatic means the Strategist frames difficult feedback carefully and prioritises maintaining a comfortable working relationship alongside honest assessment.

These three dimensions produce eight distinct Strategist personality configurations. The system suggests the configuration that best fits the accumulated signals from the Foundation — the business stage, the frustrations noted on Screen 18, the brand personality from Screen 11, and the business model complexity — but the user can freely override any dimension.

**Part Three: The Foundation Review**

Before the Foundation is committed, the user sees a complete review of every major decision made across all twenty screens. This review is not a long list of data fields. It is a structured strategic summary presented as if the Strategist is briefing the user on what they understand about the business.

The review is presented in the Strategist's voice — already calibrated to the personality configuration the user just set: 'Here is what I understand about \[Business Name\]. You serve \[ICP Name\] — \[ICP description\]. The problem you solve is \[problem statement from Screen 5\]. Your positioning is \[positioning statement from Screen 10\]. Your primary goal for the next ninety days is \[goal from Screen 15\]. The competitors I will be watching are \[competitor names from Screen 8\]. And your brand should always sound \[voice descriptors from Screen 11\].'

This brief is the first time the user hears the Strategist's voice. It is the first time the Foundation comes alive as a coherent strategic picture rather than a collection of individual answers. Many users report that this is the moment they understand what the Foundation is and why they spent twenty screens building it.

Each element of the summary is clickable. Clicking takes the user back to the relevant screen to make changes before committing. The review is the last chance to fix anything before the Foundation is locked.

**Part Four: Build My Office**

The final button on Screen 21 reads 'Build my office'. When the user clicks it, several things happen simultaneously. The Foundation data is committed to the database and the Foundation JSON is compiled. All twenty-one agents are initialised with the Foundation context. The quick office construction animation begins — a loading screen that shows the office being assembled, agents appearing at their desks, the Strategist settling into the corner office, the nameplate being installed on the office door with the name the user chose.

The construction animation typically takes eight to twelve seconds. When it resolves, the user is looking at their completed office for the first time. All twenty-one agents are at their positions. The office is named with their company. The Strategist's office door has the name they chose on it. The first Nudge appears — a welcome message from the Strategist in the app notification system, written in their calibrated personality: 'I have everything I need. Let us start building something.

The Foundation is complete. The relationship begins.

# **Part Three: The Foundation JSON — What Gets Stored**

## **The Complete Data Structure**

When the Foundation is committed on Screen 21, all twenty screens of data are compiled into a structured JSON document that becomes the ground truth for every agent in the system. This document is cached by Vertex AI's context caching mechanism, allowing it to be injected into agent contexts at ninety percent reduced cost relative to sending the full document fresh with every inference call.

The Foundation JSON contains eleven major sections. The business identity section contains the business name, website URL, industry category, business model, primary description, business stage, and team size. The product catalogue section contains a structured array of all products and services with their names, descriptions, customer outcomes, and pricing models. The problem articulation section contains the three-part problem narrative from Screen 5 and the synthesised problem statement. The ICP section contains a structured array of all ICPs — primary and secondary — with all their descriptive fields, the persona names, and the language samples.

The competitive landscape section contains all competitor records: their names, URLs, the differentiation assessment for each, the identified weaknesses, and the competitive context notes. The positioning section contains the confirmed positioning statement. The brand voice section contains the five slider values, the selected descriptor tags, the voice fingerprint embedding, and the three voice example texts from Screen 12. The content strategy section contains the selected content territories with their ownership justifications.

The channel and performance section contains the current channel map, the aspirational channel map, all channel-specific meta-data from the micro-questions, and the goal and KPI targets with their numerical values. The asset inventory section contains references to all uploaded assets and their extracted metadata. The meta section contains the Strategist name, the Strategist personality configuration, the reference brand analysis, and the frustration prioritisation data.

## **Foundation Versioning**

Every change to the Foundation after initial completion creates a new version record. The version history stores: what changed, when it changed, who changed it, and what the downstream impact assessment showed at the time of the change. This history is visible to the user in Foundation settings and serves as a strategic log of how the business's positioning and identity have evolved over time.

Agents have access to the Foundation version history as part of their context when the history is relevant. A Campaign Strategist reviewing performance trends across twelve months of campaigns can reference the Foundation version at the time of each campaign to understand whether positioning changes correlate with performance changes. This longitudinal intelligence is one of the capabilities that only becomes available after extended product use.

## **The Live Foundation**

The Foundation is not a setup document that becomes static after completion. It is a living document that the system continuously monitors for staleness and opportunities to update. When the Muse memory pattern analysis detects that the user has mentioned information in conversations that contradicts or extends the Foundation — a new product line mentioned in passing, a change in primary ICP mentioned in a Muse conversation, a competitor that was not named in the Foundation that the user keeps referencing — the system surfaces a Foundation update suggestion.

Foundation update suggestions appear as a specific type of Nudge with a different visual treatment from competitive or performance Nudges. They are labelled as Foundation insights and explain what was detected and what change is being suggested: 'In three recent conversations you have mentioned a new enterprise product line that is not in your Foundation. Would you like to add it so your agents can plan campaigns for it?' The user can accept the suggestion, which opens the relevant Foundation screen pre-filled with the extracted information, dismiss the suggestion, or ask Muse to discuss it before deciding.
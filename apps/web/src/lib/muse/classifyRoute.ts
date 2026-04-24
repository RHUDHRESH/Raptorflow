import { convergeFast } from "@/lib/bedrock";

export type MuseRoute = "tactical" | "strategic" | "campaign" | "council" | "foundation";

export async function classifyRoute(userMessage: string): Promise<MuseRoute> {
  const prompt = `Classify this marketing question into exactly one category.
Return only the category word, nothing else.

Categories:
- tactical: specific content requests ("write me a tweet", "suggest email subject lines", "give me 5 headline options")
- strategic: high-level strategy questions ("what should our positioning be", "how do we grow", "what's our biggest weakness")
- campaign: campaign-specific questions ("how should I structure this campaign", "what moves should I make for X")
- council: requests for multi-perspective debate ("what would the council say about", "get multiple opinions on", "debate whether we should")
- foundation: questions about company identity ("update our ICP", "change our brand voice", "what is our positioning")

Message: "${userMessage.trim()}"

Category:`;

  const text = await convergeFast(prompt, 20);
  const category = text
    .trim()
    .toLowerCase()
    .replace(/[^a-z_]/g, "");

  if (["tactical", "strategic", "campaign", "council", "foundation"].includes(category)) {
    return category as MuseRoute;
  }
  return "tactical";
}

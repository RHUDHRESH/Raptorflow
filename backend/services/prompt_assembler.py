"""
Prompt Assembler Middleware

Assembles LLM prompts with BCM context, enforcing token budgets and caching.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import tiktoken

from .services.upstash_client import get_upstash_client
from .api.v1.context import get_manifest


@dataclass
class TokenBudget:
    bcm: int = 1200
    snippets: int = 400
    task: int = 300


class PromptAssembler:
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.upstash = get_upstash_client()
        self.budget = TokenBudget()

    async def assemble(
        self,
        workspace_id: str,
        task_prompt: str,
        intent: str,
        snippets: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Assemble complete LLM prompt with BCM context and snippets

        Args:
            workspace_id: Workspace UUID
            task_prompt: The task-specific prompt
            intent: Intent/key for caching
            snippets: Optional vector snippets to include

        Returns:
            Assembled prompt string with role tags
        """
        # Check cache first
        cache_key = (
            f"llmcache:w:{workspace_id}:i:{intent}:p:{self._hash_prompt(task_prompt)}"
        )
        cached = await self.upstash.get(cache_key)
        if cached:
            return cached

        # Get BCM manifest
        bcm = await get_manifest(workspace_id)
        bcm_tokens = self._count_tokens(str(bcm.manifest))

        # Apply token budgeting
        if bcm_tokens > self.budget.bcm:
            bcm.manifest = self._trim_to_tokens(bcm.manifest, self.budget.bcm)

        # Process snippets if provided
        snippet_text = ""
        if snippets:
            snippet_text = self._process_snippets(snippets)

        # Assemble final prompt
        prompt = (
            f"<BCM version='{bcm.version}' checksum='{bcm.checksum}'>\n"
            f"{bcm.manifest}\n"
            f"</BCM>\n\n"
            f"<SNIPPETS>\n"
            f"{snippet_text}\n"
            f"</SNIPPETS>\n\n"
            f"<TASK>\n"
            f"{task_prompt}\n"
            f"</TASK>"
        )

        # Cache for future use
        await self.upstash.set(cache_key, prompt, ttl=86400)  # 24h

        return prompt

    def _process_snippets(self, snippets: Dict[str, Any]) -> str:
        """Process and trim snippets to fit token budget"""
        total_tokens = 0
        processed = []

        for snippet in snippets.values():
            text = snippet.get("text", "")
            tokens = self._count_tokens(text)

            if total_tokens + tokens > self.budget.snippets:
                remaining = self.budget.snippets - total_tokens
                if remaining > 50:  # Only include if meaningful space remains
                    text = self._trim_to_tokens(text, remaining)
                    processed.append(text)
                break

            processed.append(text)
            total_tokens += tokens

        return "\n\n".join(processed)

    def _count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken"""
        return len(self.encoder.encode(text))

    def _trim_to_tokens(self, content: Any, max_tokens: int) -> Any:
        """Trim content to fit within token budget"""
        # Implementation depends on content structure
        # Simplified for example - would need actual trimming logic
        return content

    def _hash_prompt(self, prompt: str) -> str:
        """Create simple hash of prompt for caching"""
        return str(hash(prompt))

import { assembleContext, type HarnessContextPack, type HarnessInput } from "./index";

export function buildPrompt(contextPack: HarnessContextPack, taskPrompt: string): string {
  if (!contextPack.contextPrefix.trim()) return taskPrompt;

  return `${contextPack.contextPrefix}

---

${taskPrompt}`;
}

export async function harnessPrompt(
  input: HarnessInput,
  taskPrompt: string,
): Promise<{ prompt: string; meta: HarnessContextPack["meta"] }> {
  const pack = await assembleContext(input);
  return {
    prompt: buildPrompt(pack, taskPrompt),
    meta: pack.meta,
  };
}

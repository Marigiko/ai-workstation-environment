import { tool } from "@mimo-ai/plugin/tool"

export default tool({
  description: "Benchmark different models with the same prompt",
  args: {
    prompt: tool.schema.string().describe("Test prompt to send to all models"),
    models: tool.schema.string().optional().describe("Comma-separated model names (default: local,claude-sonnet-4-20250514,gpt-4)"),
  },
  async execute(args) {
    const baseURL = process.env.LITELLM_URL || "http://localhost:4000"
    const apiKey = process.env.LITELLM_API_KEY || "sk-litellm-master-key"
    const modelList = args.models?.split(",").map(m => m.trim()) || ["local", "claude-sonnet-4-20250514", "gpt-4"]

    const results = await Promise.all(
      modelList.map(async (model) => {
        const start = Date.now()
        try {
          const response = await fetch(`${baseURL}/v1/chat/completions`, {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${apiKey}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              model,
              messages: [{ role: "user", content: args.prompt }],
              max_tokens: 100,
            }),
          })

          const elapsed = Date.now() - start

          if (!response.ok) {
            return {
              model,
              status: "error",
              time: elapsed,
              error: `HTTP ${response.status}`,
            }
          }

          const data = await response.json() as any
          const tokens = data.usage?.total_tokens || 0

          return {
            model,
            status: "success",
            time: elapsed,
            tokens,
            response: data.choices?.[0]?.message?.content?.substring(0, 100) || "",
          }
        } catch (error) {
          return {
            model,
            status: "error",
            time: Date.now() - start,
            error: String(error),
          }
        }
      })
    )

    const lines = ["# Model Benchmark Results\n"]
    lines.push(`**Prompt:** ${args.prompt.substring(0, 100)}...\n`)
    lines.push("| Model | Status | Time | Tokens |")
    lines.push("|-------|--------|------|--------|")

    for (const r of results) {
      if (r.status === "success") {
        lines.push(`| ${r.model} | ✓ | ${r.time}ms | ${r.tokens} |`)
      } else {
        lines.push(`| ${r.model} | ✗ | ${r.time}ms | ${r.error} |`)
      }
    }

    lines.push("\n## Responses\n")
    for (const r of results) {
      if (r.status === "success" && r.response) {
        lines.push(`### ${r.model}`)
        lines.push(`> ${r.response}...\n`)
      }
    }

    return lines.join("\n")
  },
})

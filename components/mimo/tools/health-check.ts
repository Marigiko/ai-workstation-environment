import { tool } from "@mimo-ai/plugin/tool"

export default tool({
  description: "Check health status of AI platform services",
  args: {
    verbose: tool.schema.boolean().optional().describe("Show detailed status"),
  },
  async execute(args) {
    const services = [
      { name: "LiteLLM", url: process.env.LITELLM_URL || "http://localhost:4000", endpoint: "/health" },
      { name: "Ollama", url: process.env.OLLAMA_URL || "http://localhost:11434", endpoint: "/api/tags" },
      { name: "Qdrant", url: process.env.QDRANT_URL || "http://localhost:6333", endpoint: "/healthz" },
    ]

    const results = await Promise.all(
      services.map(async (service) => {
        try {
          const response = await fetch(`${service.url}${service.endpoint}`, {
            signal: AbortSignal.timeout(5000),
          })
          return {
            name: service.name,
            status: response.ok ? "✓ healthy" : "✗ degraded",
            url: service.url,
          }
        } catch (error) {
          return {
            name: service.name,
            status: "✗ down",
            url: service.url,
            error: String(error),
          }
        }
      })
    )

    const healthy = results.filter(r => r.status.includes("healthy")).length
    const summary = `Platform Health: ${healthy}/${services.length} services healthy\n\n`

    const details = results
      .map(r => {
        let line = `${r.status} ${r.name} (${r.url})`
        if (args.verbose && r.error) {
          line += `\n  Error: ${r.error}`
        }
        return line
      })
      .join("\n")

    return summary + details
  },
})

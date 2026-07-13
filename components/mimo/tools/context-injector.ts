import { tool } from "@mimo-ai/plugin/tool"

export default tool({
  description: "Inject relevant context from Qdrant vector database (RAG)",
  args: {
    query: tool.schema.string().describe("Search query to find relevant context"),
    limit: tool.schema.number().optional().describe("Max number of results (default: 5)"),
    collection: tool.schema.string().optional().describe("Qdrant collection name (default: codebase)"),
  },
  async execute(args) {
    const qdrantURL = process.env.QDRANT_URL || "http://localhost:6333"
    const collection = args.collection || "codebase"
    const limit = args.limit || 5

    try {
      const searchResponse = await fetch(`${qdrantURL}/collections/${collection}/points/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          vector: await embedText(args.query),
          limit,
          with_payload: true,
        }),
      })

      if (!searchResponse.ok) {
        return `Error: Failed to search Qdrant (${searchResponse.status}). Collection '${collection}' may not exist.`
      }

      const data = await searchResponse.json() as any
      const results = data.result || []

      if (results.length === 0) {
        return `No relevant context found for: "${args.query}"`
      }

      const lines = [
        `# Context from Qdrant (${results.length} results)`,
        ``,
        `**Query:** ${args.query}`,
        ``,
      ]

      results.forEach((r: any, i: number) => {
        const payload = r.payload || {}
        const score = r.score?.toFixed(3) || "N/A"
        const content = payload.text || payload.content || JSON.stringify(payload)

        lines.push(`## Result ${i + 1} (score: ${score})`)
        if (payload.file) lines.push(`**File:** ${payload.file}`)
        if (payload.line) lines.push(`**Line:** ${payload.line}`)
        lines.push(``)
        lines.push(`\`\`\``)
        lines.push(content.substring(0, 500))
        if (content.length > 500) lines.push("...")
        lines.push(`\`\`\``)
        lines.push(``)
      })

      return lines.join("\n")
    } catch (error) {
      return `Error connecting to Qdrant: ${error}\n\nMake sure Qdrant is running: docker ps | grep qdrant`
    }
  },
})

async function embedText(text: string): Promise<number[]> {
  const baseURL = process.env.LITELLM_URL || "http://localhost:4000"
  const apiKey = process.env.LITELLM_API_KEY || ""

  const response = await fetch(`${baseURL}/v1/embeddings`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "text-embedding-3-small",
      input: text,
    }),
  })

  if (!response.ok) {
    throw new Error(`Embedding failed: ${response.status}`)
  }

  const data = await response.json() as any
  return data.data?.[0]?.embedding || []
}

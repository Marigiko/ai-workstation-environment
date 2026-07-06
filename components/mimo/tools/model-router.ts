import { tool } from "@mimocode/cli/plugin"

export default tool({
  description: "Switch the active model via LiteLLM API",
  args: {
    model: tool.schema.string().describe("Model name (e.g., claude-sonnet-4-20250514, gpt-4, local)"),
  },
  async execute(args) {
    const baseURL = process.env.LITELLM_URL || "http://localhost:4000"
    const apiKey = process.env.LITELLM_API_KEY || "sk-litellm-master-key"

    try {
      const response = await fetch(`${baseURL}/v1/models`, {
        headers: { "Authorization": `Bearer ${apiKey}` }
      })

      if (!response.ok) {
        return `Error: Failed to connect to LiteLLM (${response.status})`
      }

      const data = await response.json() as any
      const availableModels = data.data?.map((m: any) => m.id) || []

      if (!availableModels.includes(args.model)) {
        return `Model '${args.model}' not found. Available: ${availableModels.join(", ")}`
      }

      return `✓ Model '${args.model}' is available. To switch, use: /models and select '${args.model}'`
    } catch (error) {
      return `Error connecting to LiteLLM: ${error}`
    }
  },
})

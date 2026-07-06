import { tool } from "@mimocode/cli/plugin"

export default tool({
  description: "Trigger n8n workflow automation via webhook",
  args: {
    workflow: tool.schema.string().describe("Workflow name (post-commit-tests, health-monitor, session-summary, git-notifier)"),
    data: tool.schema.record(tool.schema.any()).optional().describe("Data to send to the workflow"),
  },
  async execute(args) {
    const n8nURL = process.env.N8N_URL || "http://localhost:5678"
    const webhookPath = args.workflow

    const webhookURL = `${n8nURL}/webhook/${webhookPath}`

    try {
      const response = await fetch(webhookURL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(args.data || {}),
        signal: AbortSignal.timeout(10000),
      })

      if (!response.ok) {
        if (response.status === 404) {
          return `Error: Workflow '${args.workflow}' not found. Available workflows:\n- post-commit-tests\n- health-monitor\n- session-summary\n- git-notifier\n\nImport workflows from: components/mimo/n8n-workflows/`
        }
        return `Error: n8n returned ${response.status}`
      }

      const result = await response.json() as any

      return `✓ Workflow '${args.workflow}' triggered successfully\n\nResult:\n${JSON.stringify(result, null, 2)}`
    } catch (error) {
      return `Error connecting to n8n at ${n8nURL}: ${error}\n\nMake sure n8n is running: docker ps | grep n8n`
    }
  },
})

import { tool } from "@mimocode/cli/plugin"
import { exec } from "child_process"
import { promisify } from "util"

const execAsync = promisify(exec)

export default tool({
  description: "Execute a platform workflow (e.g., create-fastapi-project, review-pr)",
  args: {
    workflow: tool.schema.string().describe("Workflow name (e.g., create-fastapi-project, review-pr, generate-tests)"),
    args: tool.schema.string().optional().describe("Workflow arguments as JSON string"),
  },
  async execute(args) {
    const platformRoot = process.env.AI_WORKSTATION_ROOT || process.cwd()
    const workflowPath = `${platformRoot}/workflows/${args.workflow}.yaml`

    try {
      const { stdout } = await execAsync(`cat ${workflowPath}`)
      const lines = stdout.split("\n")

      const name = lines.find(l => l.startsWith("name:"))?.replace("name:", "").trim() || args.workflow
      const description = lines.find(l => l.startsWith("description:"))?.replace("description:", "").trim() || ""
      const model = lines.find(l => l.startsWith("model_recommended:"))?.replace("model_recommended:", "").trim() || "claude-sonnet-4-20250514"

      const stepsStart = lines.findIndex(l => l.trim() === "steps:")
      const steps = lines
        .slice(stepsStart + 1)
        .filter(l => l.trim().startsWith("- name:"))
        .map(l => l.replace("- name:", "").trim())

      const output = [
        `# Workflow: ${name}`,
        ``,
        `**Description:** ${description}`,
        `**Recommended Model:** ${model}`,
        ``,
        `## Steps`,
        ...steps.map((s, i) => `${i + 1}. ${s}`),
        ``,
        `To execute this workflow, follow these steps in order.`,
        args.args ? `\n**Arguments:** ${args.args}` : "",
      ].join("\n")

      return output
    } catch (error) {
      const availableWorkflows = [
        "create-fastapi-project",
        "create-scraper",
        "review-pr",
        "generate-tests",
        "create-rag",
        "debug-python",
      ]
      return `Workflow '${args.workflow}' not found.\n\nAvailable workflows:\n${availableWorkflows.map(w => `- ${w}`).join("\n")}`
    }
  },
})

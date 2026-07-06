import { tool } from "@mimocode/cli/plugin"
import { readFileSync, writeFileSync, existsSync } from "fs"
import { join } from "path"

export default tool({
  description: "Manage project memory: read, write, search, and clean MEMORY.md",
  args: {
    action: tool.schema.enum(["read", "write", "search", "clean"]).describe("Action to perform on memory"),
    content: tool.schema.string().optional().describe("Content to write (for write action)"),
    query: tool.schema.string().optional().describe("Search query (for search action)"),
  },
  async execute(args, context) {
    const memoryPath = join(context.directory, "MEMORY.md")

    switch (args.action) {
      case "read": {
        if (!existsSync(memoryPath)) {
          return "MEMORY.md not found. Create it with: /memory write"
        }
        const content = readFileSync(memoryPath, "utf-8")
        return `# Project Memory\n\n${content}`
      }

      case "write": {
        if (!args.content) {
          return "Error: content required for write action"
        }
        writeFileSync(memoryPath, args.content, "utf-8")
        return `✓ Memory saved to MEMORY.md (${args.content.length} chars)`
      }

      case "search": {
        if (!args.query) {
          return "Error: query required for search action"
        }
        if (!existsSync(memoryPath)) {
          return "MEMORY.md not found"
        }
        const content = readFileSync(memoryPath, "utf-8")
        const lines = content.split("\n")
        const matches = lines.filter(line =>
          line.toLowerCase().includes(args.query!.toLowerCase())
        )
        if (matches.length === 0) {
          return `No matches found for: "${args.query}"`
        }
        return `Found ${matches.length} matches:\n\n${matches.join("\n")}`
      }

      case "clean": {
        if (!existsSync(memoryPath)) {
          return "MEMORY.md not found"
        }
        const content = readFileSync(memoryPath, "utf-8")
        const lines = content.split("\n")
        const cleaned = lines
          .filter(line => line.trim().length > 0)
          .filter(line => !line.startsWith("<!-- outdated"))
        const removed = lines.length - cleaned.length
        writeFileSync(memoryPath, cleaned.join("\n"), "utf-8")
        return `✓ Cleaned memory: removed ${removed} empty/outdated lines`
      }

      default:
        return `Unknown action: ${args.action}`
    }
  },
})

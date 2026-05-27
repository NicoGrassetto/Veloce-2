---
name: todo
description: Use this skill whenever the user asks to create, read, update, complete, delete, search, prioritize, schedule, or summarize tasks, todos, to-dos, reminders, projects, sections, comments, labels, or task assignments. Trigger for phrases like "add a task", "what's on my todo list", "remind me to...", "create a project", "mark this done", "list my overdue tasks", "plan my day", or any request involving Todoist, Linear, GitHub Issues, TickTick, Microsoft To Do, Notion tasks, or any other todo / task management service.
---

# Todo List Skill

## Purpose

Handle todo and task management requests safely and clearly, including:
- Creating, updating, completing, and deleting tasks
- Listing tasks for today, this week, overdue, or by filter
- Organizing tasks into projects, sections, and labels
- Setting priorities, due dates, deadlines, durations, and reminders
- Assigning tasks to collaborators
- Searching and summarizing tasks, projects, and activity
- Planning a day or week from existing tasks

## First Step: Detect Integration Availability

Before attempting any todo operation, determine whether a concrete todo integration is already implemented and available in the current environment.

Always perform this sequence:
1. Identify the user's preferred todo provider (Todoist, Linear, GitHub Issues, TickTick, Microsoft To Do, Notion tasks, or other).
2. Check local MCP availability for that provider in the current environment, starting with `.vscode/mcp.json` and any built-in MCP tools already exposed.
3. If no local MCP is available, check internet availability for a provider MCP (official docs, provider repos, or trusted MCP registries).
4. If an MCP exists and is not already configured locally, install and configure it in this repository first, then use it.
5. If no MCP exists, continue with non-MCP integration checks and fallback behavior.

If the user has not selected a provider yet, ask for the preferred provider first, then run the same local-plus-internet MCP checks for that selected provider.

Treat provider MCP as available only when one of these is true:
- A configured MCP server in the workspace clearly supports the selected provider (for example, a `todoist` entry in `.vscode/mcp.json`).
- A known built-in MCP tool in the current toolset supports the selected provider (for example, `mcp_doist_todoist_*` tools for Todoist).
- The user confirms an already connected MCP todo service for that provider.
- A trusted internet source confirms a provider MCP exists and can be installed in this environment.

When an MCP is internet-discoverable but not yet installed, treat installation as the default next action rather than merely suggesting it. Prefer official provider docs or the provider's repository, then trusted MCP registries. Install the MCP into this repo's workspace configuration so later todo requests can use it directly.

Treat integration as available only when one of these is true:
- There are explicit workspace tools / APIs already wired for todo operations.
- The project contains verified code or configuration for a todo provider and credentials flow.
- The user explicitly confirms an existing connected todo service in this session.

If none of the above is true, integration is **not implemented**.

## Required Fallback Behavior (No Integration)

When todo integration is not implemented, do not pretend to access a task list.

Ask the user this exact clarifying question (or equivalent wording):

"I don't have a todo service connected yet. Which one do you want to use: Todoist, Linear, GitHub Issues, TickTick, Microsoft To Do, Notion, or another provider?"

Then continue based on the user choice:
- If they pick a provider, first check local MCP availability, then internet MCP availability, then install and configure a provider MCP in this repo when one exists.
- If they are unsure, recommend Todoist as the default, since this repo is already wired for it.
- If they only need planning help without integration, provide a manual task list draft.

If an installable provider MCP is found online, the agent should:
1. Verify the source is trustworthy (official provider repo, provider docs, or well-known maintainer).
2. Add the MCP server configuration to the repo workspace in `.vscode/mcp.json`.
3. Take care of every setup step the agent can do unattended.
4. Only ask the user for actions the agent cannot perform itself, such as: completing browser OAuth, copying a personal API token into a secret store, creating an OAuth application in the provider's developer console, or granting workspace permissions.
5. When the user must act, give a short numbered checklist with exact links and field names so the user can complete it without hunting for information.

## Operating Rules

When the integration is available, follow these rules:

- **Confirm scope on ambiguous bulk actions.** Do not delete, complete in bulk, reassign in bulk, or modify recurring tasks without an explicit confirmation when the action affects more than a handful of items.
- **Preserve recurrence.** When rescheduling a recurring task, use the provider's reschedule operation, not a full due-date overwrite, so the recurrence rule survives.
- **Respect priorities and labels.** Use the provider's native priority and label format. For Todoist, priorities are `p1` (highest) to `p4` (default), as strings.
- **Use natural-language dates when supported.** Prefer phrases like "today", "tomorrow", "next Monday", or ISO dates the provider accepts, and respect the user's timezone.
- **Search before mutating.** When the user references a task by name, find it first, show the candidates, then act on the chosen one. Do not guess silently.
- **Summaries first, action second.** For planning and review requests, present a short summary of the relevant tasks before proposing changes.
- **Stay within scope.** Do not create projects, labels, or filters the user did not ask for.

## Recommended Workflows

- **Add a task:** capture title, optional project, due date, priority, and labels, then create with one call.
- **Daily review:** list today plus overdue, group by project, then ask which to reschedule, complete, or drop.
- **Weekly plan:** list the next seven days, surface overloaded days, and suggest moves.
- **Project cleanup:** list a project, group by status, propose archive or completion candidates.
- **Triage from external input:** turn an email, message, or note into one or more tasks with sensible defaults and confirm before creating more than a few.

## Provider Notes

- **Todoist:** uses the `mcp_doist_todoist_*` tool family. Prefer `reschedule-tasks` over `update-tasks` when changing due dates so recurring tasks keep their schedule. Use `find-project-collaborators` to resolve user names to IDs before assigning.
- **Linear:** if selected, install a Linear MCP server and authenticate with a workspace API key or OAuth app.
- **GitHub Issues:** if selected, prefer an existing GitHub MCP server and reuse the repository's auth.
- **TickTick, Microsoft To Do, Notion tasks, others:** check for an official or well-maintained community MCP server before falling back to manual planning.

## Verification

Before reporting a todo action as done:
1. Confirm the provider returned a success result, including the new or updated task ID.
2. Echo back the final task content, due date, priority, and project so the user can spot mistakes immediately.
3. For bulk operations, report counts of created, updated, completed, or skipped items.

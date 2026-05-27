---
name: calendar
description: Use this skill whenever the user asks to create, read, update, delete, list, reschedule, or summarize calendar events, meetings, reminders, or availability. Trigger for phrases like "check my calendar", "schedule a meeting", "move this event", "find free time", "send an invite", or any request involving Google Calendar, Microsoft Outlook/Office 365, Apple Calendar, ICS, or other calendar services.
---

# Calendar Interaction Skill

## Purpose

Handle calendar-related user requests safely and clearly, including:
- Creating events and reminders
- Listing upcoming events
- Updating, rescheduling, or cancelling events
- Checking availability / finding time slots
- Summarizing daily or weekly schedules

## First Step: Detect Integration Availability

Before attempting calendar operations, determine whether a concrete calendar integration is already implemented and available in the current environment.

Always perform this sequence:
1. Identify the user's preferred calendar provider (Google, Outlook, Apple, or other).
2. Check local MCP availability for that provider in the current environment.
3. If no local MCP is available, check internet availability for a provider MCP (official docs, provider repos, or trusted MCP registries).
4. If MCP exists (local or internet-discoverable and installable), use or propose the MCP path first.
5. If MCP does not exist, continue with non-MCP integration checks and fallback behavior.

If the user has not selected a provider yet, ask for the preferred provider first, then run the same local-plus-internet MCP checks for that selected provider.

Treat provider MCP as available only when one of these is true:
- A configured MCP server in the workspace clearly supports the selected provider.
- A known built-in MCP tool in the current toolset supports the selected provider.
- The user confirms an already connected MCP calendar service for that provider.
- A trusted internet source confirms a provider MCP exists and can be installed in this environment.

Treat integration as available only when one of these is true:
- There are explicit workspace tools/APIs already wired for calendar operations.
- The project contains verified code/configuration for a calendar provider and credentials flow.
- The user explicitly confirms an existing connected calendar service in this session.

If none of the above is true, integration is **not implemented**.

## Required Fallback Behavior (No Integration)

When calendar integration is not implemented, do not pretend to access a calendar.

Ask the user this exact clarifying question (or equivalent wording):

"I don't have a calendar service connected yet. Which calendar do you want to use: Google Calendar, Microsoft Outlook, Apple Calendar, or another provider?"

Then continue based on the user choice:
- If they pick a provider, first check local MCP availability, then internet MCP availability, then propose next setup steps for that provider.
- If they are unsure, offer a short comparison and recommend one.
- If they only need planning help without integration, provide a manual schedule draft.

## Interaction Rules

- Never claim to have read or modified events unless a real integration/tool call confirms it.
- For ambiguous requests, confirm key fields: title, date, start time, end time, timezone, attendees, location, recurrence.
- Ask for timezone whenever it is missing and timing matters.
- Prefer concise confirmations before destructive actions (delete/cancel).
- For recurring events, confirm recurrence rule changes explicitly.

## Output Format

When proposing or confirming calendar actions, present a compact summary:
- Action: create/update/delete/list
- Title
- Date and time (with timezone)
- Attendees
- Location / meeting link
- Recurrence (if any)
- Status: planned, needs confirmation, or completed

## Example Prompts That Should Trigger

- "Check my calendar for tomorrow afternoon."
- "Schedule a 30-minute sync with Alex next Tuesday."
- "Move my 3 PM design review to 4 PM."
- "What free slots do I have this week?"
- "Cancel Friday's standup."

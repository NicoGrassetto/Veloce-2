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
- If they pick a provider, propose next setup steps for that provider.
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

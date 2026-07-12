# Interrupt Me Later

Interrupt Me Later is a simple productivity website that helps users pick up where they left off after an interruption.

Before stepping away, users can save what they were working on, what they already finished, what is blocking them, and what they planned to do next. The website then turns that information into a clear restart card for later.

## The Problem

Interruptions do not only take away time. They also make it harder to remember what you were thinking, where you stopped, and what you were about to do next.

Interrupt Me Later saves that mental context so users can return to their work without having to reconstruct everything.

## Features

- Save current work progress
- Record blockers and unfinished tasks
- Detect relevant file names
- Identify completed work
- Generate a short restart plan
- Choose between a quick restart and a detailed recap
- View previous saved sessions
- Delete old checkpoints
- Works without a paid AI API

## How It Works

1. Enter the name of your project.
2. Paste notes about what you are currently working on.
3. Add an optional blocker or planned next step.
4. Press **Pause Session**.
5. Return later and open the saved restart card.

The website looks for phrases related to completed work, errors, next steps, questions, and file names. It then organizes them into a structured checkpoint.

## Example

### Input

```text
I am building a hackathon website in app.py. I finished the homepage and added the form. The save button is connected, but the session data is not appearing in history. Next I need to check whether storage.py is writing to sessions.json.

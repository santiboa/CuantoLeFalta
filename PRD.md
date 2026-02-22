# 📝 Product Requirements Document

**Project Name:** Cuánto Le Falta  
**Owner:** Santiago Padilla  
**Primary Platform:** X (Twitter) Bot  
**Hosting:** PythonAnywhere  

---

# 1️⃣ Core Product – The Bot (Primary Product)

## 🎯 Purpose

Cuánto Le Falta is a minimalist Twitter bot that posts the exact remaining time until the end of the current Mexican president’s term. It simply counts down. That simplicity is the brand.

---

## 🧠 What It Does

### ⏳ Countdown Logic

- Calculates the time difference between:
  - **Current date (Mexico City timezone)**
  - **October 1, 2030 – 00:00:00 (Mexico City time)**

- Outputs:
  - Days
  - Hours
  - Minutes
  - Seconds

### 🐦 Posting Behavior

- Posts at randomized intervals (within defined constraints).
- Message format remains extremely consistent.
- Core structure example:

"Le faltan X años, Y meses, Z días, A horas, B minutos, C segundos (o bien, N días).  Ya pasó XX.XXX% del sexenio (M días). #cuantolefalta"

The default mode remains pure countdown.

---

# 2️⃣ Tone Strategy – Neutral but Provocative

The bot’s power comes from tension.

It does not state an opinion.
But the act of counting down is inherently loaded.

### Core Principle

Provocation comes from:
- Timing
- Minimal wording
- Milestones
- Contrast
- Rhythm

Not from insults or commentary.

---

## 🎭 Acceptable Provocative Variations

Occasionally, the bot may use minimal, sharpened formats such as:
Key milestones and round numbers:
- "Ya paso XX.000% del sexenio."
- "Faltan exactamente 2 años y 6 meses"
- “Faltan 1000 días.”
- “Faltan 500.”
- “Ya son menos de 365 días.”
- “Últimos 100 días.”

---

## 🚫 What We want to explore eventually

- Commentary about policies
- Editorialization
- Reactions to key news

---

# 3️⃣ Technical Architecture

## 🛠 Stack

| Layer | Tool |
|-------|------|
| Language | Python |
| Hosting | PythonAnywhere |
| Scheduler | PythonAnywhere scheduled task |
| API | X / Twitter API v2 |
| Timezone Handling | Mexico City timezone (TBC) |

---

## 🔁 Execution Flow

1. Script calculates time remaining.
2. Determines tweet format (default or milestone variation).
3. Formats tweet.
4. Sends tweet via API.
5. Logs result.
6. Waits until next execution.

---

# 4️⃣ Hosting – PythonAnywhere

## Current Setup

- Hosted as a scheduled Python script, always running but sleeping.
- Runs automatically at defined intervals.
- Uses environment variables for API credentials.
- No database required.
- Lightweight and inexpensive.

## Reliability Priorities

1. Timezone correctness (Mexico City).
2. No duplicate tweets.
3. Error handling for API rate limits.
4. Logging for visibility.
5. Clear format control (avoid accidental tone drift).

---

# 5️⃣ Brand & Positioning

Cuánto Le Falta is:

- Simple
- Repetitive
- Predictable
- Shareable
- Slightly unsettling in its consistency

The repetition creates cultural presence.

The silence creates tension.

We protect that.

---

# 6️⃣ Future Potential Builds (Exploration Only)

These are ideas. Not current roadmap.

---

## 🌐 A. Lightweight Website Companion

Purpose:
- Display live countdown.
- Embed latest tweet.
- Act as a central hub.

Possible Features:
- Real-time countdown clock.
- Embedded tweet.
- Tweet intent button.
- Optional donation button.
- Very minimal design.

Hosting options:
- Flask app on PythonAnywhere
- Static site

---

## 🧠 B. Structured Milestone System

Instead of reacting to daily news, we can predefine:

- 1000 days
- 750 days
- 500 days
- 365 days
- 300 days
- 200 days
- 100 days
- 50 days
- 30 days
- 10 days
- 5 days
- 1 day

These become controlled “intensity spikes.”

No improvisation.
No reactive tweeting.
All predefined.

---

## 🛍 C. Merch / Store

If the account grows organically:

Possible items:
- Minimalist shirts (“Faltan X días”)
- Stickers
- Mugs

Only pursue if:
- Demand emerges naturally.
- Engagement is sustained long term.

---

## 📊 D. Data Layer (Optional Advanced Concept)

- Archive every tweet.
- Track engagement over time.
- Visualize follower growth.
- Analyze which formats perform best.

Only useful if scale increases significantly.

---

# 7️⃣ Product Philosophy

This is not commentary.
This is not debate.
This is not activism.

It is a clock.

But a clock, when placed in the right context, becomes powerful.

---

# 8️⃣ Current Focus

1. Keep the bot stable.
2. Protect tone discipline.
3. Ensure scheduling reliability.
4. Avoid overbuilding.

Everything else is optional.
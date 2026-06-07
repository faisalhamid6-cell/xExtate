# Mnemo Demo Report

_An organization that teaches itself — run summary._

## Metrics

| Metric | Value |
|--------|-------|
| KB size before | 6 active articles |
| KB size after | 5 active articles |
| Questions asked | 4 |
| Instant answers | 2 |
| Newly learned | 1 |
| Flagged (gate blocked) | 1 |
| Instant-Answer Rate | 50% |
| Intelligence Score | 75 |

## What happened, question by question

**Q1: How do I create and send an invoice in Billy?**

- Outcome: ✅ INSTANT cited answer (already known)
- Source: Article #1
- Confidence: 0.84
- Answer: To create an invoice in Billy, click 'New Invoice', pick a customer, add line items, then press Send. Billy emails the invoice as a PDF and tracks when the customer opens it.

**Q2: How do I set up recurring invoices in Billy?**

- Outcome: 🧠 LEARNED — resolved a new answer and saved it to the KB
- Source: Article #7
- Confidence: 0.81
- Answer: Based on related knowledge in 'How to create and send an invoice in Billy': To handle "How do I set up recurring invoices in Billy", open Billy, go to Settings, and follow the relevant section. This article was auto-resolved by Mnemo. (Synthesized from Article #1.)

**Q3: How do I set up recurring invoices in Billy?**

- Outcome: ✅ INSTANT cited answer (already known)
- Source: Article #7
- Confidence: 0.81
- Answer: Based on related knowledge in 'How to create and send an invoice in Billy': To handle "How do I set up recurring invoices in Billy", open Billy, go to Settings, and follow the relevant section. This article was auto-resolved by Mnemo. (Synthesized from Article #1.)

**Q4: What is the weather like in Tokyo today?**

- Outcome: 🚧 BLOCKED by confidence gate — flagged for human review
- Source: needs human review
- Confidence: 0.40
- Answer: Tentative answer: To handle "What is the weather like in Tokyo today", open Billy, go to Settings, and follow the relevant section. This article was auto-resolved by Mnemo. (No supporting article was found, so this is unverified.)

## Self-healing pass

- 🔗 Merged Article #4 into #3 (similarity 0.88).
- ⏳ Flagged stale Article #6 (created 2024-06-01).

## Why this matters

Every miss that Mnemo confidently resolves becomes a new article, so the **Instant-Answer Rate climbs over time** and the team self-serves more. The **confidence gate** keeps low quality answers out, and the **healer** stops the library from rotting with duplicates and stale pages.

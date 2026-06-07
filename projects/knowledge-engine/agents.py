"""
agents.py — The crew of agents that make Mnemo "an organization that teaches
itself."

There are four small agents, each with ONE clear job:

  🔎 LibrarianAgent — searches the knowledge base for an answer.
  ✍️ ResolverAgent  — answers from a found article, OR resolves a brand-new
                      answer and (only if confident) writes it back to the KB.
  🩹 HealerAgent    — cleans the KB: merges duplicates, flags stale articles,
                      and flags likely contradictions.
  🧑‍🏫 CuratorAgent  — the lead. Orchestrates the others and tracks the metrics
                      (Instant-Answer Rate, KB size, Intelligence Score).

Everything here is deterministic and uses only the standard library, so the
demo gives the same result every run.
"""

from datetime import date

from kb import KnowledgeBase, cosine_similarity, _vector


# ---------------------------------------------------------------------------
# Tuned thresholds (chosen so the scripted demo behaves the same every run)
# ---------------------------------------------------------------------------

# If the best search score is >= this, we trust the KB already has the answer
# and give an INSTANT cited answer.
ANSWER_THRESHOLD = 0.30

# When we have to resolve a NEW answer, we only WRITE it to the KB if our
# self-assessed confidence is >= this. This is the "confidence gate" that
# stops the KB from learning garbage.
WRITE_THRESHOLD = 0.60

# Healing knobs.
DUPLICATE_THRESHOLD = 0.85   # two articles this similar are near-duplicates
STALE_BEFORE_DATE = "2025-01-01"  # articles older than this are "stale"


class LibrarianAgent:
    """🔎 Finds the most relevant article(s) for a question."""

    def __init__(self, kb: KnowledgeBase, llm):
        self.kb = kb
        self.llm = llm

    def retrieve(self, question: str, k: int = 3):
        """
        Search the KB and return (results, confidence).

        `results` is a list of (Article, score). `confidence` is the top score
        — how sure we are that the answer is already in the library.
        """
        results = self.kb.search(question, k=k)
        confidence = results[0][1] if results else 0.0
        top_title = results[0][0].title if results else "(nothing)"
        print(f"   🔎 Librarian searched the KB. Best match: "
              f"\"{top_title}\" (confidence {confidence:.2f})")
        return results, confidence


class ResolverAgent:
    """✍️ Answers from the KB, or resolves and (carefully) writes new knowledge."""

    def __init__(self, kb: KnowledgeBase, llm):
        self.kb = kb
        self.llm = llm

    def answer(self, question: str, results, confidence: float) -> dict:
        """
        Decide what to do with a question.

        Returns a dict describing the outcome, with an "action" of:
          - "instant"  : answered straight from an existing article (cited)
          - "learned"  : resolved a new answer AND wrote it to the KB
          - "flagged"  : resolved a new answer but the confidence gate BLOCKED
                         the write, so it was flagged for human review instead
        """
        # CASE 1 — the KB already knows. Answer instantly, WITH a citation.
        if confidence >= ANSWER_THRESHOLD and results:
            article = results[0][0]
            print(f"   ✍️ Resolver: confident enough — answering from the KB.")
            print(f"   ✅ INSTANT ANSWER (Source: Article #{article.id})")
            print(f"      → {article.body}")
            return {
                "action": "instant",
                "question": question,
                "answer": article.body,
                "source": f"Article #{article.id}",
                "confidence": confidence,
            }

        # CASE 2 — the KB does NOT know. We must resolve a fresh answer.
        print(f"   ✍️ Resolver: no good match (confidence {confidence:.2f} "
              f"< {ANSWER_THRESHOLD:.2f}). Resolving a NEW answer...")
        new_body, gate_conf = self._resolve(question, results, confidence)

        # CONFIDENCE GATE — only learn it if we're confident it's correct.
        if gate_conf >= WRITE_THRESHOLD:
            article = self.kb.add_article(
                title=question.rstrip("?"),
                body=new_body,
                tags=self._keywords(question),
                source="resolver",
                confidence=round(gate_conf, 2),
                created_at=date.today().isoformat(),
                status="active",
            )
            print(f"   🧠 Self-confidence {gate_conf:.2f} ≥ "
                  f"{WRITE_THRESHOLD:.2f} → WRITING new Article #{article.id} "
                  f"to the KB. It just learned!")
            print(f"      → {new_body}")
            return {
                "action": "learned",
                "question": question,
                "answer": new_body,
                "source": f"Article #{article.id}",
                "confidence": gate_conf,
            }

        # Confidence too low → DO NOT write. Flag for a human instead.
        print(f"   🚧 CONFIDENCE GATE: self-confidence {gate_conf:.2f} < "
              f"{WRITE_THRESHOLD:.2f}.")
        print(f"   🙋 Refusing to learn this — FLAGGED for human review "
              f"(KB stays clean).")
        return {
            "action": "flagged",
            "question": question,
            "answer": new_body,
            "source": "needs human review",
            "confidence": gate_conf,
        }

    # ---- internal helpers ------------------------------------------------

    def _resolve(self, question: str, results, retrieval_conf: float):
        """
        Produce a draft answer plus a self-assessed confidence (0-1).

        In DEMO mode we synthesize a templated article from the question and
        any weak context we retrieved. Our confidence is HIGHER when there was
        at least some weak supporting context, and LOWER when the question is
        a total stranger to the KB. This makes the demo's gate deterministic.

        TODO (live upgrade): replace this template with a Gemini 3 prompt that
        actually answers the question, and use the model's own grounding score
        as the confidence.
        """
        # Pull any weak context (the best partial match, if there is one).
        context_article = results[0][0] if results else None
        context_score = results[0][1] if results else 0.0

        if context_article and context_score > 0.10:
            # We had *some* relevant context to lean on → more confident.
            body = (
                f"Based on related knowledge in '{context_article.title}': "
                f"{self._templated_answer(question)} "
                f"(Synthesized from Article #{context_article.id}.)"
            )
            gate_conf = 0.65 + context_score  # comfortably over the gate
        else:
            # No context at all → an educated guess. Low confidence on purpose.
            body = (
                f"Tentative answer: {self._templated_answer(question)} "
                f"(No supporting article was found, so this is unverified.)"
            )
            gate_conf = 0.40  # below WRITE_THRESHOLD → will be blocked

        return body, min(gate_conf, 0.99)

    def _templated_answer(self, question: str) -> str:
        """A simple, readable stand-in answer built from the question."""
        topic = question.rstrip("?").strip()
        return (f"To handle \"{topic}\", open Billy, go to Settings, and follow "
                f"the relevant section. This article was auto-resolved by Mnemo.")

    def _keywords(self, question: str) -> list:
        """Grab a few useful tag words from the question (skip filler words)."""
        stop = {"how", "do", "i", "can", "the", "a", "an", "to", "in", "is",
                "what", "does", "my", "of", "for", "and", "with", "on"}
        words = _vector(question)
        return [w for w in words if w not in stop and len(w) > 2][:5]


class HealerAgent:
    """🩹 Keeps the KB healthy: merges duplicates, flags stale/contradictions."""

    # Opposing-keyword pairs used for a simple contradiction check.
    CONTRADICTION_PAIRS = [
        ("supported", "not supported"),
        ("available", "unavailable"),
        ("included", "not included"),
        ("yes", "no"),
    ]

    def __init__(self, kb: KnowledgeBase, llm):
        self.kb = kb
        self.llm = llm

    def heal(self) -> dict:
        """
        Run one full cleaning pass and return a report dict.

        TODO (live upgrade): use Gemini for semantic de-duplication and true
        contradiction detection instead of these keyword/similarity rules.
        """
        report = {"merged": [], "stale": [], "contradictions": []}

        active = [a for a in self.kb.articles if a.status == "active"]

        # (a) Near-duplicate detection → MERGE the newer one into the older.
        for i in range(len(active)):
            for j in range(i + 1, len(active)):
                a, b = active[i], active[j]
                if a.status != "active" or b.status != "active":
                    continue
                sim = cosine_similarity(_vector(a.text()), _vector(b.text()))
                if sim >= DUPLICATE_THRESHOLD:
                    # Keep the lower id (older), merge the other into it.
                    keep, drop = (a, b) if a.id <= b.id else (b, a)
                    drop.status = "merged"
                    print(f"   🩹 Found near-duplicate (similarity "
                          f"{sim:.2f}): merged Article #{drop.id} into "
                          f"#{keep.id}.")
                    report["merged"].append(
                        {"kept": keep.id, "merged": drop.id,
                         "similarity": round(sim, 2)})

        # (b) Stale detection → FLAG anything older than the cutoff date.
        for art in self.kb.articles:
            if art.status != "active":
                continue
            if art.created_at and art.created_at < STALE_BEFORE_DATE:
                art.status = "flagged"
                print(f"   🩹 Article #{art.id} is stale (created "
                      f"{art.created_at}) → FLAGGED for review.")
                report["stale"].append(
                    {"id": art.id, "created_at": art.created_at})

        # (c) Contradiction detection → FLAG pairs that talk about the same
        # topic but say opposite things.
        active = [a for a in self.kb.articles if a.status == "active"]
        for i in range(len(active)):
            for j in range(i + 1, len(active)):
                a, b = active[i], active[j]
                topic_sim = cosine_similarity(_vector(a.title), _vector(b.title))
                if topic_sim < 0.30:
                    continue  # not even about the same thing
                if self._contradicts(a.body, b.body):
                    print(f"   🩹 Possible contradiction between Article "
                          f"#{a.id} and #{b.id} → FLAGGED.")
                    report["contradictions"].append({"a": a.id, "b": b.id})

        if not any(report.values()):
            print("   🩹 Healer found nothing to fix — the KB is healthy.")
        return report

    def _contradicts(self, text_a: str, text_b: str) -> bool:
        """True if one body says a positive keyword and the other its opposite."""
        la, lb = text_a.lower(), text_b.lower()
        for positive, negative in self.CONTRADICTION_PAIRS:
            if (positive in la and negative in lb) or \
               (positive in lb and negative in la):
                return True
        return False


class CuratorAgent:
    """🧑‍🏫 The lead orchestrator. Runs the show and tracks the metrics."""

    def __init__(self, kb: KnowledgeBase, llm):
        self.kb = kb
        self.llm = llm
        self.librarian = LibrarianAgent(kb, llm)
        self.resolver = ResolverAgent(kb, llm)
        self.healer = HealerAgent(kb, llm)

        # Live metrics.
        self.questions_asked = 0
        self.instant_answers = 0
        self.learned = 0
        self.flagged = 0
        self.log = []  # full record of every question, for the report

    def ask(self, question: str) -> dict:
        """Handle one question end-to-end and update the metrics."""
        self.questions_asked += 1
        print(f"\n❓ Q{self.questions_asked}: {question}")

        results, confidence = self.librarian.retrieve(question)
        outcome = self.resolver.answer(question, results, confidence)

        if outcome["action"] == "instant":
            self.instant_answers += 1
        elif outcome["action"] == "learned":
            self.learned += 1
        elif outcome["action"] == "flagged":
            self.flagged += 1

        self.log.append(outcome)
        return outcome

    # ---- metrics ---------------------------------------------------------

    def instant_answer_rate(self) -> float:
        """Percent of questions answered instantly from the KB."""
        if self.questions_asked == 0:
            return 0.0
        return 100.0 * self.instant_answers / self.questions_asked

    def intelligence_score(self) -> int:
        """
        A single feel-good number that climbs as the system learns.

        = (active KB size × 10) + (instant answers × 5) + (learned × 15)
        Bigger, smarter library and more self-service = higher score.
        """
        return (self.kb.count_active() * 10
                + self.instant_answers * 5
                + self.learned * 15)

    def dashboard(self, title: str) -> None:
        """Print a small, watchable metrics panel."""
        print(f"\n📊 {title}")
        print(f"   • KB size (active articles): {self.kb.count_active()}")
        print(f"   • Questions asked:           {self.questions_asked}")
        print(f"   • Instant answers:           {self.instant_answers}")
        print(f"   • Instant-Answer Rate:       "
              f"{self.instant_answer_rate():.0f}%")
        print(f"   • Intelligence Score:        {self.intelligence_score()}")

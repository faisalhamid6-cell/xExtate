"""
kb.py — The Knowledge Base: where Mnemo stores everything it knows.

Plain-English idea
------------------
Think of this as a simple library of short articles, saved in one JSON file on
disk (`data/kb.json`). Each article has a title, a body, some tags, and a few
bookkeeping fields (when it was created, how confident we are, and whether it
is still "active").

The one clever bit is `search()`. It finds the articles most relevant to a
question using "cosine similarity" over a bag of words. In plain English:
we count the words in the question and the words in each article, then measure
how much their word-clouds overlap. A score of 1.0 means "basically identical
wording", 0.0 means "no words in common". No AI or internet needed.

TODO (live upgrade): replace this word-counting search with MongoDB Atlas
$vectorSearch using Gemini embeddings. The method signature stays the same, so
nothing else in the app has to change.
"""

import json
import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field, asdict
from datetime import date


# Common filler words. We drop these before searching so that two texts only
# look similar when they share MEANINGFUL words, not just "the" and "in".
STOPWORDS = {
    "the", "a", "an", "to", "in", "is", "are", "of", "for", "and", "or",
    "with", "on", "at", "it", "this", "that", "i", "you", "my", "your",
    "how", "do", "does", "can", "what", "which", "when", "where", "why",
    "be", "as", "by", "from", "into", "like", "today", "please",
}


# We resolve all paths relative to THIS file, so the demo works no matter what
# folder you run it from.
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
DEFAULT_KB_PATH = os.path.join(DATA_DIR, "kb.json")


@dataclass
class Article:
    """One unit of knowledge. Maps 1:1 to a future MongoDB document."""

    id: int
    title: str
    body: str
    tags: list = field(default_factory=list)
    source: str = "unknown"
    created_at: str = ""              # ISO date, e.g. "2026-06-01"
    confidence: float = 1.0           # 0.0 - 1.0, how sure we are it's correct
    status: str = "active"            # "active" | "merged" | "flagged"

    def text(self) -> str:
        """All the searchable words of this article in one string."""
        return f"{self.title} {self.body} {' '.join(self.tags)}"


# ---------------------------------------------------------------------------
# Tiny text helpers (these are what a search engine does under the hood)
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list:
    """Lower-case the text, split into words, and drop common filler words."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS]


def _vector(text: str) -> Counter:
    """Turn text into a word-count 'vector' (a bag of words)."""
    return Counter(_tokenize(text))


def cosine_similarity(a: Counter, b: Counter) -> float:
    """
    Measure how similar two word-clouds are, from 0.0 (nothing in common)
    to 1.0 (identical wording). This is the classic 'cosine similarity'.
    """
    if not a or not b:
        return 0.0
    # Dot product: for every shared word, multiply the two counts and add up.
    shared = set(a) & set(b)
    dot = sum(a[word] * b[word] for word in shared)
    # Magnitudes: the 'length' of each word-cloud.
    mag_a = math.sqrt(sum(v * v for v in a.values()))
    mag_b = math.sqrt(sum(v * v for v in b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


class KnowledgeBase:
    """A small library of articles backed by a JSON file."""

    def __init__(self, path: str = DEFAULT_KB_PATH):
        self.path = path
        self.articles = []  # list[Article]

    # ---- persistence -----------------------------------------------------

    def load(self, path: str = None) -> "KnowledgeBase":
        """Read articles from a JSON file into memory."""
        path = path or self.path
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.articles = [Article(**item) for item in raw]
        return self

    def save(self, path: str = None) -> None:
        """Write all articles back to disk as pretty JSON."""
        path = path or self.path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump([asdict(a) for a in self.articles], f, indent=2)

    # ---- reading ---------------------------------------------------------

    def count_active(self) -> int:
        """How many articles are currently live (not merged/flagged)?"""
        return sum(1 for a in self.articles if a.status == "active")

    def next_id(self) -> int:
        """Pick the next free id number."""
        return (max((a.id for a in self.articles), default=0)) + 1

    def search(self, query: str, k: int = 3) -> list:
        """
        Find the top-k most relevant ACTIVE articles for a question.

        Returns a list of (Article, score) tuples, best score first. The score
        of the very first result is what we call the "retrieval confidence":
        how sure the Librarian is that the KB already contains the answer.

        TODO (live upgrade): swap this cosine search for MongoDB Atlas
        $vectorSearch over Gemini embeddings of `Article.text()`.
        """
        q_vec = _vector(query)
        scored = []
        for art in self.articles:
            if art.status != "active":
                continue  # ignore merged/flagged articles
            score = cosine_similarity(q_vec, _vector(art.text()))
            scored.append((art, score))
        # Sort by score, highest first.
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:k]

    # ---- writing ---------------------------------------------------------

    def add_article(self, title, body, tags=None, source="resolver",
                    confidence=1.0, created_at=None, status="active") -> Article:
        """Create a new article, add it to the library, and return it."""
        art = Article(
            id=self.next_id(),
            title=title,
            body=body,
            tags=tags or [],
            source=source,
            created_at=created_at or date.today().isoformat(),
            confidence=confidence,
            status=status,
        )
        self.articles.append(art)
        return art

    def get(self, article_id: int):
        """Look up one article by its id (or None if not found)."""
        for a in self.articles:
            if a.id == article_id:
                return a
        return None

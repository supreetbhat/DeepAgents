# python/m4/m4.3_homework.py
"""M4.3 Homework: Write Your Own Dynamic Subagent Workflow.

THE IDEA
The lab gave the main agent a 2MB manuscript split into labeled books and
had it write a "workflow" that dispatched one book-scanner subagent per
book, so the full corpus never entered the main model's own context. This
homework asks you to do the same shape of thing on a scenario of your own
choosing: a synthetic corpus of your own, split into your own labeled
sections, and a subagent that scans each section for something other than
anachronisms.

A few starting points, if you want one:
  - A Sherlock Holmes story, split by chapter, scanned for clues the
    detective mentions but never actually explains.
  - The script of Bee Movie or Shrek, split by scene, scanned for lines
    that don't match the character who supposedly says them.
  - Your own corrupted classic, like the lab's, but seeded with a
    different kind of error: wrong units, swapped character names,
    continuity errors between chapters.

WHAT YOU FILL IN
  TODO 1: write your own corpus, a single string split into at least 5
    labeled sections using a consistent header format (like the lab's
    "=== EPIC BOOK N ===").
  TODO 2: write the section-scanner's system prompt (what should it flag in
    one section?) and the main agent's system prompt (telling it to run a
    workflow that splits your corpus and dispatches one scanner call per
    section).

RUN
  cd python
  uv run ./m4/m4.3_homework.py

NOTE
  This uses the code interpreter (langchain_quickjs), same as the lab. Make
  sure you've run `uv sync` from python/ so it's installed.
"""

from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_quickjs import CodeInterpreterMiddleware

from models import model, strong_model

DATA_DIR = Path(__file__).resolve().parent / "homework_data"
DATA_DIR.mkdir(exist_ok=True)
CORPUS_PATH = DATA_DIR / "my_corpus.txt"


# ════════════════════════════════════════════════════════════════════════
# TODO 1: Write your own corpus.
#
# Requirements:
#   - A single string with at least 5 labeled sections.
#   - Pick a consistent header format, e.g. "=== SECTION N ===" or
#     "=== TICKET N ===", and stick to it exactly: the main agent's prompt
#     (TODO 2) needs to describe the same format so it can split on it.
#   - Plant something worth finding in a few of the sections (an off-topic
#     sentence, a specific keyword, whatever your scanner in TODO 2 is
#     looking for) so there's something for the workflow to actually
#     surface.
#
# Example shape (delete this and write your own):
#   return """\
#   === SECTION 1 ===
#   ...
#
#   === SECTION 2 ===
#   ...
#   """
# ════════════════════════════════════════════════════════════════════════

def build_corpus() -> str:
    """TODO 1: return your own corpus string with at least 5 sections."""
    return """\
=== CHAPTER 1 ===
The Adventure of the Silent Clockmaker

It was a raw November morning when Mrs. Eleanor Hartley was shown up to our
rooms in Baker Street. She was a slight woman of perhaps forty, dressed in
grey, and she clutched her reticule as though it held the last of her
courage.

"You came by the river ferry from Southwark, not by cab," said Holmes,
before she had so much as taken a chair. "There is fresh tar upon the hem
of your skirt, of the sort they paint on the ferry benches each autumn, and
the spray has spotted your left sleeve but not your right, so you sat at
the starboard rail facing the city."

Mrs. Hartley stared at him, then nodded. "My brother Edmund is missing,
Mr. Holmes. He keeps a clock shop in Clerkenwell. Three days ago he locked
the door at six, as he always does, and he has not been seen since."

Holmes glanced once at her gloved left hand and leaned back. "And the key
was never in the lock, I perceive. Pray continue."

She did not ask him how he knew, and he did not say. She told us that the
police had found the shop undisturbed, the till untouched, and her
brother's hat still upon its peg.

=== CHAPTER 2 ===
The shop of Edmund Hartley stood in a narrow lane off St. John Street, its
window crowded with brass carriage clocks and a tall longcase clock in
walnut. Inspector Lestrade met us at the door with the air of a man who has
already decided the matter is a waste of everyone's time.

"Run off from his debts, Mr. Holmes. Plain as day."

Holmes said nothing. He walked the length of the shop twice. Every clock
in the place had stopped, and every one of them showed seventeen minutes
past four.

"Curious," I remarked.

"Very," said Holmes. He crossed to the back window and, bending low,
pinched a few grains of something from the sill between finger and thumb.
It was sand, of a pale and unmistakable blue. He studied it under his lens
for a long moment, then brushed it into an envelope.

"That settles the matter of the second visitor," he said quietly, and
would say no more about it, then or later.

Lestrade snorted. "Second visitor? There's been no one here but the
clockmaker and his apprentice."

"Then we had best speak to the apprentice," said Holmes.

=== CHAPTER 3 ===
The apprentice, a lanky youth named Tobias Crane, lodged above a
chandler's shop two streets away. He received us nervously, wiping his
hands upon his trousers.

"You have been filing brass this morning, and not for your master," said
Holmes. "The fine yellow dust is still in the creases of your right hand,
and the shop has been closed by the police these three days, so the work
was done here, at your own bench."

Crane flushed. "A bit of private work, sir. Mending a watch for my
landlady. There's no harm in it."

"None at all," said Holmes pleasantly. He asked the lad a dozen questions
about his master's habits: when he rose, where he dined, whom he owed. On
the way down the stairs he paused beside a cage in which a small yellow
canary sat silent on its perch.

"The canary sang on Tuesday, Watson," he murmured. "Remember that."

I waited for him to explain, but he only lit his pipe and strode out into
the street, and I confess I have never understood what he meant by it.

=== CHAPTER 4 ===
That night Holmes and I kept watch at the Brewer's Quay, for Holmes had
learned from Crane that Edmund Hartley owed a considerable sum to a
moneylender named Josiah Marsh, whose warehouse backed onto the river.

The fog came up thick after midnight. We crouched behind a stack of
barrels for the better part of three hours, listening to the slap of the
tide against the pilings. At a little after three a lantern appeared at
the warehouse door, and a stout man, whom Holmes identified in a whisper
as Marsh himself, carried a small wooden crate down to a waiting skiff.

"Clock parts," Holmes breathed. "Hartley's finest movements. Marsh has
been taking them in payment of the debt, a few at a time, which is why the
display window looked so crowded and the workshop shelves so bare."

We followed the skiff along the bank as far as Wapping Stairs, where Marsh
handed the crate to a second man and rowed back alone. Holmes was well
satisfied, and we returned to Baker Street as the sky began to pale.

=== CHAPTER 5 ===
The following afternoon Holmes led Lestrade, Mrs. Hartley and myself to a
small lodging house in Wapping. In the upstairs back room, thin and
unshaven but very much alive, sat Edmund Hartley.

"I could not pay Marsh," he said wretchedly. "He threatened to have me
taken up for fraud. I thought if I vanished for a week or two, he might
take the stock and leave me be."

"And the clocks?" I asked.

"I stopped them myself," said Hartley. "Each one has a small release
lever behind the pendulum. I set them all to the hour I left, seventeen
minutes past four, so that my sister would know I had gone of my own
accord and not been taken. It was our old signal from when we were
children."

Mrs. Hartley wept and embraced him. Lestrade, somewhat deflated, went off
to see about Mr. Marsh.

"I knew it the moment I saw the second teaspoon," said Holmes to me as we
descended the stairs. Before I could ask what teaspoon he meant, for I had
seen none, he had hailed a cab.

=== CHAPTER 6 ===
It was some days later, by the fire in Baker Street, that I pressed
Holmes for an account of the affair.

"The tar on Mrs. Hartley's skirt you know about," he said. "The brass dust
on young Crane's hand told me he was doing private work, and a boy who
does private work at night knows a good deal about where his master's
stock is going. That led us to Marsh. The stopped clocks, Hartley has
explained himself; I suspected a signal the moment I saw they were all
alike, for no accident stops twenty clocks at the same minute."

"And the rest?" I asked. "The key, the blue sand, the canary?"

Holmes smiled and reached for his violin. "Some things, Watson, are best
left to the reader's imagination."

He played until well past midnight, and I retired no wiser than before.
"""


CORPUS_PATH.write_text(build_corpus())


# ════════════════════════════════════════════════════════════════════════
# TODO 2: Write the scanner and main agent prompts.
#
# Return (scanner_prompt, main_prompt):
#   - scanner_prompt: what the section-scanner subagent should look for in
#     ONE section it's handed, and what it should return.
#   - main_prompt: tells the main agent about the corpus file, the header
#     format from TODO 1, and to run a WORKFLOW that splits the corpus and
#     dispatches one scanner call per section (the word "workflow" is what
#     triggers code-based dispatch, see the lesson).
# ════════════════════════════════════════════════════════════════════════

def build_prompts() -> tuple[str, str]:
    """TODO 2: return (scanner_prompt, main_prompt)."""
    scanner_prompt = """\
You are a clue scanner for a Sherlock Holmes story. You will be given ONE
chapter of the story. Your job is to find clues or deductions that Holmes
mentions but does not explain within that chapter.

What counts as an unexplained clue:
- Holmes states a conclusion, hints at a significant detail, or points to
  an object, and the chapter never gives the reasoning behind it.
- Example: "Mark the stain on the doorframe, Watson," and the chapter
  never says what the stain means.

What does NOT count:
- A deduction Holmes explains in the same passage. Example: "You came by
  ferry; there is tar from the ferry benches on your hem." The reasoning
  is given, so do not flag it.
- Plot mysteries that are not Holmes's own clues (e.g. "the man is
  missing").

You only see one chapter, so a clue may be explained in another chapter.
Report it anyway if it is unexplained within THIS chapter; the main agent
will reconcile across chapters.

Return your findings in exactly this format, because code will parse it:

CLUE: <exact quote from the chapter>
WHY: <one sentence on what is left unexplained>

Repeat the CLUE/WHY pair for each finding. If there are none, return the
single word NONE. Do not add any other commentary.
"""

    main_prompt = """\
You coordinate an analysis of a Sherlock Holmes story stored at
/my_corpus.txt. The story is split into chapters, and each chapter begins
with a header line in exactly this format:

=== CHAPTER N ===

where N is the chapter number (1, 2, 3, ...).

Goal: find every clue Holmes mentions but never explains anywhere in the
story.

Run a WORKFLOW to do this:
1. Read /my_corpus.txt.
2. Split it into chapters on the "=== CHAPTER N ===" header lines.
3. Dispatch one call to the section-scanner subagent per chapter, passing
   the chapter number and that chapter's full text. Do not read or analyse
   the chapters yourself; delegate every chapter to the scanner.
4. Collect every scanner result, keeping track of which chapter it came
   from. A result of NONE means that chapter had no findings.

Then reconcile across chapters before reporting. The scanner sees only one
chapter at a time, so it may flag a clue that a later chapter explains
(for example, a detail that a character or Holmes accounts for near the
end of the story). Drop any flagged clue that another chapter clearly
explains. Keep clues that Holmes deliberately leaves unexplained.

Final report: a list of the unexplained clues grouped by chapter, each
with the exact quote and a one-line note on what is never explained. After
that, briefly list any clues you dropped during reconciliation and which
chapter explained them.
"""

    return scanner_prompt, main_prompt


SCANNER_PROMPT, MAIN_PROMPT = build_prompts()

section_scanner = {
    "name": "section-scanner",
    "description": (
        "Scan one section of the corpus for whatever the scanner prompt "
        "asks for. Delegate one section per call."
    ),
    "system_prompt": SCANNER_PROMPT,
    "model": model,
}

agent = create_deep_agent(
    model=strong_model,
    middleware=[CodeInterpreterMiddleware()],
    system_prompt=MAIN_PROMPT,
    subagents=[section_scanner],
    backend=FilesystemBackend(root_dir=DATA_DIR, virtual_mode=True),
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Run a workflow to scan every section of my_corpus.txt and report what you find.",
            }
        ]
    },
    config={"recursion_limit": 100},
)
print(result["messages"][-1].content)

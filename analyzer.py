from __future__ import annotations

import re
from typing import Any


FILE_PATTERN = re.compile(
    r"\b[\w\-./]+\.(?:py|js|jsx|ts|tsx|html|css|json|md|java|"
    r"cpp|c|ipynb|txt|csv|yaml|yml|toml|sql|sh)\b",
    flags=re.IGNORECASE,
)

COMPLETED_KEYWORDS = (
    "finished",
    "completed",
    "done",
    "works",
    "working",
    "implemented",
    "built",
    "added",
    "fixed",
    "created",
    "set up",
    "connected",
)

BLOCKER_KEYWORDS = (
    "error",
    "issue",
    "problem",
    "stuck",
    "fails",
    "failing",
    "failed",
    "broken",
    "doesn't work",
    "does not work",
    "not working",
    "invalid",
    "bug",
    "blocked",
)

NEXT_STEP_KEYWORDS = (
    "next",
    "need to",
    "should",
    "plan to",
    "have to",
    "going to",
    "todo",
    "to-do",
)

QUESTION_WORDS = (
    "why",
    "how",
    "what",
    "where",
    "when",
    "which",
    "whether",
)


def split_sentences(text: str) -> list[str]:
    cleaned_text = re.sub(
        r"\s+",
        " ",
        text.strip(),
    )

    if not cleaned_text:
        return []

    pieces = re.split(
        r"(?<=[.!?])\s+|\n+",
        cleaned_text,
    )

    return [
        piece.strip(" -•\t")
        for piece in pieces
        if piece.strip()
    ]


def contains_keyword(
    sentence: str,
    keywords: tuple[str, ...],
) -> bool:
    lowered_sentence = sentence.lower()

    return any(
        keyword in lowered_sentence
        for keyword in keywords
    )


def remove_duplicates(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for item in items:
        cleaned_item = item.strip()
        lowercase_item = cleaned_item.lower()

        if cleaned_item and lowercase_item not in seen:
            seen.add(lowercase_item)
            result.append(cleaned_item)

    return result


def extract_file_names(text: str) -> list[str]:
    detected_files = FILE_PATTERN.findall(text)

    return sorted(
        set(detected_files),
        key=str.lower,
    )


def extract_questions(
    sentences: list[str],
) -> list[str]:
    questions: list[str] = []

    for sentence in sentences:
        lowered_sentence = sentence.lower().strip()

        if sentence.endswith("?"):
            questions.append(sentence)

        elif any(
            lowered_sentence.startswith(f"{word} ")
            for word in QUESTION_WORDS
        ):
            questions.append(sentence)

        elif (
            "not sure" in lowered_sentence
            or "figure out" in lowered_sentence
        ):
            questions.append(sentence)

    return remove_duplicates(questions)[:4]


def infer_current_task(
    sentences: list[str],
    completed: list[str],
    blockers: list[str],
) -> str:
    next_step_candidates = [
        sentence
        for sentence in sentences
        if contains_keyword(
            sentence,
            NEXT_STEP_KEYWORDS,
        )
    ]

    if next_step_candidates:
        return next_step_candidates[0]

    completed_lowercase = {
        item.lower()
        for item in completed
    }

    blocker_lowercase = {
        item.lower()
        for item in blockers
    }

    for sentence in reversed(sentences):
        lowered_sentence = sentence.lower()

        if (
            lowered_sentence not in completed_lowercase
            and lowered_sentence not in blocker_lowercase
        ):
            return sentence

    if blockers:
        return f"Resolve: {blockers[0]}"

    if completed:
        return (
            "Continue from the most recently completed step."
        )

    return "Continue working from the saved context."


def clean_next_step(sentence: str) -> str:
    cleaned_sentence = sentence.strip()

    patterns = (
        r"^next[,:\s]+",
        r"^i\s+need\s+to\s+",
        r"^we\s+need\s+to\s+",
        r"^i\s+should\s+",
        r"^we\s+should\s+",
        r"^i\s+plan\s+to\s+",
        r"^we\s+plan\s+to\s+",
        r"^todo[:\s]+",
        r"^to-do[:\s]+",
    )

    for pattern in patterns:
        cleaned_sentence = re.sub(
            pattern,
            "",
            cleaned_sentence,
            flags=re.IGNORECASE,
        )

    if cleaned_sentence:
        cleaned_sentence = (
            cleaned_sentence[0].upper()
            + cleaned_sentence[1:]
        )

    return cleaned_sentence.rstrip(".")


def build_next_steps(
    sentences: list[str],
    blocker: str,
    detected_blockers: list[str],
    explicit_next_step: str,
) -> list[str]:
    steps: list[str] = []

    if explicit_next_step.strip():
        steps.append(
            clean_next_step(explicit_next_step)
        )

    for sentence in sentences:
        if contains_keyword(
            sentence,
            NEXT_STEP_KEYWORDS,
        ):
            steps.append(
                clean_next_step(sentence)
            )

    main_blocker = blocker.strip()

    if not main_blocker and detected_blockers:
        main_blocker = detected_blockers[0]

    if main_blocker:
        steps.extend(
            [
                f"Reproduce the blocker: {main_blocker}",
                "Test one small change at a time.",
                "Record what changed before trying another fix.",
            ]
        )

    if not steps:
        steps.extend(
            [
                "Open the most relevant file or note.",
                "Review the last completed step.",
                "Continue with the first unfinished task.",
            ]
        )

    return remove_duplicates(steps)[:5]


def build_quick_restart(
    relevant_files: list[str],
    next_steps: list[str],
    current_task: str,
) -> list[str]:
    quick_steps: list[str] = []

    if relevant_files:
        quick_steps.append(
            f"Open {relevant_files[0]}."
        )

    if current_task:
        quick_steps.append(
            current_task.rstrip(".") + "."
        )

    quick_steps.extend(
        step.rstrip(".") + "."
        for step in next_steps
    )

    return remove_duplicates(quick_steps)[:4]


def analyze_context(
    project_name: str,
    context: str,
    next_step: str = "",
    blocker: str = "",
) -> dict[str, Any]:
    sentences = split_sentences(context)

    completed = remove_duplicates(
        [
            sentence
            for sentence in sentences
            if contains_keyword(
                sentence,
                COMPLETED_KEYWORDS,
            )
            and not contains_keyword(
                sentence,
                BLOCKER_KEYWORDS,
            )
        ]
    )[:5]

    detected_blockers = remove_duplicates(
        [
            sentence
            for sentence in sentences
            if contains_keyword(
                sentence,
                BLOCKER_KEYWORDS,
            )
        ]
    )

    if blocker.strip():
        detected_blockers.insert(
            0,
            blocker.strip(),
        )

    detected_blockers = remove_duplicates(
        detected_blockers
    )[:5]

    relevant_files = extract_file_names(context)

    current_task = infer_current_task(
        sentences=sentences,
        completed=completed,
        blockers=detected_blockers,
    )

    next_steps = build_next_steps(
        sentences=sentences,
        blocker=blocker,
        detected_blockers=detected_blockers,
        explicit_next_step=next_step,
    )

    unresolved_questions = extract_questions(
        sentences
    )

    summary = (
        sentences[0]
        if sentences
        else "No detailed work context was provided."
    )

    return {
        "project": (
            project_name.strip()
            or "Untitled Project"
        ),
        "summary": summary,
        "completed": completed,
        "current_task": current_task,
        "blockers": detected_blockers,
        "next_steps": next_steps,
        "quick_restart": build_quick_restart(
            relevant_files=relevant_files,
            next_steps=next_steps,
            current_task=current_task,
        ),
        "relevant_files": relevant_files,
        "unresolved_questions": unresolved_questions,
    }
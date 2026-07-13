from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import streamlit as st

from analyzer import analyze_context
from storage import add_session, delete_session, load_sessions


st.set_page_config(
    page_title="Interrupt Me Later",
    page_icon="⏸️",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .hero {
            padding: 1.4rem 1.6rem;
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 18px;
            margin-bottom: 1.4rem;
        }

        .restart-box {
            padding: 1rem 1.1rem;
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 14px;
            margin-bottom: 0.7rem;
        }

        div[data-testid="stButton"] button {
            border-radius: 12px;
            font-weight: 700;
        }

        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextInput"] input {
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def show_list(items: list[str], empty_message: str) -> None:
    if not items:
        st.info(empty_message)
        return

    for item in items:
        st.markdown(f"- {item}")


def show_quick_restart(analysis: dict) -> None:
    st.markdown("### ⚡ 30-second restart")

    quick_steps = analysis.get("quick_restart", [])

    if not quick_steps:
        quick_steps = analysis.get("next_steps", [])

    for number, step in enumerate(quick_steps, start=1):
        st.markdown(
            f"""
            <div class="restart-box">
                <strong>{number}.</strong> {step}
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_restart_card(session: dict, compact: bool = False) -> None:
    analysis = session["analysis"]

    st.markdown(f"## {analysis['project']}")
    st.caption(f"Paused {session['created_at']}")

    show_quick_restart(analysis)

    if compact:
        return

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.markdown("### ✅ What is already done")

        show_list(
            analysis.get("completed", []),
            "No completed steps were detected.",
        )

        st.markdown("### 📁 Relevant files")

        relevant_files = analysis.get("relevant_files", [])

        if relevant_files:
            for filename in relevant_files:
                st.code(filename, language=None)
        else:
            st.info("No file names were detected.")

    with right_column:
        st.markdown("### 🎯 Current task")

        st.warning(
            analysis.get(
                "current_task",
                "No current task was detected.",
            )
        )

        st.markdown("### 🚧 Blockers")

        blockers = analysis.get("blockers", [])

        if blockers:
            for blocker in blockers:
                st.error(blocker)
        else:
            st.success("No blockers were detected.")

    st.markdown("### ❓ Unresolved questions")

    show_list(
        analysis.get("unresolved_questions", []),
        "No unresolved questions were detected.",
    )

    st.markdown("### 🧭 Full next-step plan")

    for number, step in enumerate(
        analysis.get("next_steps", []),
        start=1,
    ):
        st.write(f"**{number}.** {step}")

    with st.expander("View original work context"):
        st.write(session["raw_context"])


st.markdown(
    """
    <div class="hero">
        <h1>⏸️ Interrupt Me Later</h1>
        <p>
            Save your train of thought before an interruption and return
            with a clear restart plan.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

pause_tab, resume_tab, about_tab = st.tabs(
    [
        "Pause a session",
        "Resume previous work",
        "How it works",
    ]
)

with pause_tab:
    st.subheader("Create a restart checkpoint")

    st.write(
        "Paste anything that would help your future self, including "
        "progress, code notes, errors, unfinished ideas, file names, "
        "or what you planned to do next."
    )

    project_name = st.text_input(
        "Project name",
        placeholder="Example: Hackathon website",
    )

    work_context = st.text_area(
        "Current work context",
        height=260,
        placeholder=(
            "Example: I am working on a research presentation. I finished organizing my sources and drafted the introduction. I am stuck on how to explain the main data clearly. Next I need to create the results slide and decide which graph to use."
        ),
    )

    left_input, right_input = st.columns(2)

    with left_input:
        blocker = st.text_input(
            "Main blocker (optional)",
            placeholder="Example: The response is not valid JSON",
        )

    with right_input:
        next_step = st.text_input(
            "Planned next step (optional)",
            placeholder="Example: Print the raw response",
        )

    return_mode = st.radio(
        "Default return view",
        [
            "Quick restart",
            "Detailed recap",
        ],
        horizontal=True,
    )

    if st.button(
        "Pause Session",
        type="primary",
        use_container_width=True,
    ):
        if not work_context.strip():
            st.error(
                "Add some work context before pausing the session."
            )

        else:
            with st.spinner("Preserving your mental context..."):
                analysis = analyze_context(
                    project_name=project_name,
                    context=work_context,
                    next_step=next_step,
                    blocker=blocker,
                )

                session = {
                    "id": str(uuid4()),
                    "created_at": datetime.now().strftime(
                        "%B %d, %Y at %I:%M %p"
                    ),
                    "raw_context": work_context.strip(),
                    "return_mode": return_mode,
                    "analysis": analysis,
                }

                add_session(session)

            st.success("Checkpoint saved.")

            show_restart_card(
                session,
                compact=return_mode == "Quick restart",
            )

with resume_tab:
    sessions = load_sessions()

    if not sessions:
        st.info(
            "No saved sessions yet. Pause a session to create one."
        )

    else:
        st.write(
            f"You have **{len(sessions)}** saved checkpoint(s)."
        )

        for session in sessions:
            analysis = session["analysis"]

            label = (
                f"{analysis['project']} — "
                f"{session['created_at']}"
            )

            with st.expander(label):
                detailed = st.toggle(
                    "Show detailed recap",
                    value=(
                        session.get("return_mode")
                        == "Detailed recap"
                    ),
                    key=f"detail-{session['id']}",
                )

                show_restart_card(
                    session,
                    compact=not detailed,
                )

                if st.button(
                    "Delete this checkpoint",
                    key=f"delete-{session['id']}",
                ):
                    delete_session(session["id"])
                    st.success("Checkpoint deleted.")
                    st.rerun()

with about_tab:
    st.subheader("How does this site work?")

    st.write(
        "The website takes unstructured notes and automatically "
        "identifies completed work, current tasks, blockers, file "
        "names, unresolved questions, and next steps. It then turns "
        "that information into a clean restart checkpoint."
    )

    st.subheader("What the website looks for")

    st.markdown(
        """
        - Progress words such as **finished**, **built**, **fixed**, and **working**
        - Blocker words such as **error**, **stuck**, **broken**, and **not working**
        - Next-step phrases such as **next**, **need to**, and **should**
        - Questions and unfinished decisions
        """
    )

    st.subheader("Privacy")

    st.write(
        "All analysis happens through local Python rules, and saved sessions remain "
        "inside the project's data file!"
    )
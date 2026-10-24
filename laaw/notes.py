"""Notes rendering for the LAAW CLI. Pure — takes Notes, returns markdown files."""

from .constants import GENERATED_HEADER, NOTES_FILE_WORD_CAP, NOTE_WORD_CAP, TAG_ORDER
from .model.note import Note


def validate_note(note: Note) -> None:
    count = note.word_count()
    if count > NOTE_WORD_CAP:
        raise ValueError(f"note exceeds {NOTE_WORD_CAP} words ({count})")


def _content_words(notes: list[Note]) -> int:
    return sum(n.word_count() for n in notes)


def _group_by_tag(notes: list[Note]) -> list[tuple[str, list[Note]]]:
    """Return [(tag, [notes])] in TAG_ORDER, unknown tags folded into 'other'."""
    buckets: dict[str, list[Note]] = {tag: [] for tag in TAG_ORDER}
    for note in notes:
        buckets[note.tag if note.tag in buckets else "other"].append(note)
    return [(tag, group) for tag, group in buckets.items() if group]


def _section_lines(tag: str, notes: list[Note]) -> list[str]:
    return [f"## {tag}"] + [f"- {note.text}" for note in notes]


def _file_text(body_lines: list[str]) -> str:
    return "\n".join(body_lines) + "\n"


def render_notes(notes: list[Note]) -> dict[str, str]:
    for note in notes:
        validate_note(note)

    groups = _group_by_tag(notes)
    files: dict[str, str] = {}
    links: list[str] = []
    overflow_index = 0
    main_sections: list[list[str]] = []
    main_words = 0

    def emit(tag: str, chunk: list[Note]) -> None:
        nonlocal overflow_index
        overflow_index += 1
        filename = f"notes_{overflow_index}.md"
        files[filename] = _file_text(_section_lines(tag, chunk))
        links.append(f"- {filename} (tags: {tag})")

    for tag, tag_notes in groups:
        # A tag that alone exceeds the cap cannot share a file; split it into its own.
        if _content_words(tag_notes) > NOTES_FILE_WORD_CAP:
            for chunk in _chunks(tag_notes):
                emit(tag, chunk)
            continue
        # Otherwise pack into the main file while note content stays under the cap.
        if main_words + _content_words(tag_notes) <= NOTES_FILE_WORD_CAP:
            main_sections.append(_section_lines(tag, tag_notes))
            main_words += _content_words(tag_notes)
        else:
            emit(tag, tag_notes)

    main_lines = [GENERATED_HEADER, "# Notes"]
    for section in main_sections:
        main_lines += section
    files["notes.md"] = _file_text(main_lines + links)
    return files


def _chunks(notes: list[Note]) -> list[list[Note]]:
    chunks: list[list[Note]] = []
    current: list[Note] = []
    for note in notes:
        if current and _content_words(current) + note.word_count() > NOTES_FILE_WORD_CAP:
            chunks.append(current)
            current = [note]
        else:
            current.append(note)
    if current:
        chunks.append(current)
    return chunks

# workflow.md structural conventions

Established during P02. Applies to any future work that edits
`workflow.md` or adds to `.ai/workflow/reference/` — not just P02's
own tasks.

## Section stability

Every one of `workflow.md`'s 13 section headings/numbers is
deliberately kept stable — headings are preserved byte-for-byte across
edits specifically so every cross-reference elsewhere in the repo
(`.ai/workflow/workflow.md §N`/`#N-...` links in `skills/*-full/`,
`README.md`, and the Full-profile templates) keeps resolving without
needing its own edit.

**When adding content to `workflow.md`:** prefer a new subsection
within an existing section (e.g. §5's `### Execution modes`) over
inserting a brand-new numbered section. A new top-level section shifts
every following section's number, which breaks every anchor pointing
past it and reintroduces exactly the cross-reference risk this
convention exists to avoid. If a genuinely new top-level section is
unavoidable, redo a full cross-reference sweep (`grep` every
`workflow.md §`/`workflow.md#` occurrence across `skills/*-full/`,
`README.md`, and the Full templates) before considering the change
done — don't assume it's still safe just because it worked out that
way for past changes.

## `reference/` file convention

`.ai/workflow/reference/` holds occasional-need detail behind
`workflow.md`'s trimmed core — rationale, historical-incident
explanations, lookup tables not needed on every read. One file per
concept (not fewer/larger files). Each reference file:

- Opens with a one-line "what this is for, referenced from
  `workflow.md §N`" pointer, since it may be read standalone, out of
  `workflow.md`'s narrative order.
- Is linked from the *specific* sentence in core that needs it — not
  just dropped into the folder and left for an agent to browse and
  guess which file is relevant.

A reference file with no inbound link from core is a bug (orphaned),
same severity as a broken cross-reference in the other direction.

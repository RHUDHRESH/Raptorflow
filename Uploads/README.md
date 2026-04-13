# Uploads

**This directory is read-only reference material. It is not used by any build, test, or deployment step.**

The Word and Markdown files in this directory are the original source documents that were uploaded and used to inform the scaffold design. They are preserved here for traceability — to ensure every architectural decision can be traced back to its source.

## Contents

| Path                 | Description                                         |
| -------------------- | --------------------------------------------------- |
| `Word/`              | Original .docx source documents (uploaded corpus)   |
| `Markdown/`          | Converted markdown versions of the source documents |
| `markdown_files.zip` | Bulk export of all markdown files                   |

## What this means for you

- **Do not edit these files.** They are the historical record of what was built from.
- **Do not depend on them** in any build script, test, or runtime code.
- They exist so that if someone asks "why does the scaffold look like this?", the answer is traceable.
- The authoritative scaffold is defined by `schemas/`, `crates/`, `apps/web/`, and `database/migrations/` — not these documents.

## Traceability

Each source document has a corresponding digest in `docs/source-digests/`. The full list is validated by `scripts/check-docs.mjs`.

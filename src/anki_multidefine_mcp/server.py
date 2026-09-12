"""anki-multidefine-mcp — MCP server exposing MultiDefine dictionary providers."""

from __future__ import annotations

from mcp.server import MCPServer

from .providers import build_provider, PROVIDERS

mcp = MCPServer("anki-multidefine")

# Static capability metadata (source of truth: manual, matches provider behaviour)
_LANG_META = {
    "english":     {"has_audio": True,  "has_ipa": True,  "has_verb_forms": True},
    "german":      {"has_audio": True,  "has_ipa": True,  "has_verb_forms": True},
    "russian":     {"has_audio": True,  "has_ipa": True,  "has_verb_forms": False},
    "french":      {"has_audio": True,  "has_ipa": False, "has_verb_forms": False},
    "azerbaijani": {"has_audio": False, "has_ipa": False, "has_verb_forms": False},
}


@mcp.tool()
def define(word: str, language: str) -> dict:
    """Look up a word in a monolingual dictionary.

    Returns structured word_info with definitions, examples, IPA, audio URL,
    and verb forms. Returns {"found": false} if the word is not in the dictionary.
    Raises ValueError for an unsupported language key (call languages() first).
    """
    provider = build_provider(language, {})
    if provider is None:
        raise ValueError(
            f"Unsupported language {language!r}. Call languages() to see available options."
        )
    results = provider.get_words_info(word)
    if not results:
        return {"found": False, "word": word, "language": language}
    return {"found": True, "word": word, "language": language, "entries": results}


@mcp.tool()
def languages() -> list:
    """List supported languages and their capabilities (audio, IPA, verb forms)."""
    out = []
    for key, cls in PROVIDERS.items():
        meta = _LANG_META.get(key, {})
        out.append({"key": key, "display_name": cls().display_name, **meta})
    return out


_SCHEMA = """\
# MultiDefine → Anki field mapping

Read this before adding MultiDefine cards via anki-mcp-server.

## Note type
Use: MultiDefine_{Language}  e.g. MultiDefine_German, MultiDefine_Russian
These types are created automatically when the MultiDefine Anki add-on is installed.
If the add-on is not installed, create a note type with the 6 fields below in order.

## Field mapping (0-indexed)

| # | Field name            | Value source |
|---|-----------------------|--------------|
| 0 | Word                  | entries[0].name  (the resolved headword) |
| 1 | DefinitionAndExamples | Formatted HTML — see format rules below |
| 2 | Audio                 | [sound:{filename}] — see audio rules below |
| 3 | Phonetics             | [ipa_text] — from pronunciations[0].ipa, or empty |
| 4 | VerbForms             | space-joined verb_forms_list, or empty |
| 5 | Image                 | leave empty unless user provides one |

## DefinitionAndExamples format rules
For each entry in word_info.entries (multiple = different parts of speech):
  - If entry.wordform is set: render as <i>{wordform}</i>
  - For each definition (up to max_definitions, default 3):
      <div><b>{description}</b></div>
      <ul><li>{example}</li>...</ul>   (up to max_examples, default 2)
  - Separate entries with <hr/>
Cloze: wrap the headword token in examples as #word# so the card template
blanks it on the reverse side. The template renders #word# → blank on back,
#word# → bold on front answer.

## Audio rules
1. Check entries[].pronunciations[] for a non-null mp3 or ogg URL.
2. Call anki-mcp-server's storeMediaFile tool to download the audio into
   Anki's media collection. Use the URL's last path segment (URL-decoded) as
   the filename.
3. Reference as [sound:{filename}] in the Audio field.
4. If no audio URL exists: leave Audio field empty (do not write "No audio").

## Workflow rules
- Before adding: call anki-mcp-server findNotes to check for existing cards
  with the same word in the same deck to avoid duplicates.
- If define() returns {"found": false}: tell the user; do not create a note.
- Multiple entries in one define() result (noun + verb etc.): merge into one
  note, concatenated in DefinitionAndExamples with <hr/> between them.
"""


@mcp.resource("multidefine://schema")
def schema() -> str:
    """Field mapping and workflow rules for adding MultiDefine cards to Anki."""
    return _SCHEMA


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

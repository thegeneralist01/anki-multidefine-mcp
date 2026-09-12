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
    model_name = f"MultiDefine_{language.capitalize()}"
    return {
        "found": True,
        "word": word,
        "language": language,
        "entries": results,
        "_schema": {
            "model_name": model_name,
            "fields": {
                "Word": "entries[0].name",
                "DefinitionAndExamples": (
                    f"<i>wordform</i> if set, then <div><b>description</b></div> per definition "
                    f"(up to 3); <ul><li>example</li></ul> if examples list is non-empty (up to 2); "
                    f"replace '{word}' token with #{word}# for cloze; separate multiple entries with <hr/>"
                ),
                "Audio": (
                    "download mp3 or ogg URL via storeMediaFile and write [sound:filename] — "
                    "if no URL exists write empty string, NEVER write placeholder text"
                ),
                "Phonetics": "pronunciations[0].ipa verbatim — empty string if none",
                "VerbForms": "space-joined verb_forms_list — empty string if none",
                "Image": "",
            },
            "rules": [
                f"Use modelName '{model_name}' — NEVER Basic or any other note type",
                "Call findNotes before addNote to avoid duplicates",
                "If define() returned found=false do not create a note",
            ],
        },
    }


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

## CRITICAL: Note type

ALWAYS use: MultiDefine_{Language}
  - MultiDefine_English
  - MultiDefine_German
  - MultiDefine_Russian
  - MultiDefine_French
  - MultiDefine_Azerbaijani

NEVER use Basic, Basic (and reversed card), Cloze, or any other note type.
The MultiDefine note types are created automatically when the MultiDefine Anki
add-on is installed. If modelNames() does not list them, tell the user to install
the add-on before proceeding.

## Field mapping (0-indexed)

| # | Field name            | Value source |
|---|-----------------------|--------------|
| 0 | Word                  | entries[0].name  (the resolved headword) |
| 1 | DefinitionAndExamples | Formatted HTML — see format rules below |
| 2 | Audio                 | [sound:{filename}] — see audio rules below |
| 3 | Phonetics             | pronunciations[0].ipa verbatim, or empty string |
| 4 | VerbForms             | space-joined verb_forms_list, or empty string |
| 5 | Image                 | empty string unless user provides one |

## DefinitionAndExamples format rules
For each entry in word_info.entries (multiple = different parts of speech):
  - If entry.wordform is set: render as <i>{wordform}</i>
  - For each definition group, for each definition (up to 3):
      <div><b>{description}</b></div>
      <ul><li>{example}</li>...</ul>   (up to 2 examples; omit <ul> if none)
  - Separate multiple entries with <hr/>
Cloze: replace the headword token inside description/examples with #word# so the
card template blanks it on the reverse side.

## Audio rules
1. Check entries[].pronunciations[] for a non-null mp3 or ogg URL.
2. Call anki-mcp-server's storeMediaFile tool to download the URL into
   Anki's media collection. Use the URL's last path segment (URL-decoded) as
   the filename.
3. Set the Audio field to [sound:{filename}].
4. If no audio URL exists: set Audio field to empty string "".
   NEVER write "No audio", "No audio found", or any placeholder text.

## Workflow rules
- Before adding: call findNotes to check for existing cards with the same word
  in the same deck to avoid duplicates.
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

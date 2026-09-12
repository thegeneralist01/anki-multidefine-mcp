# AGENTS.md — anki-multidefine-mcp contributor context

This file is part of anki-multidefine-mcp and is licensed under the GNU General Public License, version 2. See LICENSE.

## Project purpose

anki-multidefine-mcp is a pip-installable MCP server exposing MultiDefine dictionary providers as MCP tools. Providers return dictionary data; a separate Anki MCP server creates notes and stores media.

## Repository layout

```text
src/anki_multidefine_mcp/
  server.py                  MCP server, tools, resources, and stdio entry point
  providers/
    __init__.py              provider registry and build_provider()
    base.py                  DictionaryProvider and word_info helpers
    net.py                   shared HTTP helpers
    oxford.py                upstream Oxford scraper; BSD 3-Clause
    english_oxford.py        Oxford provider wrapper
    german_dwds.py           DWDS provider
    russian_wiktionary.py    ru.Wiktionary provider
    french_larousse.py       Larousse provider
    azerbaijani_azleks.py    AZLEKS provider
```

## Hard rules

1. `providers/oxford.py` is upstream BSD 3-Clause code by Near Huscarl. Do not modify it.
2. Providers must not import `anki`, `aqt`, or `mw`. They must be importable without Anki.
3. This package uses pip-installed `beautifulsoup4`, including soupsieve. `.select()` and `.select_one()` are allowed in provider code.
4. Requests to `*.wikimedia.org` or `*.wiktionary.org` must use the Wikimedia-compliant User-Agent already defined in `russian_wiktionary.py`.
5. Providers return data; `server.py` performs MCP I/O. Keep that separation.

## word_info contract

Every provider's `get_words_info(word)` returns `list[dict]` where each dict is:

```python
{
  'name': str,                    # resolved headword
  'wordform': Optional[str],      # POS label (italic in output), or None
  'pronunciations': [
    {
      'prefix': str,              # must match one of provider.pronunciation_prefixes
      'ipa': Optional[str],       # phonetic text without surrounding slashes/brackets
      'mp3': Optional[str],       # absolute URL or None
      'ogg': Optional[str],       # absolute URL or None
      'audio_name': Optional[str] # explicit filename, or None → derive from URL
    }
  ],
  'definitions': [                # list of namespace groups
    {
      'namespace': Optional[str],
      'definitions': [
        {
          'description': Optional[str],
          'examples': [str],
          'extra_example': [str]
        }
      ]
    }
  ],
  'verb_forms_list': [str],       # inflected forms; may be []
}
```

Use `make_sense(description, examples)` and `single_group(senses)` from `providers/base.py` to build these structures.

## Adding a new language

1. Create `providers/<language>.py`, subclass `DictionaryProvider`, set `key`, `display_name`, and `pronunciation_prefixes`, and implement `get_words_info(word) -> list[dict]`.
2. Register it in `providers/__init__.py` by importing it and adding its key to `PROVIDERS`.
3. Add its capability metadata to `_LANG_META` in `server.py`.

## Verification

Use the repository-root virtual environment. The live lookup checks require network access. Run these five checks before merging provider or server changes:

```bash
.venv/bin/python -c "from src.anki_multidefine_mcp.server import mcp; print('OK')"

.venv/bin/python -c "from src.anki_multidefine_mcp.server import languages; result = languages(); assert len(result) == 5; assert all({'key', 'display_name', 'has_audio', 'has_ipa', 'has_verb_forms'} <= entry.keys() for entry in result); print('Languages OK')"

.venv/bin/python -c "from src.anki_multidefine_mcp.server import define; result = define('Haus', 'german'); assert result['found'] is True; assert result['entries'][0]['name'] == 'Haus'; assert result['entries'][0]['definitions'][0]['definitions']; print('German OK')"

.venv/bin/python -c "from src.anki_multidefine_mcp.server import define; russian = define('уважение', 'russian'); assert russian['found'] is True; french = define('zzznonsenseword999', 'french'); assert french['found'] is False; print('Russian and not-found OK')"

.venv/bin/python -c "from src.anki_multidefine_mcp.server import schema; result = schema(); assert 'MultiDefine_' in result and 'storeMediaFile' in result; print('Schema OK')"
```

After `.venv/bin/pip install -e .`, check the MCP stdio handshake:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0"}}}' | .venv/bin/python -m anki_multidefine_mcp.server
```

## MCP SDK

The required SDK is `mcp[cli]>=2,<3`. Use `MCPServer` from `mcp.server`; decorate tools with `@mcp.tool()` and resources with `@mcp.resource(uri)`; call `mcp.run()` to serve stdio.

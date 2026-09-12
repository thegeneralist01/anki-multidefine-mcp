# Contributing

This file is part of anki-multidefine-mcp and is licensed under the GNU General Public License, version 2. See LICENSE.

## Setup

Create a repository-root virtual environment and install the package:

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

There are no `dev` extras yet, so use `.venv/bin/pip install -e .` if the extras selector is unavailable.

## Smoke tests

The live lookup checks require network access. Run these five commands from the repository root:

```bash
.venv/bin/python -c "from src.anki_multidefine_mcp.server import mcp; print('OK')"

.venv/bin/python -c "from src.anki_multidefine_mcp.server import languages; result = languages(); assert len(result) == 5; assert all({'key', 'display_name', 'has_audio', 'has_ipa', 'has_verb_forms'} <= entry.keys() for entry in result); print('Languages OK')"

.venv/bin/python -c "from src.anki_multidefine_mcp.server import define; result = define('Haus', 'german'); assert result['found'] is True; assert result['entries'][0]['name'] == 'Haus'; assert result['entries'][0]['definitions'][0]['definitions']; print('German OK')"

.venv/bin/python -c "from src.anki_multidefine_mcp.server import define; russian = define('уважение', 'russian'); assert russian['found'] is True; french = define('zzznonsenseword999', 'french'); assert french['found'] is False; print('Russian and not-found OK')"

.venv/bin/python -c "from src.anki_multidefine_mcp.server import schema; result = schema(); assert 'MultiDefine_' in result and 'storeMediaFile' in result; print('Schema OK')"
```

After `.venv/bin/pip install -e .`, also check the MCP stdio handshake:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0"}}}' | .venv/bin/python -m anki_multidefine_mcp.server
```

## Adding a provider

Follow the three steps in [AGENTS.md](AGENTS.md#adding-a-new-language): create the provider, register it in `providers/__init__.py`, and add its capabilities to `_LANG_META` in `server.py`.

## Pull request checklist

- [ ] All five verification steps pass.
- [ ] `providers/oxford.py` is untouched.
- [ ] No provider imports `anki`, `aqt`, or `mw`.
- [ ] New files include a GPL v2 license header.

## License

By contributing, you license your contribution under GNU GPL version 2.

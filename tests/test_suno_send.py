"""Songs & Suno › An Suno senden (MCP): arguments, stream parsing, CLI call (no real CLI, no credits)."""
import ast
import json
import os
import re
import string
import subprocess
import tempfile
import types
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'source' / 'workstation.py'
CORE = Path(__file__).resolve().parents[1] / 'source' / 'mpw_core.py'  # Qt-free core (module-level functions)
TEXT = CORE.read_text(encoding='utf-8') + '\n' + SOURCE.read_text(encoding='utf-8')
TREE = ast.parse(TEXT)
NAMES = ('ProviderError', '_cli_detail', 'suno_create_arguments', 'suno_send_instruction', '_json_or_text',
         'parse_suno_stream', 'suno_clips', 'suno_send_matches', 'call_suno_via_claude', 'cli_environment')
CONSTANTS = ('SUNO_MCP_URL', 'SUNO_MCP_CONFIG', 'SUNO_CREATE_TOOL', 'SUNO_WAIT_TOOL', 'SUNO_SEND_TIMEOUT_SECONDS',
             'SUNO_LIMITS')


def load():
    nodes = [n for n in TREE.body
             if (isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in NAMES)
             or (isinstance(n, ast.Assign) and any(getattr(t, 'id', '') in CONSTANTS for t in n.targets))]
    ns = {'json': json, 're': re, 'os': os, 'tempfile': tempfile, 'Path': Path, 'subprocess': subprocess,
          'resolve_cli_executable': lambda provider, command: r'C:\Tools\claude.exe'}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), ns)
    return ns


FN = load()


def line(**obj):
    return json.dumps(obj, ensure_ascii=False)


def stream(arguments, create_body, wait_body, mcp='connected', extra_create=None):
    out = [line(type='system', subtype='init', mcp_servers=[{'name': 'suno', 'status': mcp}]),
           line(type='assistant', message={'content': [{'type': 'tool_use', 'id': 't0', 'name': 'ToolSearch',
                                                        'input': {'query': 'select:mcp__suno__audio-create'}}]}),
           line(type='user', message={'content': [{'type': 'tool_result', 'tool_use_id': 't0', 'content': []}]}),
           line(type='assistant', message={'content': [{'type': 'tool_use', 'id': 't1', 'name': 'mcp__suno__audio-create',
                                                        'input': arguments}]}),
           line(type='user', message={'content': [{'type': 'tool_result', 'tool_use_id': 't1',
                                                   'content': [{'type': 'text', 'text': create_body}]}]})]
    if extra_create is not None:
        out.append(line(type='assistant', message={'content': [{'type': 'tool_use', 'id': 't9',
                                                                'name': 'mcp__suno__audio-create', 'input': extra_create}]}))
    out += [line(type='assistant', message={'content': [{'type': 'tool_use', 'id': 't2', 'name': 'mcp__suno__audio-wait',
                                                         'input': {'ids': ['c1', 'c2'], 'until': 'playable'}}]}),
            line(type='user', message={'content': [{'type': 'tool_result', 'tool_use_id': 't2',
                                                    'content': [{'type': 'text', 'text': wait_body}]}]}),
            line(type='result', subtype='success', is_error=False, result='Done.')]
    return '\n'.join(out)


ARGS = FN['suno_create_arguments']('Rain Song', ' Blues Rock, raw ', '[Verse 1]\nRain on the roof\n', key='mpw-test')
CREATE = json.dumps({'clip_ids': ['c1', 'c2'], 'status': 'queued'})
WAIT = json.dumps({'id': 'c1', 'status': 'streaming', 'song_url': 'https://suno.com/song/c1',
                   'clips': [{'id': 'c1', 'title': 'Rain Song', 'status': 'streaming', 'song_url': 'https://suno.com/song/c1'},
                             {'id': 'c2', 'title': 'Rain Song', 'status': 'streaming', 'song_url': 'https://suno.com/song/c2'}]})


class Arguments(unittest.TestCase):
    def test_custom_mode_fields_trimmed_with_key(self):
        self.assertEqual(ARGS, {'title': 'Rain Song', 'style': 'Blues Rock, raw', 'lyrics': '[Verse 1]\nRain on the roof',
                                'idempotency_key': 'mpw-test'})
        auto = FN['suno_create_arguments']('T', '', 'L')
        self.assertNotIn('style', auto)
        self.assertTrue(auto['idempotency_key'].startswith('mpw-') and len(auto['idempotency_key']) > 10)
        self.assertNotEqual(auto['idempotency_key'], FN['suno_create_arguments']('T', '', 'L')['idempotency_key'])

    def test_instruction_contains_exact_json_and_only_two_tools(self):
        text = FN['suno_send_instruction'](ARGS)
        self.assertIn(json.dumps(ARGS, ensure_ascii=False, indent=1), text)
        self.assertIn('mcp__suno__audio-create exactly once', text)
        self.assertIn('mcp__suno__audio-wait', text)
        self.assertNotIn('description', json.loads(text[text.index('{'):text.rindex('}') + 1]))


class StreamParsing(unittest.TestCase):
    def test_success_and_exact_match(self):
        parsed = FN['parse_suno_stream'](stream(ARGS, CREATE, WAIT))
        self.assertEqual(parsed['mcp_status'], 'connected')
        self.assertEqual(parsed['create_inputs'], [ARGS])
        self.assertTrue(FN['suno_send_matches'](parsed['create_inputs'][0], ARGS))
        clips = FN['suno_clips'](parsed)
        self.assertEqual([c['url'] for c in clips], ['https://suno.com/song/c1', 'https://suno.com/song/c2'])
        self.assertEqual(parsed['errors'], [])

    def test_changed_lyrics_detected(self):
        changed = dict(ARGS, lyrics=ARGS['lyrics'] + '\n[Chorus]')
        parsed = FN['parse_suno_stream'](stream(changed, CREATE, WAIT))
        self.assertFalse(FN['suno_send_matches'](parsed['create_inputs'][0], ARGS))
        self.assertFalse(FN['suno_send_matches'](dict(ARGS, model='v6'), ARGS))

    def test_second_create_call_is_visible(self):
        parsed = FN['parse_suno_stream'](stream(ARGS, CREATE, WAIT, extra_create=ARGS))
        self.assertEqual(len(parsed['create_inputs']), 2)

    def test_tool_error_and_not_connected(self):
        out = '\n'.join([line(type='system', subtype='init', mcp_servers=[{'name': 'suno', 'status': 'needs-auth'}]),
                         line(type='assistant', message={'content': [{'type': 'tool_use', 'id': 't1',
                                                                      'name': 'mcp__suno__audio-create', 'input': ARGS}]}),
                         line(type='user', message={'content': [{'type': 'tool_result', 'tool_use_id': 't1', 'is_error': True,
                                                                 'content': 'HTTP 402: not enough credits'}]}),
                         'not json', line(type='result', subtype='error_during_execution', is_error=True)])
        parsed = FN['parse_suno_stream'](out)
        self.assertEqual(parsed['mcp_status'], 'needs-auth')
        self.assertEqual(parsed['errors'], ['mcp__suno__audio-create: HTTP 402: not enough credits'])
        self.assertEqual(parsed['final_error'], 'error_during_execution')
        self.assertEqual(FN['suno_clips'](parsed), [])

    def test_clips_fallback_to_create_result(self):
        parsed = {'wait_result': None, 'create_result': {'clip_ids': ['a', 'b'], 'title': 'X', 'status': 'queued'}}
        self.assertEqual([c['id'] for c in FN['suno_clips'](parsed)], ['a', 'b'])

    def test_real_stream_shape_from_account_usage(self):
        # Shape of a real Claude Code 2.1 stream (init with mcp_servers, ToolSearch, tool_result list).
        real = '\n'.join([line(type='system', subtype='init', mcp_servers=[{'name': 'suno', 'status': 'connected'}]),
                          line(type='assistant', message={'content': [{'type': 'tool_use', 'id': 'u1',
                                                                       'name': 'mcp__suno__account-usage', 'input': {}}]}),
                          line(type='user', message={'content': [{'type': 'tool_result', 'tool_use_id': 'u1',
                                                                  'content': [{'type': 'text', 'text': '{"suno_account": {}}'}]}]}),
                          line(type='result', subtype='success', is_error=False, total_cost_usd=0.1)])
        parsed = FN['parse_suno_stream'](real)
        self.assertEqual((parsed['mcp_status'], parsed['create_inputs'], parsed['errors']), ('connected', [], []))


class CliCall(unittest.TestCase):
    def test_only_suno_and_two_tools_in_empty_temp_folder(self):
        calls = []

        def run(args, **kwargs):
            config = Path(args[args.index('--mcp-config') + 1])
            calls.append((args, kwargs, json.loads(config.read_text(encoding='utf-8'))))
            return subprocess.CompletedProcess(args, 0, stream(ARGS, CREATE, WAIT).encode('utf-8'), b'')
        saved = FN['subprocess']
        FN['subprocess'] = types.SimpleNamespace(run=run, PIPE=subprocess.PIPE, TimeoutExpired=subprocess.TimeoutExpired,
                                                 CREATE_NO_WINDOW=0x08000000)
        try:
            result = FN['call_suno_via_claude']('claude', ARGS)
        finally:
            FN['subprocess'] = saved
        args, kwargs, config = calls[0]
        self.assertEqual(config, {'mcpServers': {'suno': {'type': 'http', 'url': 'https://api.suno.com/mcp'}}})
        self.assertIn('--strict-mcp-config', args)
        self.assertEqual(args[args.index('--allowedTools') + 1:], ['mcp__suno__audio-create', 'mcp__suno__audio-wait'])
        self.assertNotIn('--dangerously-skip-permissions', args)
        self.assertIn('mpw_suno_', kwargs['cwd'])
        self.assertFalse(Path(kwargs['cwd']).exists(), 'temporary folder must be removed')
        self.assertNotIn('shell', kwargs)
        self.assertEqual(result['create_inputs'], [ARGS])

    def test_timeout_becomes_cli_timeout(self):
        def run(args, **kwargs):
            raise subprocess.TimeoutExpired(args, 600)
        saved = FN['subprocess']
        FN['subprocess'] = types.SimpleNamespace(run=run, PIPE=subprocess.PIPE, TimeoutExpired=subprocess.TimeoutExpired)
        try:
            with self.assertRaises(FN['ProviderError']) as ctx:
                FN['call_suno_via_claude']('claude', ARGS)
        finally:
            FN['subprocess'] = saved
        self.assertEqual(ctx.exception.kind, 'cli_timeout')


class TextsAndWiring(unittest.TestCase):
    def test_all_languages_complete(self):
        cls = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'Workstation')
        node = next(n for n in cls.body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'SUNO_SEND_TEXTS')
        texts = ast.literal_eval(node.value)
        self.assertEqual(set(texts), {'de', 'en', 'fr', 'es', 'it'})
        fmt = string.Formatter()
        for lang, items in texts.items():
            self.assertEqual(set(items), set(texts['de']), lang)
            for key, value in items.items():
                self.assertEqual({f for _, f, _, _ in fmt.parse(value) if f},
                                 {f for _, f, _, _ in fmt.parse(texts['de'][key]) if f}, f'{lang}.{key}')

    def test_button_in_own_row_and_safe_thread_handoff(self):
        self.assertIn('self.suno_send_button.clicked.connect(self.open_suno_send_dialog)', TEXT)
        self.assertIn('job.signals.finished.connect(self._suno_send_finished)', TEXT)
        body = TEXT[TEXT.index('    def open_suno_send_dialog(self):'):TEXT.index('    def _suno_send_finished(self')]
        self.assertIn('QMessageBox.question(', body)  # credits are only spent after confirmation
        self.assertNotIn('.connect(lambda result', body)

    def test_links_saved_without_overwriting(self):
        self.assertIn("INSERT OR IGNORE INTO media_links(song_id,platform,url,label) VALUES(?,?,?,?)", TEXT)


if __name__ == '__main__':
    unittest.main()

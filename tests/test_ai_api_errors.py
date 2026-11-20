"""API error handling of the AI Prompt Launcher; no network access, urlopen is replaced."""
import ast
import io
import json
from pathlib import Path
import unittest
import urllib.error
import urllib.request

SOURCE = Path(__file__).resolve().parents[1] / 'source' / 'workstation.py'
CORE = Path(__file__).resolve().parents[1] / 'source' / 'mpw_core.py'  # Qt-free core (module-level functions)
TREE = ast.parse(CORE.read_text(encoding='utf-8') + '\n' + SOURCE.read_text(encoding='utf-8'))
NAMES = ('ProviderError', '_provider_error_detail', '_http_error_kind', '_provider_answer_text', 'call_provider')


def load():
    nodes = [n for n in TREE.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in NAMES]
    assert {n.name for n in nodes} == set(NAMES), 'API helper functions missing'
    ns = {'json': json, 'urllib': urllib}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), ns)
    return ns


FN = load()
ProviderError = FN['ProviderError']
KEY = 'sk-secret-123'


def http_error(code, body):
    return urllib.error.HTTPError('https://x', code, 'err', {}, io.BytesIO(json.dumps(body).encode()))


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class AIApiErrors(unittest.TestCase):
    def setUp(self):
        self.original = urllib.request.urlopen
        self.addCleanup(setattr, urllib.request, 'urlopen', self.original)

    def call(self, provider='Claude', raises=None, answer=None):
        def fake(request, timeout):
            if raises is not None:
                raise raises
            return Response(json.dumps(answer).encode())
        urllib.request.urlopen = fake
        return FN['call_provider'](provider, 'some-model', KEY, 'prompt')

    def kind(self, **kw):
        with self.assertRaises(ProviderError) as ctx:
            self.call(**kw)
        return ctx.exception

    def test_http_codes_are_classified_and_keep_provider_message(self):
        for code, kind in ((401, 'auth'), (403, 'auth'), (404, 'model'), (429, 'rate'),
                           (400, 'bad_request'), (500, 'server'), (529, 'server'), (418, 'http')):
            exc = self.kind(raises=http_error(code, {'error': {'message': f'msg {code}'}}))
            self.assertEqual((exc.kind, exc.code, exc.detail), (kind, str(code), f'msg {code}'))

    def test_api_key_is_never_echoed(self):
        exc = self.kind(raises=http_error(401, {'error': {'message': f'Incorrect API key {KEY}'}}))
        self.assertNotIn(KEY, exc.detail)
        self.assertIn('***', exc.detail)

    def test_gemini_list_error_body(self):
        exc = self.kind(provider='Gemini', raises=http_error(400, [{'error': {'message': 'API key not valid'}}]))
        self.assertEqual(exc.detail, 'API key not valid')

    def test_network_and_timeout(self):
        self.assertEqual(self.kind(raises=urllib.error.URLError('getaddrinfo failed')).kind, 'network')
        self.assertEqual(self.kind(raises=urllib.error.URLError(TimeoutError())).kind, 'timeout')
        self.assertEqual(self.kind(raises=TimeoutError()).kind, 'timeout')
        self.assertEqual(self.kind(raises=ConnectionResetError()).kind, 'network')

    def test_answers(self):
        ok = {'content': [{'type': 'text', 'text': 'hi'}], 'stop_reason': 'end_turn'}
        self.assertEqual(self.call(answer=ok), 'hi')
        self.assertEqual(self.kind(answer={'content': [], 'stop_reason': 'refusal'}).kind, 'blocked')
        self.assertEqual(self.kind(answer={'content': [{'type': 'text', 'text': 'x'}], 'stop_reason': 'max_tokens'}).kind, 'truncated')
        self.assertEqual(self.kind(answer={'content': [], 'stop_reason': 'end_turn'}).kind, 'empty')
        self.assertEqual(self.kind(answer={'unexpected': True}).kind, 'format')
        self.assertEqual(self.kind(provider='Gemini', answer={'promptFeedback': {'blockReason': 'SAFETY'}}).kind, 'blocked')
        self.assertEqual(self.kind(provider='Gemini', answer={'candidates': [{'finishReason': 'SAFETY'}]}).kind, 'blocked')
        self.assertEqual(self.call(provider='Gemini', answer={'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': 'g'}]}}]}), 'g')
        self.assertEqual(self.kind(provider='ChatGPT', answer={'choices': [{'finish_reason': 'length', 'message': {'content': 'x'}}]}).kind, 'truncated')
        self.assertEqual(self.call(provider='ChatGPT', answer={'choices': [{'finish_reason': 'stop', 'message': {'content': 'c'}}]}), 'c')

    def test_claude_request_defaults(self):
        sent = {}

        def fake(request, timeout):
            sent['body'], sent['timeout'] = json.loads(request.data), timeout
            return Response(json.dumps({'content': [{'type': 'text', 'text': 'ok'}], 'stop_reason': 'end_turn'}).encode())
        urllib.request.urlopen = fake
        FN['call_provider']('Claude', 'claude-sonnet-5-5', KEY, 'prompt')
        # Thinking counts against max_tokens on current models; 6000 truncated answers.
        self.assertGreaterEqual(sent['body']['max_tokens'], 16000)
        self.assertGreaterEqual(sent['timeout'], 180)
        self.assertIn("'Claude':'claude-sonnet-5-5'", SOURCE.read_text(encoding='utf-8'))

    def test_all_languages_have_all_messages(self):
        cls = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'Workstation')
        node = next(n for n in cls.body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'AI_API_ERRORS')
        texts = ast.literal_eval(node.value)
        self.assertEqual(set(texts), {'de', 'en', 'fr', 'es', 'it'})
        for lang, items in texts.items():
            self.assertEqual(set(items), set(texts['de']), lang)
            for value in items.values():
                value.format(provider='P', code='1', model='M')


if __name__ == '__main__':
    unittest.main()

from django.core.management.base import BaseCommand
import os
import requests
from agentos_sdk import AgentOS

class Command(BaseCommand):
    help = 'Connects the AI agent to the AgentOS platform'

    def handle(self, *args, **options):
        self.stdout.write('Starting AgentOS AI connector...')
        
        manifest = {
            'agent_id': '__AGENT_ID__',
            'version': '1.0.0',
            'team': 'core',
            'capabilities': ['example'],
            'actions': [
                {'label': 'Query Local AI Model', 'action': 'EXAMPLE'},
            ],
            'ui_url': os.getenv('AGENTOS_UI_URL', 'http://localhost:3001'),
        }

        def handler(action, payload):
            action = (action or '').upper()
            if action == 'EXAMPLE':
                text = payload.get('text', 'Hello, how are you?')
                ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
                try:
                    r = requests.post(
                        f"{ollama_url}/api/chat",
                        json={
                            "model": "qwen2.5-vl:3b",
                            "messages": [{"role": "user", "content": text}],
                            "stream": False
                        },
                        timeout=60
                    )
                    if r.status_code == 200:
                        ans = r.json().get('message', {}).get('content', '')
                        return {
                            'output': {'response': ans},
                            'usage': {'tokens_in': len(text.split()), 'tokens_out': len(ans.split()), 'cost': 0.0}
                        }
                    else:
                        raise Exception(f"Ollama returned status {r.status_code}: {r.text}")
                except Exception as e:
                    # Fallback if Ollama is not ready/available
                    return {
                        'output': {
                            'error': f"Ollama query failed: {e}",
                            'echo': text,
                            'note': 'Ensure Ollama is running and qwen2.5-vl:3b is pulled.'
                        },
                        'usage': {'tokens_in': len(text.split()), 'cost': 0.0}
                    }
            raise ValueError(f"Unknown action: {action}")

        client = AgentOS()
        try:
            client.run(manifest=manifest, handler=handler)
        except KeyboardInterrupt:
            self.stdout.write('Disconnected.')

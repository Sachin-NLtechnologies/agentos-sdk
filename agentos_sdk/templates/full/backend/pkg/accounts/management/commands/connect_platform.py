from django.core.management.base import BaseCommand
import os
from agentos_sdk import AgentOS

class Command(BaseCommand):
    help = 'Connects the agent to the AgentOS platform'

    def handle(self, *args, **options):
        self.stdout.write('Starting AgentOS connector...')
        
        manifest = {
            'agent_id': os.getenv('AGENTOS_AGENT_ID', '__AGENT_ID__'),
            'version': '1.0.0',
            'team': 'core',
            'capabilities': ['example'],
            'actions': [
                {'label': 'Example action', 'action': 'EXAMPLE'},
            ],
            'ui_url': os.getenv('AGENTOS_UI_URL', f"http://localhost:{os.getenv('AGENT_PORT', '3001')}"),
        }

        def handler(action, payload):
            # A simple example action
            action = (action or '').upper()
            if action == 'EXAMPLE':
                text = payload.get('text', '')
                return {
                    'output': {'echo': text},
                    'usage': {'tokens_in': len(text.split()), 'cost': 0.0}
                }
            raise ValueError(f"Unknown action: {action}")

        client = AgentOS()
        try:
            client.run(manifest=manifest, handler=handler)
        except KeyboardInterrupt:
            self.stdout.write('Disconnected.')

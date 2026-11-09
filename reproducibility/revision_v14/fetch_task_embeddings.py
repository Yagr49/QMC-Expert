"""Fetch only four fixed task descriptions; credentials stay in process memory."""
from pathlib import Path
import getpass, json, hashlib, sys, time
import requests
import numpy as np

ROOT = Path(__file__).resolve().parent
TASKS = [
    ('Sa_MIC', 'Minimum Inhibitory Concentration against Staphylococcus aureus ATCC 43300, a methicillin-resistant Gram-positive bacterium. MIC measures the lowest concentration that inhibits visible bacterial growth.'),
    ('Sa_MBC', 'Minimum Bactericidal Concentration against Staphylococcus aureus ATCC 43300, a methicillin-resistant Gram-positive bacterium. MBC measures the lowest concentration that kills 99.9% of bacteria.'),
    ('Ec_MIC', 'Minimum Inhibitory Concentration against Escherichia coli ATCC 25922, a Gram-negative reference strain. MIC measures the lowest concentration that inhibits visible bacterial growth.'),
    ('Ec_MBC', 'Minimum Bactericidal Concentration against Escherichia coli ATCC 25922, a Gram-negative reference strain. MBC measures the lowest concentration that kills 99.9% of bacteria.'),
]

def main():
    key = getpass.getpass('OpenRouter key (hidden): ')
    session = requests.Session()
    session.headers['Authorization'] = 'Bearer ' + key.strip()
    try:
        response = session.get('https://openrouter.ai/api/v1/key', timeout=30)
        print('Authentication HTTP status:', response.status_code, flush=True)
        if response.status_code != 200:
            print('Authentication failed; no paid request sent.', flush=True)
            return 1
        destination = ROOT / 'data'
        destination.mkdir(exist_ok=True)
        if (destination / 'task_text_embeddings.npy').exists():
            print('Existing cached vectors retained; no paid request sent.')
            return 0
        model = 'openai/text-embedding-3-small'
        response = session.post('https://openrouter.ai/api/v1/embeddings',
            json={'model': model, 'input': [t[1] for t in TASKS], 'encoding_format': 'float'},
            timeout=90)
        print('Embedding HTTP status:', response.status_code, flush=True)
        if response.status_code != 200:
            print('Embedding request failed; response body deliberately omitted.')
            return 1
        body = response.json()
        records = sorted(body['data'], key=lambda d: d['index'])
        vectors = np.asarray([r['embedding'] for r in records], dtype=np.float32)
        assert vectors.shape == (4, 1536) and np.isfinite(vectors).all()
        np.save(destination / 'task_text_embeddings.npy', vectors)
        metadata = {'requested_model': model, 'returned_model': body.get('model'),
            'tasks': [dict(id=t[0], text=t[1]) for t in TASKS], 'shape': list(vectors.shape),
            'usage': body.get('usage'), 'retrieved_unix': time.time(),
            'sha256': hashlib.sha256((destination / 'task_text_embeddings.npy').read_bytes()).hexdigest(),
            'note': 'Fresh reconstruction of four archived task descriptions; no molecular structures or measured activities sent.'}
        (destination / 'task_text_embeddings.json').write_text(json.dumps(metadata, indent=2))
        print(json.dumps({'cached_shape': list(vectors.shape), 'model': model, 'usage': body.get('usage')}), flush=True)
        return 0
    except requests.RequestException as error:
        print('Network request failed:', type(error).__name__, flush=True)
        return 1
    finally:
        session.headers.pop('Authorization', None)
        key = None

if __name__ == '__main__':
    sys.exit(main())

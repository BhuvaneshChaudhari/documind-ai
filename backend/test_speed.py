import requests, time

r = requests.post('http://localhost:8000/upload',
    files={'file': open(r'C:\Users\bhuva\Desktop\Internship Report Bhuvanesh.pdf', 'rb')},
    timeout=60)
print('Upload:', r.status_code)

for q in ['What cloud platform did the intern use?', 'What were the internship objectives?']:
    t0 = time.monotonic()
    r = requests.post('http://localhost:8000/ask', json={'question': q, 'top_k': 5}, timeout=120)
    t1 = time.monotonic()
    d = r.json()
    print('Q:', q)
    print('A:', d.get('answer', ''))
    print('Time:', round(t1-t0, 1), 's  Conf:', d.get('confidence_score', 'N/A'))
    print()

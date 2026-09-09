#!/usr/bin/env python3
"""Verify real HTTP sessions and restart durability using a disposable H2 database.
Run after building the backend JAR. Uses Python's standard library only.
"""
import http.cookiejar
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
JAR = ROOT / 'apps/backend/target/backend-0.1.0-SNAPSHOT.jar'


def client(base, identity):
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def request(path, method='GET', body=None, status=200):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(base + path, data=data, method=method,
                                     headers={'Content-Type': 'application/json', 'X-StudyBuddy-Request': '1'})
        try:
            response = opener.open(req, timeout=10)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            value = json.loads(response.read())
            assert response.code == status, (path, response.code, value)
            return value

    request('/api/session', 'POST', {'accountId': identity})
    return request


def start(database, output):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen(['java', '-jar', str(JAR), f'--server.port={port}',
                                f'--spring.datasource.url=jdbc:h2:file:{database};DB_CLOSE_ON_EXIT=FALSE'],
                               cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
    base = f'http://127.0.0.1:{port}'
    for _ in range(150):
        if process.poll() is not None:
            raise RuntimeError('Backend stopped unexpectedly. Inspect the smoke-test log.')
        try:
            # Seeded choices prove both HTTP readiness and ApplicationRunner completion.
            with urllib.request.urlopen(base + '/api/session/accounts', timeout=1) as response:
                if len(json.loads(response.read())) >= 1:
                    return process, base
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(0.1)
    stop(process)
    raise TimeoutError('Backend did not become ready within 15 seconds.')


def stop(process):
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def main():
    if not JAR.exists():
        raise SystemExit('Build the backend first: cd apps/backend && ./mvnw package')
    process = None
    with tempfile.TemporaryDirectory(prefix='studybuddy-smoke-') as temp:
        folder = Path(temp)
        log = folder / 'backend.log'
        try:
            with log.open('w') as output:
                process, base = start(folder / 'database', output)
                a, b, admin = client(base, 'S001'), client(base, 'S002'), client(base, 'ADMIN001')
                assert len(a('/api/students')) == 50
                assert len(a('/api/students/courses')) == 10
                profile = a('/api/students/S001')
                profile['name'] = 'Restart verification student'
                a('/api/students', 'POST', profile)
                assert a('/api/students/S002')['contactNumber'] is None
                buddy = a('/api/connections/requests', 'POST', {'receiverId': 'S002', 'message': 'Durability check'})
                b(f"/api/connections/requests/{buddy['id']}/status?status=ACCEPTED", 'POST')
                assert a('/api/students/S002')['contactNumber'] is not None
                config = admin('/api/admin/matching-config')
                config['strategy'] = 'COURSE_FIRST'
                admin('/api/admin/matching-config', 'PUT', config)
                group = a('/api/groups')[0]
                group['name'] = 'Durable study circle'
                saved_group = a('/api/groups', 'POST', group)
                join = b(f"/api/groups/{saved_group['id']}/join-requests", 'POST')
                a(f"/api/groups/join-requests/{join['id']}/decision?decision=ACCEPTED", 'POST')
                admin('/api/admin/accounts/S050', 'DELETE')
                stop(process)
                process, base = start(folder / 'database', output)
                a, b, admin = client(base, 'S001'), client(base, 'S002'), client(base, 'ADMIN001')
                assert len(a('/api/students')) == 49, 'Deleted seed must not reappear on restart'
                assert a('/api/students/S001')['name'] == 'Restart verification student'
                assert a('/api/students/S002')['contactNumber'] is not None
                assert len(a('/api/connections/students/S001/active')) == 1
                assert admin('/api/admin/matching-config')['strategy'] == 'COURSE_FIRST'
                restored = next(g for g in a('/api/groups') if g['id'] == saved_group['id'])
                assert 'S002' in restored['memberIds']
                a(f"/api/connections/requests/{buddy['id']}/status?status=ENDED", 'POST')
                assert a('/api/students/S002')['contactNumber'] is None
                assert b('/api/students/S001')['contactNumber'] is None
                print('PASS: real HTTP sessions, 10 courses / 50 initial profiles, request privacy, and restart persistence')
                print('PASS: profile, accepted connection, group membership, matching settings, and account deletion survive restart')
        except Exception:
            print(log.read_text())
            raise
        finally:
            stop(process)


if __name__ == '__main__':
    main()

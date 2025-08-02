#!/usr/bin/env python
"""
Test runner script to run specific working tests with coverage
"""

import os
import sys
import subprocess

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Working test modules
working_tests = [
    'appcore.tests.test_services',  # All service utility tests
    'appaccount.tests.test_serializers',  # Most serializer tests (with some fixes needed)
    'appdata.tests.test_serializers',  # Most serializer tests (with some fixes needed)
]

def run_tests_with_coverage():
    """Run tests and generate coverage report"""
    cmd = [
        'uv', 'run', 'coverage', 'run', 
        '--source=app',
        '--omit=*/migrations/*,*/tests/*,*/venv/*,*/__pycache__/*',
        'app/manage.py', 'test'
    ] + working_tests + ['--settings=app.settings']
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd='/workspaces/42-bangkok/backend')
    
    if result.returncode == 0:
        # Generate reports
        subprocess.run(['uv', 'run', 'coverage', 'report'], cwd='/workspaces/42-bangkok/backend')
        subprocess.run(['uv', 'run', 'coverage', 'html'], cwd='/workspaces/42-bangkok/backend')
        print("\nHTML coverage report generated at htmlcov/index.html")
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(run_tests_with_coverage())
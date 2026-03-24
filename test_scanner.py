import os
import sys

# Add the parent directory to the path so we can import migration_tool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from migration_tool.core.scanner import RegistryScanner

def main():
    print("Testing Registry Scanner...")
    scanner = RegistryScanner()
    apps = scanner.scan()
    print(f"\nFound {len(apps)} applications.")
    
    print("\nSample of found apps:")
    for app in apps[:10]:
        print(f" - {app['name']} (v{app['version']}) by {app['publisher']}")

if __name__ == "__main__":
    main()

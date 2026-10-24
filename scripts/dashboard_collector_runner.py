"""Thin entrypoint so multiprocessing never re-executes the collector implementation."""
from dashboard_collector import main

if __name__ == '__main__':
    main()

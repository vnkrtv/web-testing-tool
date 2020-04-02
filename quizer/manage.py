#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import re
import pathlib


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizer.settings')
    running_tests = (sys.argv[1] == 'test')
    if running_tests:
        config_path = pathlib.Path('./quizer/main/config.py')
        with open(config_path, 'r') as file:
            config_file = list(file.readlines())
        buf = re.sub(r'[\'\s]', r'', config_file[-1]).split('=')
        db_name = buf[1]
        config_file[-1] = buf[0] + " = 'test_" + buf[1] + "'\n"
        with open(config_path, 'w') as file:
            file.write(''.join(config_file))

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    try:
        execute_from_command_line(sys.argv)
    finally:
        if running_tests:
            with open(config_path, 'r') as file:
                config_file = list(file.readlines())
            buf = re.sub(r'[\'\s]', r'', config_file[-1]).split('=')
            config_file[-1] = buf[0] + " = '" + db_name + "'\n"
            with open(config_path, 'w') as file:
                file.write(''.join(config_file))


if __name__ == '__main__':
    main()

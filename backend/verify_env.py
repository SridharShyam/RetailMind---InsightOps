import sys
try:
    import jinja2
    print(f"Jinja2 found: {jinja2.__version__}")
    import markupsafe
    print(f"MarkupSafe found: {markupsafe.__version__}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")

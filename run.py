import os
import sys
import threading
import multiprocessing
import webbrowser
from app import create_app

app = create_app(os.getenv('FLASK_ENV', 'development'))


def auto_open_browser(port: int):
    """Automatically launches the user's default browser after the server binds to the port."""
    import time
    time.sleep(1.2)
    try:
        webbrowser.open(f'http://127.0.0.1:{port}')
    except Exception:
        pass


if __name__ == '__main__':
    multiprocessing.freeze_support()
    port = int(os.getenv('PORT', 5000))
    print("\n" + "=" * 65)
    print("  EDUVERSE AI - Web Application Server")
    print(f"  Access URL : http://127.0.0.1:{port}")
    print("  Status     : Running")
    print("  IMPORTANT  : Keep this terminal window open while using EduVerse AI.")
    print("  To Stop    : Press CTRL+C in this terminal window.")
    print("=" * 65 + "\n")

    # Launch browser automatically
    threading.Thread(target=auto_open_browser, args=(port,), daemon=True).start()

    try:
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n[EduVerse AI] Server stopped cleanly.")

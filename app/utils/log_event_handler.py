from watchdog.events import FileSystemEventHandler


class LogEventHandler(FileSystemEventHandler):
    def __init__(self, monitor):
        self.monitor = monitor
        self.last_position = 0

    def on_modified(self, event):
        if not event.is_directory and event.src_path == self.monitor.log_file:
            try:
                with open(event.src_path, "r", encoding="utf-8") as file:
                    file.seek(self.last_position)
                    for line in file:
                        self.monitor.parse_log_line(line.strip())
                    self.last_position = file.tell()
            except Exception as e:
                print(f"Error reading modified log file: {e}")

    def on_created(self, event):
        # If it's the newly created log file
        if not event.is_directory and event.src_path == self.monitor.log_file:
            try:
                with open(event.src_path, "r", encoding="utf-8") as file:
                    for line in file:
                        self.monitor.parse_log_line(line.strip())
                    self.last_position = file.tell()
            except Exception as e:
                print(f"Error reading newly created log file: {e}")

"""NanoOS: a tiny educational operating-system simulator.

This is not a hardware kernel. It is a shell-driven simulation that models a
few familiar OS concepts:
- users and login
- a virtual file system
- process lifecycle and scheduling ticks
- simple memory accounting

Run with: python os_sim.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Process:
    pid: int
    owner: str
    name: str
    memory_mb: int
    status: str = "ready"
    cpu_time: int = 0


@dataclass
class NanoOS:
    total_memory_mb: int = 512
    users: Dict[str, str] = field(default_factory=lambda: {"root": "root"})
    files: Dict[str, str] = field(default_factory=lambda: {"/readme.txt": "Welcome to NanoOS"})
    next_pid: int = 1
    current_user: str = "root"
    processes: List[Process] = field(default_factory=list)

    def used_memory(self) -> int:
        return sum(proc.memory_mb for proc in self.processes if proc.status != "terminated")

    def available_memory(self) -> int:
        return self.total_memory_mb - self.used_memory()

    def add_user(self, username: str, password: str) -> str:
        if username in self.users:
            return f"User '{username}' already exists."
        self.users[username] = password
        return f"User '{username}' created."

    def login(self, username: str, password: str) -> str:
        if self.users.get(username) != password:
            return "Authentication failed."
        self.current_user = username
        return f"Logged in as {username}."

    def write_file(self, path: str, content: str) -> str:
        if not path.startswith("/"):
            return "Path must be absolute (start with /)."
        self.files[path] = content
        return f"Wrote {len(content)} bytes to {path}."

    def read_file(self, path: str) -> str:
        if path not in self.files:
            return f"File not found: {path}"
        return self.files[path]

    def list_files(self) -> str:
        return "\n".join(sorted(self.files.keys())) or "<empty>"

    def spawn(self, name: str, memory_mb: int) -> str:
        if memory_mb <= 0:
            return "Memory must be a positive integer."
        if memory_mb > self.available_memory():
            return f"Out of memory. Available: {self.available_memory()}MB"
        process = Process(
            pid=self.next_pid,
            owner=self.current_user,
            name=name,
            memory_mb=memory_mb,
        )
        self.next_pid += 1
        self.processes.append(process)
        return f"Started process pid={process.pid} name={process.name} mem={process.memory_mb}MB"

    def kill(self, pid: int) -> str:
        for process in self.processes:
            if process.pid == pid and process.status != "terminated":
                process.status = "terminated"
                return f"Process {pid} terminated."
        return f"No running process with pid {pid}."

    def tick(self) -> str:
        ready = [proc for proc in self.processes if proc.status == "ready"]
        if not ready:
            return "No runnable processes."
        selected = min(ready, key=lambda proc: proc.cpu_time)
        selected.status = "running"
        selected.cpu_time += 1
        selected.status = "ready"
        return f"Scheduler ran pid={selected.pid} ({selected.name}); cpu_time={selected.cpu_time}"

    def ps(self) -> str:
        live = [proc for proc in self.processes if proc.status != "terminated"]
        if not live:
            return "No active processes."
        lines = ["PID OWNER NAME STATUS MEM CPU"]
        for proc in live:
            lines.append(
                f"{proc.pid:>3} {proc.owner:<5} {proc.name:<12} {proc.status:<6} "
                f"{proc.memory_mb:>3} {proc.cpu_time:>3}"
            )
        return "\n".join(lines)

    def meminfo(self) -> str:
        used = self.used_memory()
        free = self.available_memory()
        return f"Total: {self.total_memory_mb}MB\nUsed:  {used}MB\nFree:  {free}MB"


HELP_TEXT = """Commands:
  help
  adduser <name> <password>
  login <name> <password>
  whoami
  ls
  cat <path>
  write <path> <content>
  spawn <name> <memory_mb>
  kill <pid>
  ps
  tick [count]
  meminfo
  shutdown
"""


def run_shell() -> None:
    os = NanoOS()
    print("NanoOS booted. Type 'help' for commands.")

    while True:
        raw = input(f"{os.current_user}@nano$ ").strip()
        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()

        if cmd == "help":
            print(HELP_TEXT)
        elif cmd == "adduser" and len(parts) == 3:
            print(os.add_user(parts[1], parts[2]))
        elif cmd == "login" and len(parts) == 3:
            print(os.login(parts[1], parts[2]))
        elif cmd == "whoami":
            print(os.current_user)
        elif cmd == "ls":
            print(os.list_files())
        elif cmd == "cat" and len(parts) == 2:
            print(os.read_file(parts[1]))
        elif cmd == "write" and len(parts) >= 3:
            path = parts[1]
            content = " ".join(parts[2:])
            print(os.write_file(path, content))
        elif cmd == "spawn" and len(parts) == 3:
            try:
                mem = int(parts[2])
            except ValueError:
                print("memory_mb must be an integer")
                continue
            print(os.spawn(parts[1], mem))
        elif cmd == "kill" and len(parts) == 2:
            try:
                pid = int(parts[1])
            except ValueError:
                print("pid must be an integer")
                continue
            print(os.kill(pid))
        elif cmd == "ps":
            print(os.ps())
        elif cmd == "tick":
            count = 1
            if len(parts) == 2:
                try:
                    count = max(1, int(parts[1]))
                except ValueError:
                    print("tick count must be an integer")
                    continue
            for _ in range(count):
                print(os.tick())
        elif cmd == "meminfo":
            print(os.meminfo())
        elif cmd == "shutdown":
            print("System halted.")
            break
        else:
            print("Unknown or malformed command. Type 'help'.")


if __name__ == "__main__":
    run_shell()

#!/usr/bin/env python3
"""myfetch: мінімалістичний системний огляд для Linux. Без зовнішніх залежностей."""

import getpass
import itertools
import os
import platform
import shutil
import socket
import sys

GB = 1024 ** 3


def read_os_name() -> str:
    try:
        with open("/etc/os-release", encoding="utf-8") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return "Linux"


def read_os_id() -> str:
    try:
        with open("/etc/os-release", encoding="utf-8") as f:
            for line in f:
                if line.startswith("ID="):
                    return line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return ""


LOGOS = {
    "arch": [
        "       /\\",
        "      /  \\",
        "     /\\   \\",
        "    /      \\",
        "   /   ,,   \\",
        "  /   |  |  -\\",
        " /_-''    ''-_\\",
    ],
    "ubuntu": [
        "          _",
        "      ---(_)",
        "  _/  ---  \\",
        " (_) |   |",
        "   \\  --- _/",
        "      ---(_)",
    ],
    "debian": [
        "  _____",
        " /  __ \\",
        "|  /    |",
        "|  \\___-",
        "-_",
        "  --_",
    ],
    "default": [
        "    .--.",
        "   |o_o |",
        "   |:_/ |",
        "  //   \\ \\",
        " (|     | )",
        "/'\\_   _/`\\",
        "\\___)=(___/",
    ],
}


def get_logo(os_id: str) -> list[str]:
    return LOGOS.get(os_id, LOGOS["default"])


def read_cpu() -> str:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "невідомо"


def read_memory() -> tuple[float, float]:
    """Повертає (використано, всього) у ГБ."""
    info = {}
    with open("/proc/meminfo", encoding="utf-8") as f:
        for line in f:
            key, value = line.split(":", 1)
            info[key] = int(value.split()[0])  # значення в kB
    total = info["MemTotal"] * 1024 / GB
    used = (info["MemTotal"] - info["MemAvailable"]) * 1024 / GB
    return used, total


def read_uptime() -> str:
    with open("/proc/uptime", encoding="utf-8") as f:
        seconds = int(float(f.read().split()[0]))
    hours, rest = divmod(seconds, 3600)
    minutes = rest // 60
    return f"{hours}г {minutes}хв"


def read_disk(path: str = "/") -> str:
    usage = shutil.disk_usage(path)
    percent = usage.used * 100 // usage.total
    return f"{usage.used / GB:.1f} / {usage.total / GB:.1f} ГБ ({percent}%)"


def read_shell() -> str:
    return os.path.basename(os.environ.get("SHELL", "невідомо"))


def main() -> None:
    use_color = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    accent = "\033[1;36m" if use_color else ""
    reset = "\033[0m" if use_color else ""

    user = getpass.getuser()
    host = socket.gethostname()
    used, total = read_memory()

    rows = [
        ("OS", read_os_name()),
        ("Kernel", platform.release()),
        ("Arch", platform.machine()),
        ("Uptime", read_uptime()),
        ("Shell", read_shell()),
        ("CPU", read_cpu()),
        ("RAM", f"{used:.1f} / {total:.1f} ГБ"),
        ("Disk", read_disk()),
    ]

    label_width = max(len(label) for label, _ in rows)
    header = f"{user}@{host}"

    info_lines = [f"{accent}{header}{reset}", "─" * len(header)]
    info_lines += [f"{accent}{label:<{label_width}}{reset}  {value}" for label, value in rows]

    logo = get_logo(read_os_id())
    logo_width = max(len(line) for line in logo) + 3

    for logo_line, info_line in itertools.zip_longest(logo, info_lines, fillvalue=""):
        print(f"{accent}{logo_line:<{logo_width}}{reset}{info_line}")


if __name__ == "__main__":
    main()


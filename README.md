<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=0,10,20,30,40&height=120&section=header&text=MASS%20ADMIN%20FINDER&fontSize=35&fontColor=fff&animation=fadeIn&fontY=35" width="100%"/>

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Requests](https://img.shields.io/badge/Library-Requests-orange.svg?style=flat-square)](https://pypi.org/project/requests/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=flat-square)]()
[![License](https://img.shields.io/badge/License-Educational-yellow.svg?style=flat-square)]()

</div>


# Mass Admin Page Finder

```
  __  __                  _
 |  \/  | __ _ ___ ___   / \   admin
 | |\/| |/ _` / __/ __| / _ \  finder
 | |  | | (_| \__ \__ \/ ___ \
 |_|  |_|\__,_|___/___/_/   \_\ by 6ickzone
```

A simple, fast, multi-threaded CLI tool to discover admin/login pages and common sensitive paths across a list of target domains. Built with Python and `requests`, with a live spinner and an interactive pause-on-hit prompt so you don't get flooded with results.

> ⚠️ **Disclaimer:** This tool is intended for authorized security testing only — your own assets, CTFs, or targets you have explicit written permission to test (e.g. bug bounty programs in scope). Scanning systems without authorization is illegal in most jurisdictions. The author is not responsible for misuse.

---

## Features

- **Multi-threaded scanning** — scan dozens of paths concurrently per target for speed.
- **Multi-target support** — feed it a list of domains and it scans them one by one.
- **Accurate status detection** — uses `allow_redirects=False` so real `301`/`302`/`307`/`308` responses are captured directly, instead of silently following redirect chains (which was the #1 cause of false "no results" in earlier versions).
- **Live spinner animation** — no more staring at a frozen terminal wondering if it's alive.
- **Pause-on-hit prompt** — the moment a valid path is found, the scan pauses and asks if you want to keep going, so you can react to interesting hits (like a 403-protected `/cpanel`) immediately instead of scrolling through a wall of output later.
- **SSL-bypass friendly** — `verify=False` with SSL warnings suppressed, so self-signed/misconfigured certs on targets won't crash the scan.
- **Clean, colorized output** — results are color-coded by status (200 / redirect / auth / forbidden).

---

## Requirements

- Python 3.7+
- [`requests`](https://pypi.org/project/requests/)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/6ickzone/admin-mass.git
   ```

2. Enter the project directory:
   ```bash
   cd admin-mass
   ```

3. **Install requirements**:
   ```bash
   pip install requests
   ```
   
---

## Usage

1. Prepare a **path list** (`path.txt`) — one path per line. Lines starting with `#` are treated as comments and skipped.

   ```
   wp-admin/
   admin/
   administrator/
   cpanel/
   login/
   wp-login.php
   ```

2. Prepare a **target list** (e.g. `target.txt`) — one domain per line (with or without `http(s)://`).

   ```
   example.com
   anotherdomain.com
   ```

3. Run the script:

   ```bash
   python3 admin_finder.py
   ```

4. Follow the prompts:

   ```
   Target list file (default: target.txt):
   Use HTTPS? (y/n, default y):
   Threads (default 50):
   ```

5. When a valid path is found, the scan pauses:

   ```
   [?] Found a hit. Continue scanning remaining paths? (Y/n):
   ```

   Hit `Enter` / `y` to keep scanning the current target, or `n` to stop and move on.

---

## 🧵 About threads

This tool uses Python's `concurrent.futures.ThreadPoolExecutor` to send multiple requests at the same time instead of one-by-one, which is what makes it "mass" scanning instead of a slow sequential checker.

- **`threads` = max concurrent requests** sent at once for the current target's path list.
- **Default is 50.** This is a safe middle ground for most single targets on decent hosting/network conditions.
- **Higher threads (100+)** = faster scans, but:
  - More load on your own network/CPU.
  - Higher chance of getting rate-limited, IP-banned, or WAF-blocked by the target.
  - Less "polite" if you're testing shared/production infrastructure.
- **Lower threads (10–20)** = slower but gentler — recommended when:
  - Scanning a production site you don't want to accidentally stress.
  - The target has visible rate-limiting or a WAF (Cloudflare, Sucuri, etc.) in front of it.
  - You're on a bug bounty program that has explicit rules about request rate.

Rule of thumb: start low, especially on real/live targets, and only raise thread count once you've confirmed the target can handle it without throwing errors or blocking your requests.

---

## Status Code Legend

| Status | Meaning |
|---|---|
| `200 OK` | Path exists and is directly accessible. |
| `301 / 302 / 307 / 308 REDIRECT` | Path exists but redirects elsewhere (e.g. HTTP → HTTPS, or to a login page). Shows the `Location` header so you can see exactly where it points. |
| `401 AUTH` | Path exists but requires authentication (HTTP Basic Auth). |
| `403 FORBIDDEN` | Path exists but access is blocked (often by server config or a WAF). |

Paths that time out, fail to connect, or raise other request errors are silently skipped and not shown in the results.

---

## How it works (short version)

1. Loads your path list and target list.
2. For each target, builds `base_url + path` combinations.
3. Fires them off concurrently through a thread pool with a custom `User-Agent`, SSL verification disabled, and redirects **not** auto-followed.
4. Each response is classified by status code and streamed back as results complete (not after the whole scan finishes).
5. On the first hit, the live spinner pauses and you're asked whether to continue — preventing silent "mass scan with zero feedback" syndrome while still processing results in parallel under the hood.

---

## Roadmap / Ideas

- [ ] Option to scan all targets without the per-hit prompt (silent/batch mode flag).
- [ ] Output results to a file (`.txt` / `.json` / `.csv`).
- [ ] Custom header / cookie / proxy support via CLI args.
- [ ] Rate-limiting / delay option between requests.

---

## Author

**6ickzone** (0x6ick)

---

## License

This project is licensed under the [WTFPL](LICENSE) — DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE

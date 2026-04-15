# Network Hardening Scanner

> Scan, assess, and remediate network misconfigurations — containerised, automated, and aligned with CIS Benchmarks.

[![Build Status](https://img.shields.io/github/actions/workflow/status/privsecops-lab/network-hardening-scanner/ci.yml?branch=main&style=flat-square)](https://github.com/privsecops-lab/network-hardening-scanner/actions)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://github.com/privsecops-lab/network-hardening-scanner)
[![Python](https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![CIS Benchmark](https://img.shields.io/badge/aligned-CIS%20Benchmark%20v8-orange?style=flat-square)](https://www.cisecurity.org/cis-benchmarks)

---

## What this does

Network Hardening Scanner is a Python CLI tool that audits a Linux host or Docker-based lab environment against a security hardening baseline. It enumerates open ports and running services, compares the live state against a configurable CIS Benchmark-aligned policy, scores each finding (PASS / WARN / FAIL), and outputs a self-contained HTML report with remediation guidance.

It is designed to run both manually and automatically — a GitHub Actions workflow runs the scanner against a deliberately misconfigured lab environment on every push to `main`, making security regression visible in CI.

**The problem it solves:** Manually checking hardening state is error-prone and rarely repeatable. This tool makes hardening assessment scriptable, diffable, and auditable.

---

## Quick start

```bash
# Clone the repo
git clone git@github.com:privsecops-lab/network-hardening-scanner.git
cd network-hardening-scanner

# Build and start the lab (scanner + target VM)
docker compose up --build

# Run the scanner against the target
docker compose exec scanner python scan.py --target lab-target --output report.html

# Open the report
open report.html   # or xdg-open on Linux
```

Requirements: Docker 24+, Docker Compose v2. No local Python installation needed.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 Docker Compose Lab               │
│                                                 │
│  ┌─────────────────┐     ┌───────────────────┐  │
│  │   scanner        │────▶│   lab-target      │  │
│  │  (Python CLI)   │     │  (Ubuntu 22.04)   │  │
│  │                 │     │  deliberately      │  │
│  │  • Nmap wrapper │     │  misconfigured:    │  │
│  │  • netstat parse│     │  • open ports      │  │
│  │  • baseline diff│     │  • weak SSH config │  │
│  │  • HTML reporter│     │  • exposed services│  │
│  └────────┬────────┘     └───────────────────┘  │
│           │                                      │
│           ▼                                      │
│  ┌─────────────────┐                            │
│  │  report.html    │  ← scored findings +        │
│  │  (self-contained│    remediation steps         │
│  └─────────────────┘                            │
└─────────────────────────────────────────────────┘

GitHub Actions runs this full scan on every push to main.
```

---

## How the scoring works

The scanner loads a **hardening baseline** from `baseline/policy.yaml` and compares it against live scan results. Each check produces one of three outcomes:

| Status | Meaning |
|--------|---------|
| ✅ PASS | Live state matches the expected secure configuration |
| ⚠️ WARN | Deviation detected but not immediately exploitable |
| ❌ FAIL | Clear misconfiguration — remediation required |

The overall score is a weighted percentage. FAIL findings carry 3× the weight of WARN findings.

### Example policy check (YAML)

```yaml
checks:
  - id: NET-001
    description: SSH should not permit root login
    category: SSH Hardening
    severity: FAIL
    check:
      type: file_contains
      path: /etc/ssh/sshd_config
      pattern: "PermitRootLogin no"

  - id: NET-002
    description: Port 23 (Telnet) should not be open
    category: Open Ports
    severity: FAIL
    check:
      type: port_closed
      port: 23
```

---

## Project structure

```
network-hardening-scanner/
├── scanner/
│   ├── scan.py            # CLI entrypoint
│   ├── nmap_wrapper.py    # Nmap scan execution and parsing
│   ├── netstat_parser.py  # Local service enumeration
│   ├── baseline_diff.py   # Compare live state vs policy
│   └── reporter.py        # HTML report generation
├── baseline/
│   └── policy.yaml        # Hardening checks (CIS-aligned)
├── lab/
│   ├── Dockerfile.target  # Deliberately misconfigured Ubuntu target
│   └── setup.sh           # Installs and misconfigures services
├── .github/
│   └── workflows/
│       └── ci.yml         # Runs scanner in CI on every push
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Standards alignment

Hardening checks are drawn from the following sources:

- **CIS Ubuntu Linux 22.04 LTS Benchmark v1.0** — SSH hardening, firewall rules, unnecessary services
- **NIST SP 800-123** — General server security principles
- **Docker CIS Benchmark v1.6** — Container-specific checks (applied to the scanner container itself)

Each policy check references its source control ID in `policy.yaml` for traceability.

---

## Roadmap

- [x] Docker Compose lab setup with misconfigured target
- [x] Nmap wrapper and port enumeration
- [x] YAML-based policy baseline
- [ ] Baseline diff engine and scoring
- [ ] HTML report generator
- [ ] GitHub Actions CI integration
- [ ] CIS SSH hardening checks (NET-001 through NET-012)
- [ ] Firewall rules assessment (ufw/iptables)
- [ ] JSON report export for downstream tooling
- [ ] Remediation auto-apply mode (optional, gated flag)

---

## Contributing

This is a team project. All changes go through pull requests — no direct pushes to `main`.

1. Pick an open issue from the [project board](https://github.com/orgs/privsecops-lab/projects/1)
2. Create a branch: `feat/issue-N-short-description`
3. Open a PR referencing the issue — one teammate must approve before merge
4. See [`.github/pull_request_template.md`](.github/pull_request_template.md) for the review checklist

---

## Team

| Contributor | Role |
|-------------|------|
| [Tolulope](https://github.com/ruthtolulope) | Baseline engine & scoring |
| [Osam](https://github.com/) | Network scanning module |
| [Daniel](https://github.com/) | Docker lab & CI pipeline |

---

## License

MIT — see [LICENSE](LICENSE).

---

*Part of the [PrivSecOps Lab](https://github.com/privsecops-lab) project portfolio.*

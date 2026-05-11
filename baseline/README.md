# Policy Baseline — Schema Reference

This folder contains the hardening policy used by the Network Hardening Scanner.
The scanner loads `policy.yaml`, compares it against live scan results, and scores
each check as PASS, WARN, or FAIL.

## Check schema

Every check in `policy.yaml` follows this structure:

```yaml
- id: NET-001
  description: SSH must not permit root login
  category: SSH Hardening
  severity: FAIL
  reference: CIS 5.2.8
  check:
    type: file_contains
    path: /etc/ssh/sshd_config
    expected: "PermitRootLogin no"
  remediation: >
    Set 'PermitRootLogin no' in /etc/ssh/sshd_config
    and restart SSH with: systemctl restart sshd
```

### Field definitions

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique check identifier. Format: `NET-XXX`, `PORT-XXX`, or `SVC-XXX` |
| `description` | Yes | Plain English description of what is being checked |
| `category` | Yes | Groups checks in the report: `SSH Hardening`, `Open Ports`, `Unnecessary Services` |
| `severity` | Yes | `FAIL` = directly exploitable · `WARN` = elevated risk, not immediately dangerous |
| `reference` | No | CIS Benchmark or NIST control ID this check maps to |
| `check` | Yes | The verification block — see check types below |
| `remediation` | No | Step-by-step fix instructions, shown in the HTML report |


## Check types

### `file_contains`
Checks whether a specific string exists in a configuration file on the target.

```yaml
check:
  type: file_contains
  path: /etc/ssh/sshd_config
  expected: "PermitRootLogin no"
```

| Parameter | Description |
|-----------|-------------|
| `path` | Absolute path to the file on the target system |
| `expected` | The exact string that must be present for the check to PASS |

### `port_closed`
Checks whether a specific TCP or UDP port is closed on the target.

```yaml
check:
  type: port_closed
  port: 23
  protocol: tcp
```

| Parameter | Description |
|-----------|-------------|
| `port` | Port number to check |
| `protocol` | `tcp` or `udp` |

---

### `service_stopped`
Checks whether a named service is not running on the target.

```yaml
check:
  type: service_stopped
  service: apache2
```

| Parameter | Description |
|-----------|-------------|
| `service` | The service name as it appears in `systemctl` or `service` commands |

---

## Severity levels

| Severity | Score weight | Meaning |
|----------|-------------|---------|
| `FAIL` | 3× | The system is directly exploitable or in clear violation of the benchmark |
| `WARN` | 1× | A deviation from best practice that raises risk but is not immediately critical |

The overall score is calculated as:
score = (passing checks)/(total checks weighted)*100

FAIL findings carry three times the weight of WARN findings, meaning a system
with any FAIL findings cannot achieve a high score even if most checks pass.

---

## Standards alignment

| Standard | Version | Sections used |
|----------|---------|--------------|
| CIS Ubuntu Linux 22.04 LTS Benchmark | v1.0 | 2.2 (Services), 3.5 (Ports), 5.2 (SSH) |
| NIST SP 800-123 | — | § 4.2 (Unnecessary services and ports) |

---

## Adding new checks

1. Choose the appropriate check type (`file_contains`, `port_closed`, `service_stopped`)
2. Assign the next available ID in the relevant series (`NET-`, `PORT-`, `SVC-`)
3. Set severity honestly — `FAIL` only if directly exploitable
4. Always include a `remediation` field — the report is only useful if it tells people how to fix things
5. Reference the CIS or NIST control if one exists

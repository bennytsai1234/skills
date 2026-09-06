# GPU Host Facts

## RTX 4090 Linux test host

- Host: `192.168.216.23`
- GPU: NVIDIA RTX 4090
- Admin/login user: `rateadm`
- Public Internet: available
- Typical role: Linux/GPU testing where external network access may be useful

## H200 Linux host

- Host: `192.168.151.216`
- GPU: NVIDIA H200
- Admin/login user: `benny`
- Public Internet: unavailable
- Typical role: H200 GPU workloads in the internal network

Do not assume public `pip`, GitHub, Hugging Face, `curl`, or `wget` access from H200.

## SSH key location

Known Windows key directory:

```text
C:\Users\045650\.ssh
```

WSL-visible equivalent when applicable:

```text
/mnt/c/Users/045650/.ssh
```

Inspect SSH config / available identity files before choosing an exact private key filename. Never copy private key contents into repository files or chat output.

## Direct login targets

```text
rateadm@192.168.216.23
benny@192.168.151.216
```

If live probing contradicts a non-secret fact in this reference, use the observed current state for the task and update this reference only when the human wants the reusable fact corrected.

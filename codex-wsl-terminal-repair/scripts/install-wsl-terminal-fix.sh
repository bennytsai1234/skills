#!/usr/bin/bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source_file="$script_dir/codex-wsl-sh-compat"
install_file=/usr/local/libexec/codex-wsl-sh-compat

sudo install -d -o root -g root -m 0755 /usr/local/libexec
sudo install -o root -g root -m 0755 "$source_file" "$install_file"
sudo ln -sfn "$install_file" /usr/bin/sh

test "$(readlink -f /bin/sh)" = "$install_file"
/bin/sh -c 'test "$((20 + 6))" -eq 26'
/usr/bin/git --version

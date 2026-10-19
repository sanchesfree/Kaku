`~/.ssh/config` is the per-user file `/usr/bin/ssh` reads for host aliases, users, ports, keys and jump hosts. Put each specific `Host` block above a final `Host *` block, because ssh keeps the first value it finds for a keyword, then check with `ssh -G` before connecting. Apple's OpenSSH adds `UseKeychain`, which the OpenBSD manual and OpenSSH 10.0's keyword list omit, so that line belongs with `/usr/bin/ssh`.

## A config you can check

ssh reads command-line options, then `~/.ssh/config`, then `/etc/ssh/ssh_config`. Keywords are case-insensitive and arguments are case-sensitive. A `#` line is a comment.

The manual recommends that `~/.ssh` be readable, writable and executable by you and not accessible by others, and that the config be read/write for you and not writable by others. ssh ignores a private key others can read. The control socket needs a directory others cannot write:

```bash
mkdir -p ~/.ssh/sockets
chmod 700 ~/.ssh ~/.ssh/sockets
chmod 600 ~/.ssh/config ~/.ssh/id_ed25519
```

`Include` with a relative path loads from `~/.ssh` at the line where it sits, so files in `~/.ssh/config.d/` are read before the blocks below. Specific aliases come next. `Host *` is last and only fills keywords those blocks left unset.

```
Include config.d/*

Host dev
    HostName 10.0.0.8
    User dev
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ProxyJump jump

Host jump
    HostName jump.example.com
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

Host *
    AddKeysToAgent yes
    UseKeychain yes
    IdentitiesOnly yes
    ServerAliveInterval 15
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%C
    ControlPersist 10m
```

`Host` is the name you type. `HostName` is the address ssh connects to, defaulting to that typed name. `User` is the remote account. `Port` defaults to 22. `ControlPersist` uses the `sshd_config` time format, where `10m` is ten minutes.

`ssh -G` prints the configuration after Host and Match blocks and exits without connecting. It prints the keywords in lowercase:

```bash
ssh -G dev | grep -E '^(hostname|user|port|identityfile|identitiesonly|proxyjump|controlmaster|controlpersist|serveraliveinterval|addkeystoagent) '
```

You want `hostname 10.0.0.8`, `user dev`, `port 2222`, `proxyjump jump`, and a single `identityfile` for `~/.ssh/id_ed25519`. `hostname dev` means the block did not match.

## How Host blocks are chosen

ssh walks those three sources from top to bottom and keeps the first value for each keyword. A `Host *` at the top sets `User` for every connection, and a later `User` line never replaces it. That is the reason for specific blocks first.

`Host` matches the command-line name. `*` matches any run of characters, `?` matches one, and a leading exclamation mark excludes a host. `Host dev jump` matches either name. The pattern sees the typed name. It sees `HostName` only when `CanonicalizeHostname` is on, which re-reads the file. The default is `no`.

`IdentityFile` appends. OpenSSH 10.0 adds the default paths, including `~/.ssh/id_ed25519`, only when that list is empty, so one `IdentityFile` on `Host dev` is the whole list for `dev`. Another on `Host *` is added for every host, which is why the global block in the sample has none. `IdentitiesOnly yes` offers the configured files and skips other agent keys. With no `IdentityFile`, those configured files are the defaults.

## Keys and the macOS keychain

`IdentityFile` accepts a private key, or a public key path when the agent already holds the matching private key.

On Apple's ssh, `UseKeychain` defaults to `no`. `yes` makes macOS search the keychain for the passphrase and store a correct one you type. `AddKeysToAgent` defaults to `no`. `yes` adds a key loaded from a file to a running agent, as `ssh-add` would, so the next connection finds it there.

Store the passphrase without opening a session:

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

`--apple-load-keychain` uses a passphrase already stored. `-K` and `-A` still do this unless `APPLE_SSH_ADD_BEHAVIOR` is `openssh`. The manual says a future macOS will require that variable for those short flags, and it warns unless the variable is `macos`.

`UseKeychain` is in Apple's `ssh_config` and absent from the [OpenBSD manual](https://man.openbsd.org/ssh_config) and from OpenSSH 10.0's keyword table. On macOS 27.0, `/usr/bin/ssh -V` reports `OpenSSH_10.3p1` with LibreSSL. Another `ssh` earlier on `PATH` can reject the keyword. `IgnoreUnknown` skips unknown options only when it appears before them:

```
IgnoreUnknown UseKeychain
```

## Jump hosts and connections that stay open

`ProxyJump jump` connects to that alias first, then forwards TCP to the destination. Commas separate extra hops. `none` disables it. `ProxyJump` and `ProxyCommand` compete, and the one obtained first blocks the other. Destination settings are not applied to the jump host, so `jump` has its own block for the user and the key. `ssh -J jump dev` is the command-line form, and those options apply to `dev`, not to the jump.

`ControlMaster auto` reuses a master when the socket exists, and opens a new connection otherwise. `ControlPath ~/.ssh/sockets/%C` keeps that socket in a directory others cannot write. `%C` hashes local host, remote host, port, user and `ProxyJump`. The manual recommends `%h`, `%p` and `%r`, or `%C`, so two destinations do not share a socket.

`ControlPersist 10m` leaves the master up after the first session closes and exits it after ten idle minutes. The default `no` closes it with that session. `yes` or `0` keeps it until it is killed or told to exit:

```bash
ssh -O check dev
ssh -O exit dev
```

`ServerAliveInterval 15` sends a keepalive through the encrypted channel after 15 seconds without data from the server. The default `0` sends none. `ServerAliveCountMax` defaults to 3, so this interval disconnects after about 45 seconds of silence. The manual says `TCPKeepAlive` can be spoofed because it sits outside that channel. A later `ssh`, `scp` or `sftp` can reuse the master, using the master's agent forwarding.

## When the connection still fails

If ssh asks for a password, others may be able to read the private key, so ssh skipped it. `ssh-add` skips that file too, and `chmod 600` on the key is the fix. A config someone else owns, or one with group or world write, makes OpenSSH 10.0 exit with `Bad owner or permissions on` and the path.

If the server drops the connection before the right key, the agent offered other identities first. `ssh -G` should then show `identitiesonly yes` and one `identityfile` line. If `ssh -O check` cannot reach a master, create `~/.ssh/sockets`, connect once, and check again. `ssh -O exit dev` clears a stuck master.

## What Kaku changes

`ssh dev` in a [Kaku](/docs/features) tab runs the `ssh` on your `PATH`, which reads this file. The tab title is an ssh glyph plus the host token from the command. `user@` is stripped, and so is a single trailing `:port` when the port is all digits, so `HostName 10.0.0.8` still leaves `dev` in the title. Kaku recognizes `ssh`, `mosh`, `autossh` and `et`.

`kaku init` wraps `ssh` in zsh and fish. With `TERM=kaku` the wrapper uses `TERM=xterm-256color`, since the remote host usually has no `kaku` terminfo entry. `KAKU_SSH_SKIP_TERM_FIX=1` turns that off. If `SSH_AUTH_SOCK` contains `1password` or `2BUA8C4S2C`, it adds `-o IdentitiesOnly=yes` unless you already passed `IdentitiesOnly` or set `KAKU_SSH_SKIP_1PASSWORD_FIX=1`. The zsh setup says this avoids too many authentication failures when 1Password offers every stored key. An existing `ssh` function is kept. A zsh alias becomes a function that still runs the alias command. `command ssh -G dev` skips the function.

`Cmd + Shift + R` mounts that session with sshfs at `~/Library/Caches/dev.kaku/sshfs/<host>` and opens yazi. It needs the `sshfs-mac` cask, macFUSE and the key login from `IdentityFile`. See the [Yazi setup](/blog/yazi-file-manager). A job that should survive a dropped link still belongs in tmux on the server, covered in [tmux on a Mac](/blog/tmux-alternative-mac). fzf completes `ssh **` then Tab with hosts from this file, `~/.ssh/known_hosts` and `/etc/hosts`, as in [fzf with zsh](/blog/fzf-zsh-mac).

With `ssh_domains` unset, each literal host name in `~/.ssh/config` and `/etc/ssh/ssh_config` also becomes a domain (patterns such as `Host *` do not): `SSH:host` with multiplexing off, and `SSHMUX:host` with Kaku's multiplexer. `Cmd + Shift + P` lists `Attach Domain` plus the name until it attaches, then `New Tab (Domain ...)`. `SSH:host` uses libssh by default and reads those files. That client does not support `ProxyJump` directly and expands `%j` to an empty string. A `ProxyCommand` still runs. `SSHMUX:host` runs `wezterm cli --prefer-mux proxy` remotely unless `remote_wezterm_path` or `override_proxy_command` is set, so that machine needs a `wezterm` binary.

## FAQ

### Do scp, sftp and git use this file?

`scp` copies over ssh and passes `-F` through. `sftp` takes the same `-F`. `git fetch` and `git push` run `ssh` unless `core.sshCommand` or `GIT_SSH_COMMAND` replaces it, so a `Host github.com` block applies to `git@github.com`.

### What if `ssh -V` is not Apple's OpenSSH?

Leave `UseKeychain` out, or put `IgnoreUnknown UseKeychain` above it. `AddKeysToAgent` is valid upstream. `ssh-add --apple-use-keychain` is Apple's `ssh-add`, next to `APPLE_SSH_ADD_BEHAVIOR` in its manual.

### Where do included files sit in the match order?

`Include config.d/*` expands in lexical order from `~/.ssh`, at that line. A `Host` block in an included file takes the `Include` line's place, so a `Host *` above it has already kept any keyword it set.

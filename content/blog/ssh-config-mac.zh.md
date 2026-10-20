`~/.ssh/config` 是 Mac 上 `/usr/bin/ssh` 用来记住主机别名、登录用户、端口、密钥和跳板的个人配置，具体的 `Host` 块要写在最后的 `Host *` 前面，因为每个关键字 ssh 只留下先读到的那个值。写完先跑 `ssh -G` 看生效结果，不必先连上去。Apple 的 OpenSSH 另外有 `UseKeychain`，OpenBSD 的手册和 OpenSSH 10.0 的关键字表里都没有这一项，所以它只跟系统自带的 `/usr/bin/ssh` 一起用。

## 一份可以核对的配置

ssh 先读命令行参数，再读 `~/.ssh/config`，最后读 `/etc/ssh/ssh_config`。关键字不区分大小写，参数区分大小写，以 `#` 开头的行是注释。

手册对 `~/.ssh` 的要求是只有你能读、能写、能进入，别人进不去，配置文件则是你自己可读写，别人不能写。私钥只要别人读得到，ssh 就会直接跳过。控制套接字还得放在一个别人不能写的目录里。

```bash
mkdir -p ~/.ssh/sockets
chmod 700 ~/.ssh ~/.ssh/sockets
chmod 600 ~/.ssh/config ~/.ssh/id_ed25519
```

`Include` 写相对路径时，从 `~/.ssh` 里找，并且就在这一行的位置插入，所以 `~/.ssh/config.d/` 里的主机块会排在下面这些块之前。接着写具体别名，`Host *` 放在最后，只补前面没写过的关键字。

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

`Host` 是你在命令行上敲的名字，`HostName` 才是真正要连的地址，不写的话就用你敲的那个名字。`User` 是远端账号，`Port` 默认 22。`ControlPersist` 用的是 `sshd_config` 里的时间写法，`10m` 就是十分钟。

`ssh -G` 会在套用 Host 和 Match 之后把配置打出来，然后退出，不会去连，打出来的关键字是小写的。

```bash
ssh -G dev | grep -E '^(hostname|user|port|identityfile|identitiesonly|proxyjump|controlmaster|controlpersist|serveraliveinterval|addkeystoagent) '
```

这里应该看到 `hostname 10.0.0.8`、`user dev`、`port 2222`、`proxyjump jump`，以及一行指向 `~/.ssh/id_ed25519` 的 `identityfile`。如果 `hostname` 还是 `dev`，说明 `Host dev` 没匹配上。

## Host 块按什么顺序生效

ssh 顺着命令行、用户配置、系统配置从上往下走，每个关键字只留第一次得到的值。`Host *` 如果写在文件顶上，它设过的 `User` 会套到后面每一次连接上，再往下写的 `User` 改不掉，所以具体主机要放在前面。

`Host` 匹配的是命令行上的名字，`*` 匹配任意一串字符，`?` 匹配一个字符，模式前面加感叹号表示排除。`Host dev jump` 两个名字都匹配，中间用空白分开。这个模式看的是你敲进去的名字，只有打开 `CanonicalizeHostname` 时才会改用 `HostName` 再读一遍文件，这项默认是 `no`。

`IdentityFile` 是例外，每写一次就往列表里加一个密钥。OpenSSH 10.0 只在这份列表还是空的时候，才会放进默认路径，其中包含 `~/.ssh/id_ed25519`，所以 `Host dev` 上写了一条 `IdentityFile`，`dev` 的密钥列表就只剩这一条。`Host *` 里再写一条，会加到每一个主机上，示例里的全局块因此不写 `IdentityFile`。`IdentitiesOnly yes` 只拿出已经配置的这些身份文件，代理里另外的密钥不再拿去试。某个主机自己没写 `IdentityFile` 时，配置好的文件就是那几把默认钥匙。

## 密钥和 macOS 钥匙串

`IdentityFile` 可以指向私钥，也可以指向公钥路径，只要对应的私钥已经在代理里。

Apple 的 ssh 里 `UseKeychain` 默认是 `no`，写成 `yes` 之后，macOS 会到钥匙串里找这个密钥的口令，你输入并且核对通过之后，口令会存进钥匙串。`AddKeysToAgent` 默认也是 `no`，写成 `yes` 时，从文件读入的密钥会加进正在跑的代理，效果和跑了 `ssh-add` 一样，下一次连接就能在代理里找到它。

不想等下一次连接，也可以直接把口令存进去。

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

`--apple-load-keychain` 用钥匙串里已经有的口令把身份加进代理。更早的 `-K` 和 `-A` 现在还是这个行为，除非把 `APPLE_SSH_ADD_BEHAVIOR` 设成 `openssh`。手册写了，以后的 macOS 会要求先设这个变量，短参数才会继续有效，变量不是 `macos` 时还会打出警告。

`UseKeychain` 写在 Apple 的 `ssh_config` 手册里，[OpenBSD 的手册](https://man.openbsd.org/ssh_config)和 OpenSSH 10.0 的关键字表里都没有。macOS 27.0 上 `/usr/bin/ssh -V` 报的是 `OpenSSH_10.3p1`，链的是 LibreSSL。`PATH` 里更靠前的另一个 `ssh` 可能会把这个关键字当成不认识。`IgnoreUnknown` 只能放过写在它后面的未知项，所以要放在最前。

```
IgnoreUnknown UseKeychain
```

## 跳板、复用和保活

`ProxyJump jump` 会先连上 `jump` 这个别名，再从那里把 TCP 转到最终主机，多跳之间用逗号分开，写成 `none` 就关掉。`ProxyJump` 和 `ProxyCommand` 谁先被读到，谁就把另一个挡住。目标主机上的配置不会套到跳板主机上，所以 `jump` 要有自己的 `Host` 块来写用户和密钥。命令行上的写法是 `ssh -J jump dev`，这些参数作用在 `dev` 上，跳板自己的用户和密钥仍然要写在 `jump` 的块里。

`ControlMaster auto` 在套接字已经存在时复用主连接，没有就新开一条。`ControlPath ~/.ssh/sockets/%C` 把套接字放在别人不能写的目录里，`%C` 是本地主机、远端主机、端口、用户和 `ProxyJump` 的哈希。手册建议路径里至少有 `%h`、`%p` 和 `%r`，或者用 `%C`，避免两台机器共用一个套接字。

`ControlPersist 10m` 会在第一个会话关掉之后把主连接留在后台，空闲十分钟再退出。默认的 `no` 是第一个会话结束主连接也结束，`yes` 或 `0` 会一直留到你杀掉它，或者明确让它退出。

```bash
ssh -O check dev
ssh -O exit dev
```

`ServerAliveInterval 15` 会在 15 秒没收到服务器数据时，从加密通道里发一条保活。默认 `0` 是不发。`ServerAliveCountMax` 默认 3，所以间隔设成 15 时，大约 45 秒没有回应就会断开。手册说 `TCPKeepAlive` 可以被伪造，因为它在加密通道外面。后面的 `ssh`、`scp`、`sftp` 可以搭上这条主连接，代理转发用的也是主连接那一份。

## 连不上的时候

ssh 忽然来要密码，可以检查私钥权限，别人也能读的私钥会被跳过。`ssh-add` 同样会跳过这种文件，对私钥执行 `chmod 600` 就符合手册。配置文件主人不是你，或者组和其他人有写权限时，OpenSSH 10.0 会以 `Bad owner or permissions on` 加上路径退出。

服务器在试到正确的密钥之前就把连接断掉，是代理先把别的身份送了上去。改完之后 `ssh -G` 应该出现 `identitiesonly yes`，并且只有一行 `identityfile`。`ssh -O check` 连不上主连接时，先建好 `~/.ssh/sockets`，连一次再查。卡住的主连接用 `ssh -O exit dev` 清掉。

## 在 Kaku 里会多出什么

在 [Kaku](/zh/docs/features) 的标签里敲 `ssh dev`，跑的是 `PATH` 上的那个 `ssh`，读的还是这份文件。标签标题是一个 ssh 图标，加上命令行里的主机名，`user@` 会被去掉，端口全是数字时末尾单独的 `:port` 也会去掉，所以 `HostName` 写成 `10.0.0.8`，标题上仍然是 `dev`。`ssh`、`mosh`、`autossh`、`et` 都会被认成远程命令。

`kaku init` 给 zsh 和 fish 包了一层 `ssh`。`TERM` 是 `kaku` 时，这层包装会改成 `TERM=xterm-256color` 再执行，因为远端通常没有 `kaku` 的 terminfo，设 `KAKU_SSH_SKIP_TERM_FIX=1` 可以关掉。`SSH_AUTH_SOCK` 里含有 `1password` 或 `2BUA8C4S2C` 时，它会加上 `-o IdentitiesOnly=yes`。你已经传了 `IdentitiesOnly`，或者设了 `KAKU_SSH_SKIP_1PASSWORD_FIX=1` 时，它不加。zsh 这段安装脚本写明，这是为了避开 1Password 把存着的密钥全部拿出来、导致认证失败次数过多。你自己定义过的 `ssh` 函数会留着不动，zsh 里的 `ssh` 别名会被换成一个函数，里面仍然跑原来的命令。`command ssh -G dev` 会绕开这个函数。

`Cmd + Shift + R` 用 sshfs 把当前 SSH 会话挂到 `~/Library/Caches/dev.kaku/sshfs/<host>`，再在 yazi 里打开。它需要 `sshfs-mac` 这个 cask、macFUSE，以及 `IdentityFile` 配好的密钥登录。挂载的细节在 [Yazi 的安装](/zh/blog/yazi-file-manager)。断线之后还想留着的进程，得在服务器上用 tmux，[在 Mac 上用 tmux](/zh/blog/tmux-alternative-mac) 写的是这件事。fzf 的 zsh 集成里，`ssh **` 再按 Tab，补全的主机来自这份配置、`~/.ssh/known_hosts` 和 `/etc/hosts`，[给 zsh 配 fzf](/zh/blog/fzf-zsh-mac) 会把快捷键接上。

没设置 `ssh_domains` 时，`~/.ssh/config` 和 `/etc/ssh/ssh_config` 里每个写死的主机名还会变成一个域（`Host *` 这类模式不算）。`SSH:host` 关闭复用，`SSHMUX:host` 走 Kaku 的复用。`Cmd + Shift + P` 打开 Command Palette，域还没挂上时列出 `Attach Domain` 加名字，挂上之后变成 `New Tab (Domain ...)`。`SSH:host` 默认用 libssh，并且会读这两份配置。这个客户端不直接支持 `ProxyJump`，并把 `%j` 展开成空字符串，`ProxyCommand` 则会照样执行。`SSHMUX:host` 在远端跑的是 `wezterm cli --prefer-mux proxy`。除非设了 `remote_wezterm_path` 或 `override_proxy_command`，那台机器上得有 `wezterm`。

## 常见问题

### scp、sftp 和 git 会读这个文件吗？

`scp` 通过 ssh 传文件，并且把 `-F` 转给 ssh。`sftp` 也有同样的 `-F`。`git fetch` 和 `git push` 默认跑 `ssh`。只有设了 `core.sshCommand` 或 `GIT_SSH_COMMAND` 才会换成别的命令，所以 `Host github.com` 会作用到 `git@github.com`。

### ssh -V 不是 Apple 的 OpenSSH 怎么办？

拿掉 `UseKeychain`，或者在它前面写 `IgnoreUnknown UseKeychain`。`AddKeysToAgent` 在上游 OpenSSH 里就有。`ssh-add --apple-use-keychain` 是 Apple 的 `ssh-add` 参数，和 `APPLE_SSH_ADD_BEHAVIOR` 写在同一本手册里。

### 被 Include 进来的文件排在匹配的哪一步？

`Include config.d/*` 按字典序展开，路径相对 `~/.ssh`，位置就是这一行所在的地方。被包含文件里的 `Host` 块插在这一行，写在 `Include` 上面的 `Host *` 已经留下的关键字不会被后面改掉。

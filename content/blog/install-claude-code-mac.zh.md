在 Mac 上装 Claude Code，用原生安装程序 `curl -fsSL https://claude.ai/install.sh | bash`，或者用 Homebrew `brew install --cask claude-code`。到项目目录里新开一个终端，跑 `claude`，在浏览器里用 Pro、Max、Team 或 Enterprise 订阅登录，Console 账号也行。原生安装会在后台自己更新，想立刻装上就跑 `claude update`。Homebrew 装的不会自动更新，升级命令是 `brew upgrade claude-code`（2026 年 10 月核对过）。

## 几种装法

Claude Code 要 macOS 13.0 或更高版本、4 GB 以上内存、x64 或 ARM64，还得能上网。官方推荐原生安装，见[高级设置](https://code.claude.com/docs/zh-CN/setup)，下载时看不到进度，装完新开一个终端，跑 `claude --version`。

默认渠道是 latest：

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

stable 通常比 latest 晚大约一周，会跳过有重大回归的版本。这里传的渠道，之后自动更新也按它来：

```bash
curl -fsSL https://claude.ai/install.sh | bash -s stable
```

Homebrew 按 cask 名字选渠道，`claude-code` 跟着 stable，`claude-code@latest` 跟着 latest：

```bash
brew install --cask claude-code
brew install --cask claude-code@latest
```

npm 装的是同一份原生二进制，它要 Node.js 22 或更高，更老的 Node 会打出 `EBADENGINE`，安装照样完成，因为 `claude` 并不跑在 Node 上。装的时候别关掉 npm 的可选依赖，也别用 `sudo npm install -g`，权限和安全都会出问题。

```bash
npm install -g @anthropic-ai/claude-code
```

shell 说找不到 `claude`，是安装目录还没进 `PATH`，原生启动器 `~/.local/bin/claude` 是指向 `~/.local/share/claude/versions/` 的符号链接。

## 登录

`claude` 在当前目录启动，第一次会把你带到浏览器。免费的 claude.ai 方案不含 Claude Code，Pro、Max、Team、Enterprise 和 Console 才有。Console 账号走的是 API，花的是预付的额度，第一次用 Console 登录会建一个名叫「Claude Code」的工作区。Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 也能用。

设了 `ANTHROPIC_API_KEY`，问到时确认用这把密钥，就会跳过登录提示。`claude auth login --console` 走 Console 计费，不走订阅，会话里用 `/login` 换账号，登录之后凭据会存下来，细节见[快速入门](https://code.claude.com/docs/zh-CN/quickstart)。

## 确认装好了

`claude doctor` 不进入会话，会打印安装是否正常、设置文件校验出的错误、可以怎么改，以及上次尝试更新的结果。会话里跑 `/doctor`，它能直接按这些建议帮你改好。

## 更新和发布渠道

原生安装在启动时查更新，跑着的时候也会隔一阵再查，新版本在后台下好，下次启动 Claude Code 才换上去。`claude update` 会立刻装上，有新版本就打印 `Successfully updated from <old version> to version <new version>`，已经是最新就打印 `Claude Code is up to date (<version>)`，Homebrew 装的打印 `Claude is up to date!`。

升级你装的那个 cask：

```bash
brew upgrade claude-code
brew upgrade claude-code@latest
```

把 `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE` 设成 `1`，有新版本时 Claude Code 会在后台跑这条升级，成功之后提示你重启。cask 里还没有这个版本的时候，你也可能先收到更新提示，升级失败就等一等再试。

npm 在全局目录可写时会自己更新，目录不可写就在启动时提示一次，`claude doctor` 会列出改法。升级用 `npm install -g @anthropic-ai/claude-code@latest`，别用 `npm update -g`，它可能停在旧的 semver 范围上。

原生安装里，`autoUpdatesChannel` 决定自动更新和 `claude update` 走哪条渠道，`"latest"` 是默认，`"stable"` 通常晚大约一周。在 `/config` 的 Auto-update channel 里改，或者写进 `~/.claude/settings.json`：

```json
{
  "autoUpdatesChannel": "stable"
}
```

`claude install stable` 和 `claude install latest` 会把原生二进制装到对应渠道，Homebrew 不看 `autoUpdatesChannel`，跟着 cask 名字走。新模型有时要 stable 渠道里还没有的版本，想用就换到 latest。

要停掉原生安装或 npm 安装的后台检查，把 `DISABLE_AUTOUPDATER` 设成 `"1"`：

```json
{
  "env": {
    "DISABLE_AUTOUPDATER": "1"
  }
}
```

这时 `claude doctor` 的 Auto-updates 那一行应该显示 `disabled (set by env: DISABLE_AUTOUPDATER)`。`claude update` 和 `claude install` 还能用，把 `DISABLE_UPDATES` 也设上，这两条才会一起停。

## 卸载，或从 npm 换到原生安装程序

删掉原生安装：

```bash
rm -f ~/.local/bin/claude
rm -rf ~/.local/share/claude
```

Homebrew 用 `brew uninstall --cask claude-code`，装的是 latest 那个 cask 就用 `brew uninstall --cask claude-code@latest`，npm 用 `npm uninstall -g @anthropic-ai/claude-code`。

从 npm 换到原生安装程序，先卸掉 npm 包，再跑 `curl -fsSL https://claude.ai/install.sh | bash`，然后新开一个终端跑 `claude --version`，`~/.claude` 留着，设置和会话历史都还在。要是想彻底清干净，再删掉 `~/.claude` 和 `~/.claude.json`，设置、允许的工具、MCP 服务器配置和会话历史会一起清掉。VS Code 扩展、JetBrains 插件和 Desktop app 下次跑起来会把这个目录再建出来。要是 `claude` 还能启动，多半还有第二份安装，或者 shell 里留着别名。

## 换行和通知

按 Enter 会把当前输入发出去，`Ctrl + J`，或者先输入 `\` 再按 Enter，在每个终端里都是插入换行。哪些终端里 `Shift + Enter` 不用设置就能换行，哪些要先跑一次 `/terminal-setup`，[Claude Code 用什么终端最好](/zh/blog/best-terminal-for-claude-code)那篇都列了，在 VS Code、Cursor 和 Devin Desktop 里 `/terminal-setup` 还会把 `terminal.integrated.gpuAcceleration` 设成 `"off"`，改回 `"auto"` 再重载窗口就能撤掉。桌面通知默认只在 Ghostty、Kitty 和 iTerm2 里发，其他终端怎么设，iTerm2 要打开哪个选项，SSH 和 [tmux](/zh/blog/tmux-alternative-mac) 里是什么情况，[通知指南](/zh/blog/claude-code-notifications)里都写了。

## 在 Kaku 里

Kaku 0.25.0 及以上配 Claude Code 2.1.295 及以上不用任何设置，0.25.0 之前的 Kaku 要在 `~/.claude/settings.json` 里设上 `"preferredNotifChannel": "ghostty"`，为什么这样，以及一条都收不到时该查什么，见[通知指南](/zh/blog/claude-code-notifications)。

`Shift + Enter` 和 `Cmd + Enter` 在输入框里插入换行。

`kaku ai` 打开 AI 设置面板，可以配置 Claude Code、Codex、Gemini CLI、Copilot CLI 和 Kimi Code，看它们的套餐用量，也能把 Kaku Assistant 配好。只有你在这个面板里改过，Kaku 才会去改对应工具的设置，你自己写的字段会留着，它也不会自己往 agent 里加 hook 或指令。

```bash
kaku ai
```

## 常见问题

### 免费的 Claude 方案包含 Claude Code 吗？

不含，要有 Pro、Max、Team、Enterprise 或 Console 账号，免费的 claude.ai 方案没有 Claude Code。

### Homebrew 会自己更新 Claude Code 吗？

不会，升级得跑 `brew upgrade claude-code` 或 `brew upgrade claude-code@latest`。把 `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE` 设成 `1`，Claude Code 会在后台跑这条升级。

### 为什么 shell 说找不到 claude？

新开一个终端跑 `claude --version`，原生启动器是 `~/.local/bin/claude`。

### Shift + Enter 把消息发出去了，换行怎么打？

`Ctrl + J`，或者 `\` 然后 Enter，每个终端都能用。`Shift + Enter` 不能换行的地方，在 tmux 外面跑一次 `/terminal-setup`，VS Code、Cursor、Devin Desktop、0.16 之前的 Alacritty 和 Zed 都是这样。

### 怎么让 Claude Code 不再自己更新？

原生安装或 npm 安装，在 `~/.claude/settings.json` 的 `env` 里把 `DISABLE_AUTOUPDATER` 设成 `"1"`，后台检查就停了，`claude update` 还是会跑，直到再设上 `DISABLE_UPDATES`。

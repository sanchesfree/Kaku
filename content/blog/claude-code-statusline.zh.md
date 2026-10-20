把 `~/.claude/settings.json` 里的 `statusLine` 设成一条 shell 命令就行，Claude Code 会把当前会话的 JSON 从 stdin 喂给它，再把脚本打到 stdout 的内容画在屏幕底部、页脚徽章上方的那一行，`/statusline` 也能生成脚本并把这项设置写进去。内容按 2026 年 10 月的[状态栏文档](https://code.claude.com/docs/zh-CN/statusline)核对过。

## 配上状态栏

`/statusline` 会在 `~/.claude/` 下写一份脚本，并改你的设置，它问要不要改文件时，确认一下就行。

```text
/statusline show model name and context percentage with a progress bar
```

也可以自己改 `~/.claude/settings.json`，或者改[项目设置](https://code.claude.com/docs/zh-CN/settings#where-settings-live)。`type` 是 `"command"`，`command` 是脚本路径或一行 shell 命令，`padding` 是额外缩进的字符数，默认 `0`。

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 2
  }
}
```

`PATH` 里有 [`jq`](https://jqlang.org/) 的话，不用单独放脚本：

```json
{
  "statusLine": {
    "type": "command",
    "command": "jq -r '\"[\\(.model.display_name)] \\(.context_window.used_percentage // 0)% context\"'"
  }
}
```

`refreshInterval` 还会每 N 秒再跑一次，最小是 `1`。`hideVimModeIndicator` 设成 `true` 时，只要脚本打出 `vim.mode`，内置的 `-- INSERT --` 就藏起来，`vim.mode` 的取值是 `NORMAL`、`INSERT`、`VISUAL` 或 `VISUAL LINE`，`vim` 这个对象只有开了 vim 模式才有。

保存文件会重新加载设置，并马上跑一次命令，想去掉这一行，用 `/statusline delete`、`/statusline clear` 或 `/statusline remove it`。

设了状态栏之后，Claude Code 会藏起大部分页脚提示，包括 `esc to interrupt`、`? for shortcuts` 和 `hold space to speak`，帮助菜单和权限确认出现时，这一行也会藏起来。[ccstatusline](https://github.com/sirmalloc/ccstatusline) 和 [starship-claude](https://github.com/martinemde/starship-claude) 是两套现成配置。

## JSON 里有什么

| 字段 | 是什么 |
|---|---|
| `model.display_name`、`model.id` | 当前模型的名字和 id |
| `workspace.current_dir` | 工作目录，`cwd` 跟它相同，优先用这个 |
| `workspace.project_dir` | 启动 Claude Code 时的目录 |
| `context_window.used_percentage` | 已用上下文的百分比，一开始可能是 `null` |
| `context_window.context_window_size` | token 上限，200000，开了扩展上下文则是 1000000 |
| `cost.total_cost_usd` | 这次会话的估算费用，美元 |
| `cost.total_duration_ms` | 会话已经跑了多少毫秒，按实际时间算 |
| `session_id` | 这次会话固定不变的 id |

[[figure:claude-code-statusline|会话 JSON 从 stdin 进脚本，打出来的那一行显示在输入区下面|分支不在这份 JSON 里，脚本自己去问 git。]]

`used_percentage` 把 `input_tokens`、`cache_creation_input_tokens` 和 `cache_read_input_tokens` 加在一起，不算 `output_tokens`，第一次 API 响应之前，`total_input_tokens` 和 `total_output_tokens` 都是 `0`。`current_usage` 在第一次调用前是 `null`，`/compact` 之后、下一次调用之前又是 `null`，百分比为 null 时 `// 0` 会换成 0。几条消息之后这一行还显示 `--`，就得重启会话。`/context` 显示的可能更高，因为它把那次响应之后新加的消息也估算进去了。

`cost.total_cost_usd` 是客户端按标价估的，除非用了 [`modelPricing`](https://code.claude.com/docs/zh-CN/settings-reference#modelpricing) 这张表，数字和账单可能对不上。`/clear` 会把它重置成 $0，v2.1.211 之前这个总数会留下来。`total_duration_ms` 在恢复会话之后继续累加，会话没在跑的时间不算，`total_api_duration_ms` 是等 API 的时间。脚本本身不花 token。

没有哪个字段是当前检出的分支，`workspace.git_worktree` 记的是 `git worktree add` 建出来的链接工作树的名字，`worktree.branch` 只在 worktree 会话里才有。

## 模型、上下文和 git 分支

脚本打出模型、文件夹、上下文百分比和分支，对 `git diff --cached --numstat` 和 `git diff --numstat` 做 `wc -l`，数的是已跟踪文件的个数，每个文件占一行，前一个是暂存的，后一个是改过的。`\033[32m` 是绿色的 `+`，`\033[33m` 是黄色的 `~`，`\033[0m` 把颜色复位，这些要 `echo -e` 才上色。

git 的结果缓存在 `/tmp/statusline-git-cache-$SESSION_ID`，5 秒内不重新跑，`session_id` 一次会话里不变，换成 `$$` 的话每次进程号都变，缓存永远用不上。`stat` 先跑 Linux 的 `stat -c %Y`，再跑 macOS 的 `stat -f %m`，在 Linux 上如果先跑 macOS 那种，它失败前会先打出一份文件系统报告。git 看的是脚本自己的目录，例子没有 `cd` 到 `workspace.current_dir`，`git branch --show-current` 为空就不显示分支。

```bash
#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
DIR=$(echo "$input" | jq -r '.workspace.current_dir')
SESSION_ID=$(echo "$input" | jq -r '.session_id')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

GREEN='\033[32m'
YELLOW='\033[33m'
RESET='\033[0m'

CACHE_FILE="/tmp/statusline-git-cache-$SESSION_ID"
CACHE_MAX_AGE=5

cache_is_stale() {
  [ ! -f "$CACHE_FILE" ] || \
  [ $(($(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || stat -f %m "$CACHE_FILE" 2>/dev/null || echo 0))) -gt $CACHE_MAX_AGE ]
}

if cache_is_stale; then
  if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    STAGED=$(git diff --cached --numstat 2>/dev/null | wc -l | tr -d ' ')
    MODIFIED=$(git diff --numstat 2>/dev/null | wc -l | tr -d ' ')
    echo "$BRANCH|$STAGED|$MODIFIED" > "$CACHE_FILE"
  else
    echo "||" > "$CACHE_FILE"
  fi
fi

IFS='|' read -r BRANCH STAGED MODIFIED < "$CACHE_FILE"

if [ -n "$BRANCH" ]; then
  GIT_STATUS=""
  [ "$STAGED" -gt 0 ] && GIT_STATUS="${GREEN}+${STAGED}${RESET}"
  [ "$MODIFIED" -gt 0 ] && GIT_STATUS="${GIT_STATUS}${YELLOW}~${MODIFIED}${RESET}"
  echo -e "[$MODEL] ${DIR##*/} | ${PCT}% | $BRANCH $GIT_STATUS"
else
  echo "[$MODEL] ${DIR##*/} | ${PCT}%"
fi
```

`${DIR##*/}` 是文件夹名，`cut -d. -f1` 去掉小数，存成 `~/.claude/statusline.sh`，再 `chmod +x`。

```bash
echo '{"model":{"display_name":"Opus"},"workspace":{"current_dir":"/home/user/project"},"context_window":{"used_percentage":25},"session_id":"test-session-abc"}' | ./statusline.sh
```

得到的是 `[Opus] project | 25%`，脚本所在目录里 `git rev-parse --git-dir` 成功的话，后面还会带上分支。宽度用 `$COLUMNS` 和 `$LINES`，`tput cols` 看不到终端，因为 stdout 被接走了。

## 颜色和图标

不到 70% 用绿色，70% 到 89% 用黄色，90% 起用红色（`\033[31m`），模型名用青色（`\033[36m`），脚本里每个 `echo` 在状态栏里各占一行。10 格宽的进度条，先用 `printf -v` 填一串空格，再用 `${var// /▓}` 和 `${var// /░}` 换成实心和空心，终端得认 ANSI 颜色。文档示例里的 emoji 和 Nerd Font 图标，正在用的字体里有这个字形才会画出来。

可点击的文字是一段 OSC 8，先写 `\e]8;;URL\a`，接着是文字，再写 `\e]8;;\a` 结束，用 `printf '%b'` 打出来，macOS 上按住 `Cmd` 点。iTerm2、Kitty、WezTerm 认这个序列，Terminal.app 不认，点不了就设 `FORCE_HYPERLINK=1`。SSH 和 tmux 可能会把这段序列剥掉，没进全屏时，MCP 报错、自动更新和上下文不足的警告，也可能会把这一行截短。

## 多久跑一次

会话一开始会跑，恢复会话也算，之后这些时候会再跑：

- Claude 有了新回复
- `/compact` 结束
- 权限模式变了
- vim 模式切换了
- `statusLine.command` 变了
- 设过 `refreshInterval`，并且时间到了
- 上一份 JSON 里，某个限流窗口到了 `resets_at`
- 同一份 JSON 里，还热着的 prompt cache 到了 `expires_at`

两次刷新之间会去抖 300ms，只有 `command` 本身改了才不等，新一轮触发时还在跑的脚本会被取消。只改脚本文件要等下一次触发才生效，保存设置则会马上跑一次。这一行要出现，退出码得是 0，stdout 也得有内容，`claude --debug` 会记下每次的 stderr，以及第一次的退出码。主会话闲着时这些事件会停，主会话在等 subagent 干活时也算闲着，这段空档就靠 `refreshInterval` 补上。

## 在 Kaku 里的图标和套餐用量

Kaku 不用装补丁字体也能画出 Nerd Font 图标，它自带 Symbols Nerd Font Mono，并且把它接在你用的字体后面当回退，所以状态栏里打印的分支、文件夹图标，用默认的 JetBrains Mono 能显示，换成你在 `kaku.lua` 里设的字体也能显示。

如果状态栏上只是想看套餐用量，`kaku ai` 已经能看到 Claude Code、Codex、Gemini CLI、Copilot CLI 和 Kimi Code 的用量，只有你在这个面板里改过，Kaku 才会动对应工具的设置，它也不会自己去加状态栏或 hook。

## 常见问题

### 状态栏为什么是空的？

脚本得有执行权限，往 stdout 打出内容，退出码是 0，少了任何一样状态栏就是空的。工作区还没被信任时，`claude --debug` 会记 `Status line command skipped: workspace trust not accepted`，`statusLine` 要跑 shell 命令，跟 [hook](/zh/blog/claude-code-hooks) 用的是同一套信任规则。在托管设置之外把 `disableAllHooks` 设成 `true`，就只剩托管的状态栏，`allowManagedHooksOnly` 会丢掉你自己写的命令。

### 百分比为什么和 `/context` 对不上？

状态栏用的是上一次 API 响应里的数，`/context` 会把那之后新加的消息估算进去，`used_percentage` 不算 `output_tokens`。

### 状态栏花钱吗？

不花，脚本不用 API token，`cost.total_cost_usd` 是按标价估的，`/clear` 会重置成 $0，v2.1.211 之前这个总数会留下来。

### 怎么显示 5 小时和 7 天的限额？

订阅了 claude.ai Pro 或 Max 的人，以及设了消费上限的 Claude apps gateway，第一次 API 响应之后才会有 `rate_limits`。`five_hour.used_percentage` 和 `seven_day.used_percentage` 从 0 到 100，`resets_at` 是 Unix 秒，窗口没有，或者已经过了 `resets_at`，对应字段就不出现，5 小时的百分比用 `jq -r '.rate_limits.five_hour.used_percentage // empty'` 读。

### subagent 在干活时，分支为什么不动？

主会话闲着时这些事件会停，主会话在等 subagent 干活时同样会停，`refreshInterval` 至少设成 `1`，再配上按 `session_id` 做的缓存，git 就不会每次刷新都跑。

# 自建 GitLab 镜像远程（gitlab-mirror）

[文档索引](../README.md) · [文档约定](ref/doc-conventions.md) · [项目状态](../STATUS.md)

本仓库的第三个 git 远程 `gitlab`，指向自建 GitLab（`bsi_humanoid/openneck_dy`），作为 fork `origin`（FAST-CERN/OpenNeck）的镜像 / 备份。自建 GitLab 在内网，经 **cpolar TCP 隧道**以 SSH 访问。建于 2026-08-13。

日常开发只在 `origin` 上进行；`gitlab` 与 `upstream` 都是 fetch-only，push 被 URL 锁挡住以防误推。

## 三个远程的角色

| 远程 | 指向 | 角色 | push |
|---|---|---|---|
| `origin` | `github.com/FAST-CERN/OpenNeck` | 主仓库（fork，RW） | 可推（primary） |
| `upstream` | `github.com/BotRunner64/OpenNeck` | 上游原始仓库（只读同步） | 锁 `no-push-to-upstream` |
| `gitlab` | 自建 GitLab `bsi_humanoid/openneck_dy` | 镜像 / 备份 | 锁 `no-push-to-gitlab` |

`origin` 是唯一的日常 push 目标。`git fetch` 对三者都可用。

## 连接：SSH 经 cpolar 隧道

`gitlab` 经 cpolar TCP 隧道访问。SSH 配置（机器级，不在仓库内）：

- **专用 key**：`~/.ssh/id_ed25519_gitlab`（ed25519）。
- **SSH 别名** `gitlab`（`~/.ssh/config`）：
  ```
  Host gitlab
    HostName 1.tcp.vip.hk.cpolar.io
    Port 10131
    User git
    IdentityFile ~/.ssh/id_ed25519_gitlab
    IdentitiesOnly yes
  ```
- **公钥**加到 GitLab 账号 `@CF_RUI`（User Settings → SSH Keys）。
- **Web 入口**：`http://wggit.vip.cpolar.cn/bsi_humanoid/openneck_dy`。

`IdentitiesOnly yes` 确保只提供该 key，避免 ssh 把本机所有 key 试一遍触发 GitLab 限流。验证连通：

```bash
ssh -T git@gitlab          # 期望: Welcome to GitLab, @CF_RUI!
```

## 一次性设置（在新机器上重建）

```bash
# 1. 生成专用 key（无 passphrase；后续可加，见下）
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_gitlab -N "" -C "OpenNeck GitLab (cpolar self-hosted)"

# 2. 把 ~/.ssh/id_ed25519_gitlab.pub 加到 GitLab 账号 SSH Keys

# 3. 加上面的 SSH config 别名后，验证：
ssh -T git@gitlab

# 4. 加远程、全量推送、锁 push：
git remote add gitlab git@gitlab:bsi_humanoid/openneck_dy.git
git push gitlab --all        # 所有本地分支
git push gitlab --tags       # 所有标签
git remote set-url --push gitlab no-push-to-gitlab   # 锁 push，防误推
```

2026-08-13 首推：`main` + `feat/twist2-dynamixel`。

## 日常使用

**拉取镜像更新**（fetch 不受 push 锁影响）：
```bash
git fetch gitlab
```

**更新镜像**（push 被锁——用直连 URL 一次性绕过，不改配置）：
```bash
git push git@gitlab:bsi_humanoid/openneck_dy.git main
```

**给私钥加 passphrase**（用 `ssh-keygen -p`，不改公钥，GitLab 无需重设）：
```bash
ssh-keygen -p -f ~/.ssh/id_ed25519_gitlab
# Enter old passphrase: 直接回车（初始为空）
# Enter new passphrase: ...
```
加完后用 `ssh -T git@gitlab` 验证（输 passphrase 能连即 OK）。嫌每次输入烦：`ssh-add ~/.ssh/id_ed25519_gitlab`。

## 注意事项

- **代理无关**：`gitlab` 走 SSH（cpolar 隧道），**不受 `http.proxy` 影响**——区别于 `origin` / `upstream` 的 HTTPS（受 `127.0.0.1:7897` 代理开关影响）。
- **cpolar 隧道地址可能变化**：连不上时先到 cpolar 控制台确认隧道公网地址 / 端口，更新 `~/.ssh/config` 的 `HostName` / `Port`。host key 变了用 `ssh-keygen -R "[1.tcp.vip.hk.cpolar.io]:10131"` 清旧条目后重连（或临时 `-o StrictHostKeyChecking=accept-new`）。
- **不是主仓库**：日常 commit / push 走 `origin`。`gitlab` 仅作镜像 / 备份，不日常推。

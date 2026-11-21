# Surge 自定义分流规则

这个仓库维护家中设备共用的分流偏好，例如哪些域名应该拦截、Netflix 使用哪个地区、哪些 AI 服务需要固定出口。规则集保存匹配条件，实际出口由 Surge 主配置中的 `[Rule]` 指定。

## 维护范围

| 由谁维护 | 内容 |
| --- | --- |
| 本仓库 | `Privacy.list`、`Hijacking.list`、`Global.list`、`custom.list`、`gpt.list`、`pikpak.list`，以及本次新增的 `netflix.list` |
| 上游 | Sukka 和 Loyalsoldier 的通用规则集由 Surge 直接订阅 |
| 本机 Surge | 策略组、节点、认证参数、订阅地址和规则顺序 |

## 第一批变更

**安全浏览。** 从 `Privacy.list` 移除 `safebrowsing.urlsec.qq.com` 和 `safebrowsing.googleapis.com`。两条规则此前拦截了安全检查。移除后，由后续规则决定出口。

**Netflix。** `netflix.list` 涵盖 Netflix 主站、静态资源、视频域名和 Fast.com。域名取自现有 `Streaming.list` 中的 Netflix 条目，并加入 `fast.com`。YouTube 继续使用原流媒体规则。测速时也应从最近请求核对实际下载连接的出口。

## 发布和验收

1. 在仓库根目录运行 `python3 -m unittest discover -s tests`。测试检查规则文本的域名匹配范围。
2. 合并到 `main` 后，确认 `netflix.list` 的原始文件可以下载，再把下面这一行加入本机 `[Rule]`。放在 `Privacy.list` 和现有拦截规则之后、`speedtest.conf`、`cdn.conf` 及通用流媒体规则之前。

   ```ini
   RULE-SET,https://raw.githubusercontent.com/koonin/surge/main/netflix.list,🌑Proxy-netflix
   ```

3. 在 Surge 中刷新 `Privacy.list` 并重载配置。用 `match_rule` 检查下表中的域名，并在 Apple TV 播放一次，核对实际 `nflxvideo.net` 连接的策略链。

| 验收域名 | 预期结果 |
| --- | --- |
| `www.netflix.com`、`assets.nflxext.com`、`*.nflxvideo.net` | 最先命中 `netflix.list`，交给 `🌑Proxy-netflix` |
| `fast.com`、`api.fast.com` | 与 Netflix 使用同一策略组 |
| `www.youtube.com` | 继续命中原有流媒体规则 |
| `safebrowsing.urlsec.qq.com`、`safebrowsing.googleapis.com` | 得到可连接的出口。如仍被拒绝，用 `match_rule` 定位下一条拦截规则 |

若 Netflix 分流异常，移除新增的 `RULE-SET` 引用并重载，即可恢复原流媒体路由。规则文件自身的变更通过 Git 回退，随后刷新对应的外部资源。

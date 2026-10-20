# 晟冠社媒自动发布

Codex skill for Shenguan Watch: source one watch from the official catalog, create evidence-backed English copy and a four-panel product image, publish to the designated Facebook and LinkedIn pages, then verify one Google Sheets audit row.

## 固定发布范围

- 产品目录：https://www.shenguanwatch.com/watch/
- Facebook：https://www.facebook.com/shenguanwatch/ （Page ID `61582598850100`）
- LinkedIn：https://www.linkedin.com/company/110553027/admin/dashboard/
- 顺序：Facebook → LinkedIn → Google Sheets。
- 不包含站内文章、网站写入 API 或网站密钥。记录表的站内链接列使用 `不适用（仅社媒）`。

## 安装与使用

将本仓库复制到 `~/.codex/skills/shenguan-social-publisher`，或用 Codex skill installer 从本仓库安装。

需要 Python 3.9+、Pillow、Codex 内置 imagegen、可访问且已登录目标账号的浏览器，以及既有发布记录表的写入权限。

```bash
python3 -m pip install -r requirements.txt
python3 scripts/test_workflow.py
```

在 Codex 中运行：

- `使用 $shenguan-social-publisher 运行一次`
- `使用 $shenguan-social-publisher 对指定产品 URL 运行一次`
- `使用 $shenguan-social-publisher dry-run`

执行 live 发布前会检查两个平台的实时身份和权限。dry-run 只生成本地素材，不发帖、不写在线表格。脚本默认 dry-run；单独运行采集器不会自动发布。图片生成和实际发布由 Codex 的授权工具完成。

## 运行与恢复

每次正常触发创建新的 campaign-runs 运行目录与独立 manifest。随机选品扫描全量分页，最多评估十个候选；指定产品默认不替换。任意提交开始后禁止换品；结果不明先核查已发布列表，禁止猜测重发。仅明确要求恢复时续用原 manifest，跳过已成功的平台。表格失败只补记录，不重发帖子。

产品的机芯、玻璃、表带等可选配置必须保留限定语，不宣传为标配；不推断天然钻石、防水下潜深度、认证或不存在的部件。详见 [内容规范](references/content-spec.md)。

## 文件与验证

- [SKILL.md](SKILL.md)：入口、目标账号和完整流程。
- [发布规范](references/publishing.md)：身份预检、上传、公开链接核验和安全续跑。
- [记录规范](references/reporting.md)：固定五列结构、精确链接去重和回读。
- `scripts/`：采集、图片优化、素材校验、状态更新、完成校验及离线行为测试。

20 项离线测试覆盖目录分页、源事实边界、选项兼容与冲突、身份限制、渠道顺序、永久链接格式、dry-run 限制、候选预算、失败恢复和表格唯一性。离线测试不替代每次执行时的登录、公开帖子和表格核验。

本仓库不包含账号凭据、浏览器状态、运行素材或发布历史。周期调度由 Codex Automations 单独配置，安装技能不会自动创建定时任务。

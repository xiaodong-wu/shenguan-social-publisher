# 发布与核验

## 工具和身份预检

Facebook 和 LinkedIn 的身份核验、上传、预览、提交及公开帖子核验都在已登录的 Chrome 中通过插件完成。

### 发现当前工具

同时检查当前工具的名称与用途说明，寻找 `node_repl`、`cua_repl`、Chrome 或浏览器控制能力。
例如 `mcp__node_repl__js` 的说明包含通过 Chrome 插件控制浏览器，即使工具名没有 Chrome。
优先采用当前 Chrome 插件提供的入口和文档。旧 `cua_repl` 缺失时继续检查新版入口。
只调用当前已暴露的工具，已撤下的工具名称仅作历史记录。

新版入口通过 `node_repl` 导入官方 Chrome 插件的 `scripts/browser-client.mjs`，调用
`setupBrowserRuntime()` 取得 `agent`。客户端的绝对路径从当前启用的插件包确定，版本号随安装变化。
若 Chrome 技能未列出或其 `skills/` 为空，在已安装的官方 Chrome 插件目录中定位客户端和
`docs/api.json`、`docs/bootstrap-troubleshooting.md`、`docs/chrome-troubleshooting.md`。
以包内公开 API 文档和运行时文档为准，保留已有的 `agent` 与 Chrome 句柄供后续调用复用。

### 连接 Chrome 与选择标签页

使用新版入口时按以下步骤处理。

1. 用户提供了插件标签页引用时，按当前插件的标签页认领文档匹配浏览器实例和标签页。
   该引用失效时报告具体标签页状态，等待用户更新引用。
2. 普通 URL 或未指定标签页时，优先复用已有 Chrome 句柄。首次选择时读取
   `await agent.browsers.list()`，再用 `await agent.browsers.get('chrome')` 取得 `chrome` 句柄。
   初始列表为空或仅有 `iab`、`mcpapps` 时也执行这次选择调用，它可以激活尚未列出的 Chrome 连接。
3. 读取 `await chrome.documentation()`，确认选中的是 Chrome 且类型为 `extension`，
   按文档命名本次会话，例如 `await chrome.nameSession('⌚ 晟冠社媒发布')`。
4. `chrome.tabs.list()` 只列出当前会话控制的标签页。已有目标页面时复用该页。
   返回 `[]` 或列表中缺少目标页面时，继续调用 `await chrome.user.openTabs()`，
   按当前返回的 URL 和标题查找目标公司页面。
   使用返回的原始标签页对象调用 `chrome.user.claimTab(tabInfo)`。
5. 普通 URL 没有对应的已打开标签页时，用同一 Chrome 连接的 `chrome.tabs.new()` 创建标签页，
   再 `tab.goto(目标URL)`。先读取当前页面，已有草稿时检查其内容和阶段后继续。
   标签页失效时在同一连接重新获取或打开目标页面，保留浏览器句柄和本地提交状态。

旧版入口仅在当前实际可调用且已有对应文档时使用。按该版本文档初始化 `cua`、读取
`cua.getState()`，必要时用 `cua.createBrowserTab` 指定 `chrome` 打开本次待发布平台的固定页面，
同样以实际返回的 `extension` 类型确认连接。一个运行时已经初始化后，按其排错文档恢复连接。

### 连接失败与续跑

初始化或连接调用失败时，读取当前插件的排错文档，执行其有界重试与只读诊断。
区分当前对话缺少可调用入口、Chrome 扩展通信失败、目标标签页失效和网站登录/权限问题。
只有完成入口发现与适用的连接尝试后才能报告连接阻塞。用户表示其他对话可用时，
重新检查本对话的工具名称和说明，并记录本次实际调用结果。

将检查时间、使用的工具、返回的浏览器类型、失败操作及错误保存到当前批次的证据和恢复历史。
需要用户处理时只说明实际阻塞与对应操作。用户主动停止浏览器控制时，等待其明确恢复。
禁止用独立 CDP/Playwright、社媒 API 或其他浏览器代发。

收到“重试”或“已连接”时读取原 manifest，使用当前工具重新探测。
仅补表时依据已核验的两条永久链接执行记录规范。仅续跑 LinkedIn 时，核验该公司账号并
跳过已发布的 Facebook。已有提交标记时先按下文核查平台结果，再决定能否提交。

### 账号预检

新任务在生成素材前核验两个账号。续跑只核验本次尚需发布的平台，使用以下固定目标。

- Facebook：`https://www.facebook.com/shenguanwatch/`，数字 ID `61582598850100`
- LinkedIn：`https://www.linkedin.com/company/110553027/admin/dashboard/`

核对数字 ID、页面显示的公司名、当前发布身份和创建帖子权限。可见名称允许正常语言
或品牌变体，但账号归属必须明确；保存实际观察，不预先声称已登录。
遇到登录、密码、MFA、CAPTCHA、身份选择器、权限不足或草稿恢复歧义立即停止。

### Facebook 一次两步切换

仅在已登录且目标页面明确提供切换到该同一主页的操作时：

1. 核对当前目标 ID 为 `61582598850100`，点击该页面中的切换动作一次。
2. 若出现确认对话框，仅当它明确显示同一目标主页时点击确认一次。
3. 导航完成后重开固定目标 URL，检查目标 ID、可见公司名、实际发布身份和创建按钮。

两步合计一次序列。若仍要求切换、出现其他账号列表或验证，则停止。不重复切换，
不改用个人账号或其他管理主页。

## 最终发布前

新任务先确认两个平台具备权限，续跑先确认待发布平台具备权限。
全部素材通过 `validate_campaign.py` 后才开始本次提交。
各平台提交前再次确认身份，粘贴完整对应文案，上传 `social-upload.jpg`，检查预览。
如果当前模板或上传工具不能接受本地图片，记录阻塞，不擅自发布无图帖子。

### AI 信息与可选设置

本技能发布普通商品静态图文，不把“使用过 AI”自动等同于必须手动打开每一个可选
AI 标签开关。对可选的静态图片披露保持未主动开启；若页面明确要求披露，或当前规则
要求该内容披露，则如实填写，不虚假声明“未使用 AI”或“真实拍摄”。
Meta 的规则会变化；不确定时查当前官方说明及当前发布界面。
2026-10-28 核查的 [Meta 官方说明](https://about.fb.com/news/2026/02/meta-prepares-for-2026-us-midterms/)
区分平台检测和发布者自行披露，并明确要求对逼真合成视频或音频使用披露工具。
不要把这一范围推断为所有普通商品静态图均必须手动加标，也不要据此保证静态图不会自动加标。

提交前记录 AI 选项是否出现、是否为必填、实际选择及依据；核验时若出现“AI 内容”，
打开标签说明区分“发布者添加”与平台检测。图片文件无元数据不证明不会出现平台标签。
已有帖子仅在用户要求修改且界面允许时编辑可选设置；平台强制或自动标签不能按可选开关处理。
不删除、重发或反复重编码试探识别结果。

## Facebook → LinkedIn

每个平台使用以下顺序，Facebook 先执行：

1. 打开固定目标页面的创建帖子操作；不从通用首页发帖。
2. 使用 `facebook.txt` 或 `linkedin.txt`，上传同一临时 JPEG。
3. 确认全部文本不含网站链接，核对图片和作者身份，处理正常的预览步骤。
4. 紧邻最终提交前运行 `update_manifest.py --status pending --submission-started`。
5. 点击最终发布按钮一次。
6. 在目标页面时间线或已发布列表找到该条帖子，打开实际帖子链接核对文本、图片和作者。
7. 保存 `evidence/facebook-public.md` 或 `evidence/linkedin-public.md`，包含核验时间、
   数字身份、观察到的作者、公开 permalink、文案/图片一致性和浏览器截图路径（可用时）。
   私有后台 URL、首页、主页 URL 和仅有“已提交”提示不算公开发布证据。
8. 记录 `published`，例如：

```bash
python3 scripts/update_manifest.py MANIFEST --channel facebook --status published \
  --url FACEBOOK_POST_URL --identity-id 61582598850100 --evidence FACEBOOK_EVIDENCE
python3 scripts/update_manifest.py MANIFEST --channel linkedin --status published \
  --url LINKEDIN_POST_URL --identity-id 110553027 --evidence LINKEDIN_EVIDENCE
```

只有点击并查看实际记录后才写核验文件；状态脚本验证路径和身份字段，不能替代观察。
平台如提供不同但真实的永久链接结构，先核实其来源，再调整本技能 URL 校验器；
不得编造一个符合正则的 URL。短链接应打开后记录真实平台永久链接。

## 结果不明与续跑

若提交后超时或浏览器断开，保留永久提交标记，记录 `blocked` 及原因。
先查看该账号的已发布内容、时间、图片和完整文案进行核对。找到则记成功；只有取得
该条未发布的明确证据后才允许一次有记录的重试。仍不明确则停止，禁止试探性再点发布。
已发布渠道不可自动删除、回滚、重发，也不能重置为 pending。

一个渠道失败或阻塞时，停止后续提交并报告当前状态。用户明确要求恢复时再重新预检；
跳过 `published` 渠道，恢复同一产品与素材。两个社媒成功但表格失败时，仅修复表格记录。
若原批次停在选品前，双平台预检通过后检查原目录。仅在还没有选品尝试、产品 manifest 或提交记录时，
以原批次目录作为抓取器的 `--output-root` 进行首次选品。将返回的 `selection_log` 与产品
manifest 路径记入原预检 manifest 的恢复历史，随后用产品 manifest 运行校验和发布脚本。
若目录已有选品痕迹，先从现有台账定位进度，避免因中途退出而再次抽品。
双平台均成功后可以删除上传 JPEG，原有文件哈希和审核证据保留，完成检查不再要求 JPEG。

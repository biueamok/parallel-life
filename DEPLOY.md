# 🚀 部署到 Streamlit Community Cloud 指南

本文档手把手带你把「平行人生」Demo 部署到公网，拿到永久 https 链接，10 分钟搞定。

---

## 📋 前置条件

- [x] GitHub 账号（免费版即可）
- [x] 浏览器（任意）

> 全程 **免费**，Streamlit Community Cloud 对公开仓库永久免费。

---

## 🪜 第一步：推送代码到 GitHub

### 方案 A · 在 AnyDev 命令行里推（推荐，最快）

```bash
# 1. 进入项目目录
cd /data/workspace/parallel_life

# 2. 初始化 git 仓库
git init
git add .
git commit -m "feat: 平行人生 Life Decision OS MVP"

# 3. 在 GitHub 上创建一个新仓库（浏览器打开）
#    https://github.com/new
#    - 仓库名：parallel-life （或你喜欢的名字）
#    - 可见性：Public（Streamlit Cloud 免费版要求公开）
#    - ⚠️ 不要勾选 "Initialize with README"

# 4. 关联远程仓库并推送（替换成你自己的 GitHub 用户名）
git remote add origin https://github.com/<你的GitHub用户名>/parallel-life.git
git branch -M main
git push -u origin main
```

> 推送时会要求输入 GitHub 用户名和 **Personal Access Token**（不是登录密码）。
> 如果没有 token，去 https://github.com/settings/tokens/new 生成一个，勾 `repo` 权限即可。

### 方案 B · 用 GitHub 网页上传（最简单，不用命令行）

1. 在 https://github.com/new 创建 Public 仓库 `parallel-life`
2. 点击仓库页面的 **"uploading an existing file"** 链接
3. 把下面这些文件拖进去：
   ```
   app.py
   core.py
   narratives.py
   mock_data.py
   styles.py
   requirements.txt
   README.md
   .gitignore
   .streamlit/config.toml
   ```
4. 点 **Commit changes** 完成上传

> 注意：`.streamlit/` 是隐藏目录，网页上传需要先建目录再传 `config.toml`。

---

## 🎯 第二步：在 Streamlit Cloud 部署

1. 打开 **https://share.streamlit.io**
2. 点 **Sign in with GitHub**（用你的 GitHub 账号登录）
3. 首次登录会授权 Streamlit 读取你的仓库，点同意
4. 点击右上角 **New app** 按钮
5. 按下图填写：

   | 字段 | 填入 |
   |---|---|
   | Repository | `<你的GitHub用户名>/parallel-life` |
   | Branch | `main` |
   | Main file path | `app.py` |
   | App URL（可选）| 起一个你喜欢的子域名，如 `parallel-life` → `parallel-life.streamlit.app` |

6. 点 **Deploy!** 按钮

⏳ Streamlit Cloud 会自动：
- 拉取你的仓库
- 读取 `requirements.txt` 装依赖（约 2-3 分钟）
- 启动 `app.py`

完成后，你会得到一个 https 公网链接，例如：
```
https://parallel-life.streamlit.app
```

**这个链接任何人都能访问，直接发给朋友就行。** 🎉

---

## 🔄 第三步：后续迭代（代码更新）

每次你修改代码后：

```bash
cd /data/workspace/parallel_life
git add .
git commit -m "更新：xxxx"
git push
```

Streamlit Cloud 会 **自动检测到 push，自动重新部署**，大约 30 秒生效，无需任何手动操作。

---

## ⚠️ 常见问题

### Q1：部署后页面显示 "ModuleNotFoundError"
- 原因：某个 Python 包没列在 `requirements.txt`
- 解决：把缺失的包加到 `requirements.txt`，push 即可自动重装

### Q2：App 进入睡眠 / 打开时显示 "Yes, get this app back up!"
- 原因：Streamlit Cloud 免费版 **7 天无人访问会休眠**
- 解决：点一下 "wake up" 按钮即可，30 秒内恢复，数据不会丢

### Q3：要不要接 OpenAI Key？
- 当前 Demo **不需要**任何 Key，用的是本地模板叙事
- 如果后续想接 GPT-4：在 Streamlit Cloud app 的 **Settings → Secrets** 里填
  ```toml
  OPENAI_API_KEY = "sk-xxxxx"
  ```
  然后代码里 `st.secrets["OPENAI_API_KEY"]` 即可读取，**不会泄露到 GitHub**

### Q4：想要私有仓库部署？
- Streamlit Cloud 免费版只支持 **Public 仓库 + 最多 1 个私有 app**
- 如果你的创业想保密，建议：
  - 方案 1：先用 Public 跑 Demo 验证，正式商业化后迁移到 Vercel / Railway / 腾讯云 CVM
  - 方案 2：升级 Streamlit 付费版（$250/月 起，不推荐早期用）

### Q5：国内访问速度慢
- Streamlit Cloud 服务器在美国，国内访问约 1-3 秒首屏
- 给国内朋友用建议部署到 **腾讯云 Serverless** 或 **Vercel**（我可以后续帮你做）

---

## 🎁 部署完成后给你的清单

- [ ] 得到公网 https 链接一份
- [ ] 链接可以直接分享给朋友，无需登录
- [ ] 代码自动同步，改完 push 就上线
- [ ] 免费、永久（只要仓库不删、不长期无访问）

---

## 📞 需要我帮忙？

推送代码 / 部署时遇到任何报错，把报错信息发给我，我立刻帮你定位解决。

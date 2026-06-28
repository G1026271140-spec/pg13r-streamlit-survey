# PG-13-R Streamlit 在线问卷

这是一个根据图片中的「延长哀伤-13-修改版（PG-13-R）」量表制作的 Streamlit 在线问卷原型。

## 功能

- Q1、Q2、Q3-Q12、Q13 全题填写
- Q3-Q12 按 1-5 分计分，总分范围 10-50
- 按图片规则给出筛查提示：
  - Q3-Q12 总分 >= 30
  - Q1 选择「是」
  - Q2 至少 6 个月
  - Q13 选择「是」
- 提交结果本地保存为 CSV
- 管理员口令查看和下载提交记录
- 页面内保留量表说明、来源与非诊断提示

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

如需启用结果管理页，请设置环境变量：

```bash
set ADMIN_PASSWORD=your-admin-password
streamlit run app.py
```

PowerShell:

```powershell
$env:ADMIN_PASSWORD="your-admin-password"
streamlit run app.py
```

## 部署到 Streamlit Community Cloud

如果从当前仓库部署，入口文件选择：

```text
projects/pg13r-streamlit-survey/app.py
```

在 Streamlit Cloud 的 App secrets 中配置管理员口令：

```toml
ADMIN_PASSWORD = "请替换为足够复杂的管理口令"
```

## 数据保存说明

当前版本把提交数据保存到应用目录下的 `data/pg13r_responses.csv`，适合原型、小范围测试和课堂演示。

Streamlit Community Cloud 的本地文件不适合作为长期稳定数据库。正式公开收集问卷时，建议改接 Google Sheets、Supabase、PostgreSQL 或其他数据库。

## 注意

本问卷仅用于延长哀伤相关症状的自评与筛查参考，不作为正式诊断。若受访者正在经历强烈痛苦，或出现伤害自己/他人的想法，应及时联系当地急救服务、危机干预热线或专业心理健康服务。

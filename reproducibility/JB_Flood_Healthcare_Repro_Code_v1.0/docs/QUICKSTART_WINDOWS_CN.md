# Windows 使用说明（先保存，后上传 GitHub）

## 这是什么

这是一套 **2026 年 10 月依据论文方法重新编写的独立参考计算程序**，不是此前计算的原始脚本。可以测试、运行、审计，但没有在你的 75,149 个真实 WorldPop 起点和完整 D06R/D08/D10 图上运行并对齐，因此现在**不能把它描述为已验证的完整复现代码**。

## 第一步：放置代码

解压 ZIP，将整个 `JB_Flood_Healthcare_Repro_Code_v1.0` 文件夹复制到研究数据 GitHub 仓库目录下的 `reproducibility/` 文件夹里。不要覆盖现有归档数据，也不要直接删除以前任何分析文件。

## 第二步：安装依赖

在解压文件夹打开 PowerShell：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python -m pytest -q
```

若 PowerShell 禁止激活虚拟环境，可直接：

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest -q
```

## 第三步：恢复真实大数据

在整个研究数据仓库根目录运行：

```powershell
python tools/restore_large_files.py
```

这一脚本来自你**现有仓库**，用于还原之前拆成 `part001`、`part002` 等的 CSV/GeoPackage。不要重新压缩成误认为原始输入的文件。

## 第四步：检查、尝试自动整理四份核心输入

回到新代码文件夹：

```powershell
jb-repro inspect --repo-root "D:\你的路径\JB-Flood-Road-Network-Healthcare-Accessibility"
jb-repro prepare --repo-root "D:\你的路径\JB-Flood-Road-Network-Healthcare-Accessibility" --outdir local_inputs
```

`prepare` 会尝试将原有有向边、人口起点、医院、关闭路段整理成统一四份 CSV。若发现原始 CSV 缺列、关联键无法验证、子边索引不一致，会主动终止，而不会伪造数据。

## 第五步：本地实验复算

只有第四步成功且手工复核了字段语义后，才继续：

```powershell
jb-repro run --edges local_inputs/edges.csv --origins local_inputs/origins.csv --hospitals local_inputs/hospitals.csv --closures local_inputs/closures.csv --outdir run_outputs --require-match
```

检查 `run_outputs/frozen_reference_comparison.json`。如果出现 `FAIL`，要研究原始子边 ID、部分关闭边界、单行道映射和医院接入方向是否一致；不能直接修改程序输出数字来获得 PASS。

## 第六步：推送 GitHub

只上传源代码及说明、合成测试数据；不要上传本地产生的大型中间数据或 `.venv` 文件夹。`run_outputs` 和 `local_inputs` 已加入 `.gitignore`。

```powershell
git add reproducibility/JB_Flood_Healthcare_Repro_Code_v1.0
git commit -m "Add independent reference code for healthcare accessibility and restoration"
git push origin main
```

建议先使用 GitHub 分支 + Pull Request 审核。

## 对投稿最重要的一句话

当前只能说“独立参考代码已公开、可供验证”，不能说“当初实验原始代码完整公开”或“已100%重现论文全部结果”。通过真实数据逐项复核后，才可以更新论文 Code availability 声明。

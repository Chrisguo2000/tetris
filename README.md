# GitHub Actions 定时运行测试项目

这个项目用于验证 GitHub Actions 是否可以按照计划自动运行，也可以手动触发运行。

## 功能说明

- 执行 `test.py`。
- 在 workflow 日志中输出当前时间。
- 将当前时间写入 `logs/run_log.txt`。
- 将 `logs/run_log.txt` 上传为 GitHub Actions Artifact。

## 定时规则

Workflow 文件路径：

```text
.github/workflows/test_schedule.yml
```

自动运行时间为每周一 `UTC 01:00`：

```cron
0 1 * * 1
```

## 如何手动运行

1. 打开 GitHub 仓库页面。
2. 进入 `Actions` 页面。
3. 选择 `Test Scheduled Python Run` workflow。
4. 点击 `Run workflow`。
5. 选择要运行的分支，然后确认运行。

## 如何查看运行日志

1. 打开 GitHub 仓库页面。
2. 进入 `Actions` 页面。
3. 选择 `Test Scheduled Python Run` workflow。
4. 点击某一次 workflow run。
5. 打开 `Run test.py` job。
6. 查看 `Execute test.py` step，其中会输出当前运行时间。

## 如何下载 Artifact

1. 打开 GitHub 仓库页面。
2. 进入 `Actions` 页面。
3. 选择 `Test Scheduled Python Run` workflow。
4. 点击一次已经完成的 workflow run。
5. 在页面底部找到 `Artifacts` 区域。
6. 下载名为 `run-log` 的 Artifact。
7. 解压后打开 `run_log.txt`，即可查看本次运行写入的时间记录。

## 本地运行

```bash
python test.py
```

本地运行后，会自动创建或更新：

```text
logs/run_log.txt
```

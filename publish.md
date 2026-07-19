# 自行推送

仓库远程设置为：

```text
git@github.com:EvilIrving/learns.git
```

解压后进入目录并检查：

```bash
cd learns
git status
git remote -v
git log --oneline -5
```

使用 SSH 推送：

```bash
git push -u origin main
```

若本机尚未配置 GitHub SSH 密钥，可改用 HTTPS：

```bash
git remote set-url origin https://github.com/EvilIrving/learns.git
git push -u origin main
```

推送前建议运行：

```bash
python3 -m unittest -v
python3 learning_tracker.py init
python3 learning_tracker.py summary --days 30
```

`learns.db`、导出的学习记录和本地环境文件默认不会提交。

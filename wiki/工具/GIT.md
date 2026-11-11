# GIT

## 基础

Git 是分布式版本控制系统，用于跟踪文件变化、协作开发。

## 核心

### 基础命令

- `git status`：检测当前文件状态
- `git add filename`：提出更改添加到暂存区
- `git commit -m "message"`：提交更新
- `git commit -a -m "message"`：跳过暂存区域直接提交
- `git rm filename`：移除文件
- `git mv README.md README`：重命名文件

### 分支操作

- `git branch name`：创建分支
- `git checkout branch`：切换分支
- `git merge branch`：合并分支
- `git branch -d name`：删除分支
- `git push origin`：推送分支到远端

### 撤销操作

- `git reset filename`：取消暂存文件
- `git checkout -- filename`：撤消对文件的修改
- `git commit --amend`：修改最后一次提交
- `git fetch origin && git reset --hard origin/master`：丢弃本地所有改动

### .gitignore

忽略不需要版本控制的文件。

## 标签

#Git #版本控制 #分支管理

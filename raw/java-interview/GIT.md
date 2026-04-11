# GIT

* **检测当前文件状态** : `git status`
* **提出更改（把它们添加到暂存区**）：`git add filename` (针对特定文件)、`git add *`(所有文件)、`git add *.txt`（支持通配符，所有 .txt 文件）
* **忽略文件**：`.gitignore` 文件
* **提交更新:**`git commit -m "代码提交信息"` （每次准备提交前，先用 `git status` 看下，是不是都已暂存起来了， 然后再运行提交命令 `git commit`）
* **跳过使用暂存区域更新的方式** : `git commit -a -m "代码提交信息"`。 `git commit` 加上 `-a` 选项，Git 就会自动把所有已经跟踪过的文件暂存起来一并提交，从而跳过 `git add` 步骤。
* **移除文件**：`git rm filename` （从暂存区域移除，然后提交。）
* **对文件重命名**：`git mv README.md README`(这个命令相当于`mv README.md README`、`git rm README.md`、`git add README` 这三条命令的集合)
* **git branch Name**
* **git checkout branch**

***

有时候我们提交完了才发现漏掉了几个文件没有添加，或者提交信息写错了。 此时，可以运行带有 `--amend` 选项的提交命令尝试重新提交：

```plain
git commit --amend
```

**取消暂存的文件**

```plain
git reset filename
```

**撤消对文件的修改:**

```plain
git checkout -- filename
```

**假如你想丢弃你在本地的所有改动与提交，可以到服务器上获取最新的版本历史，并将你本地主分支指向它：**

```plain
git fetch origin
git reset --hard origin/master
```

***

切换到主分支

```plain
git checkout master
```

合并分支(可能会有冲突)

```plain
git merge test
```

把新建的分支删掉

```plain
git branch -d feature_x
```

将分支推送到远端仓库（推送成功后其他人可见）：

```plain
git push origin
```


> 更新: 2025-06-23 11:08:29  
> 原文: <https://www.yuque.com/nibiwanxiamei/yrd6t1/wiw46wmom94o1sf6>
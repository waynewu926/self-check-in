from django.db import models

# 由于用户需求非常简单，故直接使用 Django 自带的 User 模型

# 最开始尝试过使用 AbstractUser 模型，但当时一窍不通，搞不好，遂放弃；
# 后面尝试直接自定义一个 Customer 模型，但这样操作在“用户认证”这一点比较困难，遂放弃；
# 后面又尝试使用内部的 User 模型去扩展 Customer 模型，虽然这种方式也是比较常见且推荐的，但意识到我的需求实在太简单了，所以干脆直接使用自带的 User 模型
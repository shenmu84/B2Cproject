# 美多商城项目

## 项目介绍
美多商城是一个基于Django开发的B2C电商平台，提供商品浏览、购物车、订单管理、支付等功能。

## 技术栈
- Python 3.8+
- Django 2.2.5
- MySQL 5.7+
- Redis 6.0+
- Celery 5.1.2

## 项目结构
```
meiduo_mall/
├── apps/                    # 应用目录
│   ├── mall/               # 商城相关应用
│   └── Management/         # 后台管理应用
├── celery_tasks/           # Celery异步任务
├── libs/                   # 第三方库
├── static/                # 静态文件
├── templates/             # 模板文件
├── utils/                 # 工具类
└── meiduo_mall/          # 项目配置
```

## 环境要求
- Python 3.8+
- MySQL 5.7+
- Redis 6.0+
- 虚拟环境（推荐使用venv或conda）

## 安装步骤

1. 克隆项目
```bash
git clone <repository_url>
cd meiduo_mall
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入相应的配置信息
```

5. 初始化数据库
```bash
python manage.py migrate
```

6. 创建超级用户
```bash
python manage.py createsuperuser
```

7. 启动开发服务器
```bash
python manage.py runserver
```

## 开发环境配置

1. 安装开发工具
```bash
pip install -r requirements-dev.txt
```

2. 配置IDE
- 推荐使用PyCharm或VS Code
- 配置Python解释器为虚拟环境
- 安装推荐的插件（Python, Django等）

## 部署说明

1. 生产环境配置
```bash
# 修改.env文件中的DJANGO_SETTINGS_MODULE
DJANGO_SETTINGS_MODULE=meiduo_mall.settings.prod
```

2. 收集静态文件
```bash
python manage.py collectstatic
```

3. 使用uWSGI部署
```bash
uwsgi --ini uwsgi.ini
```

## 项目功能

### 用户模块
- 用户注册
- 用户登录
- 手机验证码登录
- 第三方登录（QQ、微信）

### 商品模块
- 商品分类
- 商品列表
- 商品详情
- 商品搜索

### 购物车模块
- 添加商品
- 修改数量
- 删除商品
- 全选/取消全选

### 订单模块
- 提交订单
- 订单支付
- 订单列表
- 订单详情

### 支付模块
- 支付宝支付
- 微信支付

## 开发规范

1. 代码风格
- 遵循PEP 8规范
- 使用black进行代码格式化
- 使用flake8进行代码检查

2. 提交规范
- 使用语义化提交信息
- 每个功能创建独立分支
- 提交前进行代码审查

3. 文档规范
- 及时更新文档
- 添加必要的注释
- 编写单元测试

## 常见问题

1. 数据库连接问题
- 检查数据库配置
- 确保数据库服务运行
- 验证用户权限

2. Redis连接问题
- 检查Redis服务状态
- 验证连接配置
- 检查防火墙设置

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 许可证
MIT License 
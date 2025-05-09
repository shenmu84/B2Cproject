# 美多商城前端文件结构说明文档

## 1. 目录结构

```
front_end_pc/
├── css/                    # 样式文件目录
│   ├── reset.css          # 重置样式
│   ├── common.css         # 公共样式
│   └── main.css           # 主要样式
│
├── js/                     # JavaScript文件目录
│   ├── host.js            # 主机配置
│   ├── login.js           # 登录相关
│   ├── register.js        # 注册相关
│   ├── cart.js            # 购物车相关
│   ├── detail.js          # 商品详情相关
│   ├── list.js            # 商品列表相关
│   ├── search.js          # 搜索相关
│   ├── user_center_info.js    # 用户中心信息
│   ├── user_center_site.js    # 用户中心地址
│   ├── user_center_pass.js    # 用户中心密码
│   ├── user_center_order.js   # 用户中心订单
│   ├── place_order.js     # 订单结算
│   └── oauth_callback.js  # 第三方登录回调
│
├── images/                 # 图片资源目录
│   ├── logo.png           # 网站logo
│   ├── banner/            # 轮播图
│   └── goods/             # 商品图片
│
├── goods/                  # 商品相关资源
│   └── images/            # 商品图片
│
├── .idea/                  # IDE配置目录
│
├── index.html             # 首页
├── login.html             # 登录页
├── register.html          # 注册页
├── cart.html              # 购物车页
├── detail.html            # 商品详情页
├── list.html              # 商品列表页
├── search.html            # 搜索页
├── user_center_info.html  # 用户中心信息页
├── user_center_site.html  # 用户中心地址页
├── user_center_pass.html  # 用户中心密码页
├── user_center_order.html # 用户中心订单页
├── place_order.html       # 订单结算页
├── pay_success.html       # 支付成功页
├── order_success.html     # 订单成功页
├── oauth_callback.html    # 第三方登录回调页
└── success_verify_email.html  # 邮箱验证成功页
```

## 2. 文件说明

### 2.1 HTML文件

#### 2.1.1 公共页面
- `index.html`: 网站首页
- `login.html`: 用户登录页面
- `register.html`: 用户注册页面
- `search.html`: 商品搜索页面

#### 2.1.2 商品相关
- `list.html`: 商品列表页面
- `detail.html`: 商品详情页面
- `cart.html`: 购物车页面

#### 2.1.3 用户中心
- `user_center_info.html`: 用户信息页面
- `user_center_site.html`: 收货地址页面
- `user_center_pass.html`: 修改密码页面
- `user_center_order.html`: 订单管理页面

#### 2.1.4 订单相关
- `place_order.html`: 订单结算页面
- `pay_success.html`: 支付成功页面
- `order_success.html`: 订单成功页面

#### 2.1.5 其他功能
- `oauth_callback.html`: 第三方登录回调页面
- `success_verify_email.html`: 邮箱验证成功页面

### 2.2 JavaScript文件

#### 2.2.1 配置文件
- `host.js`: 主机配置，包含API地址等配置信息

#### 2.2.2 用户认证
- `login.js`: 处理用户登录逻辑
- `register.js`: 处理用户注册逻辑
- `oauth_callback.js`: 处理第三方登录回调

#### 2.2.3 商品相关
- `list.js`: 处理商品列表展示
- `detail.js`: 处理商品详情展示
- `search.js`: 处理商品搜索功能

#### 2.2.4 购物车
- `cart.js`: 处理购物车相关操作

#### 2.2.5 用户中心
- `user_center_info.js`: 处理用户信息管理
- `user_center_site.js`: 处理收货地址管理
- `user_center_pass.js`: 处理密码修改
- `user_center_order.js`: 处理订单管理

#### 2.2.6 订单相关
- `place_order.js`: 处理订单结算

### 2.3 CSS文件

#### 2.3.1 基础样式
- `reset.css`: 重置浏览器默认样式
- `common.css`: 公共样式定义

#### 2.3.2 主要样式
- `main.css`: 网站主要样式定义

### 2.4 资源文件

#### 2.4.1 图片资源
- `images/`: 存放网站通用图片资源
  - `logo.png`: 网站logo
  - `banner/`: 轮播图图片
  - `goods/`: 商品相关图片

#### 2.4.2 商品图片
- `goods/images/`: 存放商品图片资源

## 3. 文件依赖关系

### 3.1 HTML文件依赖
- 所有HTML文件都依赖：
  - `css/reset.css`
  - `css/common.css`
  - `css/main.css`
  - `js/host.js`

### 3.2 JavaScript文件依赖
- 所有JS文件都依赖：
  - `host.js`（用于获取API地址）

### 3.3 页面特定依赖
- 登录相关：`login.html` + `login.js`
- 注册相关：`register.html` + `register.js`
- 购物车相关：`cart.html` + `cart.js`
- 商品详情相关：`detail.html` + `detail.js`
- 用户中心相关：`user_center_*.html` + `user_center_*.js`
- 订单相关：`place_order.html` + `place_order.js`

## 4. 开发规范

### 4.1 文件命名规范
- HTML文件：小写字母，下划线分隔
- JavaScript文件：小写字母，下划线分隔
- CSS文件：小写字母，下划线分隔
- 图片文件：小写字母，下划线分隔

### 4.2 目录结构规范
- 按功能模块分类
- 资源文件集中管理
- 公共组件独立存放

### 4.3 代码规范
- HTML：语义化标签，适当的注释
- JavaScript：模块化开发，统一的编码风格
- CSS：BEM命名规范，模块化样式 
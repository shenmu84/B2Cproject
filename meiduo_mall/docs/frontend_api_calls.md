# 美多商城前端API调用文档

## 1. 用户认证模块

### 1.1 登录功能
- **文件**: `front_end_pc/login.html` + `front_end_pc/js/login.js`
- **主要函数**: 
  - `on_submit()`: 处理登录表单提交
  - `gitee_login()`: 处理Gitee第三方登录
- **API调用**:
  ```javascript
  // 用户登录
  axios.post(this.host + '/users/login/', {
    username: this.username,
    password: this.password
  })
  ```

### 1.2 注册功能
- **文件**: `front_end_pc/register.html` + `front_end_pc/js/register.js`
- **主要函数**:
  - `on_submit()`: 处理注册表单提交
  - `check_username()`: 检查用户名
  - `check_phone()`: 检查手机号
  - `send_sms_code()`: 发送短信验证码
- **API调用**:
  ```javascript
  // 用户注册
  axios.post(this.host + '/users/register/', {
    username: this.username,
    password: this.password,
    password2: this.password2,
    email: this.email,
    mobile: this.mobile
  })
  ```

### 1.3 邮箱验证
- **文件**: `front_end_pc/success_verify_email.html`
- **主要函数**:
  - `created()`: 发送邮箱验证请求
- **API调用**:
  ```javascript
  // 邮箱验证
  axios.put(this.host + '/users/email/verification/' + window.location.search)
  ```

## 2. 用户中心模块

### 2.1 个人信息
- **文件**: `front_end_pc/user_center_info.html` + `front_end_pc/js/user_center_info.js`
- **主要函数**:
  - `get_person_info()`: 获取用户信息
  - `save_email()`: 保存邮箱
  - `get_history()`: 获取浏览历史
- **API调用**:
  ```javascript
  // 获取用户信息
  axios.get(this.host + '/users/profile/')
  // 更新用户信息
  axios.put(this.host + '/users/profile/', {
    email: this.email,
    mobile: this.mobile
  })
  ```

### 2.2 地址管理
- **文件**: `front_end_pc/user_center_site.html` + `front_end_pc/js/user_center_site.js`
- **主要函数**:
  - `get_address()`: 获取地址列表
  - `save_address()`: 保存地址
  - `del_address()`: 删除地址
  - `set_default()`: 设置默认地址
- **API调用**:
  ```javascript
  // 获取地址列表
  axios.get(this.host + '/addresses/')
  // 新增地址
  axios.post(this.host + '/addresses/create/', this.form_address)
  // 修改地址
  axios.put(this.host + '/addresses/' + address_id + '/', this.form_address)
  // 删除地址
  axios.delete(this.host + '/addresses/' + address_id + '/')
  // 设置默认地址
  axios.put(this.host + '/addresses/' + address_id + '/default/')
  ```

### 2.3 修改密码
- **文件**: `front_end_pc/user_center_pass.html` + `front_end_pc/js/user_center_pass.js`
- **主要函数**:
  - `change_password()`: 修改密码
- **API调用**:
  ```javascript
  // 修改密码
  axios.put(this.host + '/password/', {
    old_password: this.old_pwd,
    new_password: this.new_pwd,
    new_password2: this.new_cpwd
  })
  ```

### 2.4 订单管理
- **文件**: `front_end_pc/user_center_order.html` + `front_end_pc/js/user_center_order.js`
- **主要函数**:
  - `get_orders()`: 获取订单列表
  - `get_order_detail()`: 获取订单详情
- **API调用**:
  ```javascript
  // 获取订单列表
  axios.get(this.host + '/orders/')
  // 获取订单详情
  axios.get(this.host + '/orders/' + order_id + '/')
  ```

## 3. 商品模块

### 3.1 商品列表
- **文件**: `front_end_pc/list.html` + `front_end_pc/js/list.js`
- **主要函数**:
  - `get_skus()`: 获取商品列表
  - `get_hot_goods()`: 获取热销商品
  - `get_category()`: 获取商品分类
- **API调用**:
  ```javascript
  // 获取商品列表
  axios.get(this.host + '/list/' + this.cat + '/skus/')
  // 获取热销商品
  axios.get(this.host + '/hot/' + this.cat + '/')
  // 获取商品分类
  axios.get(this.host + '/categories/')
  ```

### 3.2 商品详情
- **文件**: `front_end_pc/detail.html` + `front_end_pc/js/detail.js`
- **主要函数**:
  - `get_sku_id()`: 获取商品ID
  - `add_cart()`: 添加购物车
  - `get_cart()`: 获取购物车
  - `detail_visit()`: 记录访问量
- **API调用**:
  ```javascript
  // 添加浏览历史
  axios.post(this.host + '/browse_histories/', {
    sku_id: this.sku_id
  })
  // 添加购物车
  axios.post(this.host + '/carts/', {
    sku_id: this.sku_id,
    count: this.sku_count,
    selected: true
  })
  ```

### 3.3 商品搜索
- **文件**: `front_end_pc/search.html` + `front_end_pc/js/search.js`
- **主要函数**:
  - `get_search_result()`: 获取搜索结果
  - `get_cart()`: 获取购物车
- **API调用**:
  ```javascript
  // 获取搜索结果
  axios.get(this.host + '/search/', {
    params: {
      q: this.query,
      page: this.page,
      page_size: this.page_size
    }
  })
  ```

## 4. 购物车模块

- **文件**: `front_end_pc/cart.html` + `front_end_pc/js/cart.js`
- **主要函数**:
  - `get_cart()`: 获取购物车
  - `update_count()`: 更新数量
  - `update_selected()`: 更新选中状态
  - `on_selected_all()`: 全选/取消全选
- **API调用**:
  ```javascript
  // 获取购物车
  axios.get(this.host + '/carts/')
  // 更新购物车
  axios.put(this.host + '/carts/', {
    sku_id: this.cart[index].id,
    count: count,
    selected: this.cart[index].selected
  })
  // 删除购物车商品
  axios.delete(this.host + '/carts/', {
    data: {
      sku_id: this.cart[index].id
    }
  })
  // 全选/取消全选
  axios.put(this.host + '/carts/selection/', {
    selected: selected
  })
  ```

## 5. 订单模块

### 5.1 订单结算
- **文件**: `front_end_pc/place_order.html` + `front_end_pc/js/place_order.js`
- **主要函数**:
  - `on_order_submit()`: 提交订单
- **API调用**:
  ```javascript
  // 获取结算信息
  axios.get(this.host + '/orders/settlement/')
  // 提交订单
  axios.post(this.host + '/orders/commit/', {
    address_id: this.address_id,
    pay_method: this.pay_method,
    order_id: this.order_id
  })
  ```

### 5.2 支付成功
- **文件**: `front_end_pc/pay_success.html`
- **主要函数**:
  - `created()`: 查询支付状态
- **API调用**:
  ```javascript
  // 查询支付状态
  axios.put(this.host + '/payment/status/' + document.location.search)
  ```

### 5.3 订单成功
- **文件**: `front_end_pc/order_success.html` + `front_end_pc/js/order_success.js`
- **主要函数**:
  - `get_order_info()`: 获取订单信息
- **API调用**:
  ```javascript
  // 获取订单信息
  axios.get(this.host + '/orders/' + order_id + '/')
  ```

## 6. 第三方登录

- **文件**: `front_end_pc/oauth_callback.html` + `front_end_pc/js/oauth_callback.js`
- **主要函数**:
  - `on_submit()`: 绑定账号
  - `send_sms_code()`: 发送短信验证码
- **API调用**:
  ```javascript
  // 获取第三方登录回调
  axios.get(this.host + '/oauth/callback/?code=' + code)
  // 绑定第三方账号
  axios.post(this.host + '/oauth/callback/', {
    username: this.username,
    password: this.password,
    mobile: this.mobile,
    sms_code: this.sms_code,
    access_token: this.access_token,
    openid: this.openid
  })
  ```

## 7. 通用功能

### 7.1 退出登录
所有页面都包含退出登录功能，通过以下API调用实现：
```javascript
axios.delete(this.host + '/logout/')
```

### 7.2 获取购物车数量
多个页面都包含获取购物车数量的功能，通过以下API调用实现：
```javascript
axios.get(this.host + '/carts/simple/')
``` 
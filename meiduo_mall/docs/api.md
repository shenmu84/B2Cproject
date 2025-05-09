# Meiduo Mall API 文档

## 目录
1. [用户模块](#1-用户模块-users)
2. [商品模块](#2-商品模块-goods)
3. [购物车模块](#3-购物车模块-carts)
4. [订单模块](#4-订单模块-orders)
5. [支付模块](#5-支付模块-payment)
6. [搜索模块](#6-搜索模块-search)
7. [广告模块](#7-广告模块-contents)
8. [通用说明](#通用说明)

## 1. 用户模块 (users)

### 1.1 用户注册
- **URL**: `/api/v1/users/register/`
- **Method**: POST
- **Description**: 用户注册
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string",
    "password2": "string",
    "email": "string",
    "mobile": "string"
  }
  ```
- **Response**:
  ```json
  {
    "code": 0,
    "message": "注册成功",
    "data": {
      "id": "integer",
      "username": "string",
      "email": "string",
      "mobile": "string",
      "date_joined": "datetime",
      "last_login": "datetime"
    }
  }
  ```

### 1.2 用户登录
- **URL**: `/api/v1/users/login/`
- **Method**: POST
- **Description**: 用户登录
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "code": 0,
    "message": "登录成功",
    "data": {
      "token": "string",
      "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "mobile": "string"
      }
    }
  }
  ```

### 1.3 用户登出
- **URL**: `/api/v1/users/logout/`
- **Method**: POST
- **Description**: 用户登出
- **Headers**: 
  - Authorization: Bearer {token}
- **Response**:
  ```json
  {
    "code": 0,
    "message": "登出成功"
  }
  ```

### 1.4 用户信息
- **URL**: `/api/v1/users/profile/`
- **Method**: GET/PUT
- **Description**: 获取/更新用户信息
- **Headers**: 
  - Authorization: Bearer {token}
- **Response (GET)**:
  ```json
  {
    "code": 0,
    "data": {
      "id": "integer",
      "username": "string",
      "email": "string",
      "mobile": "string",
      "date_joined": "datetime",
      "last_login": "datetime"
    }
  }
  ```
- **Request Body (PUT)**:
  ```json
  {
    "email": "string",
    "mobile": "string"
  }
  ```

## 2. 商品模块 (goods)

### 2.1 商品列表
- **URL**: `/api/v1/goods/`
- **Method**: GET
- **Description**: 获取商品列表
- **Query Parameters**:
  - category_id: integer (可选)
  - page: integer (默认1)
  - page_size: integer (默认10)
- **Response**:
  ```json
  {
    "code": 0,
    "data": {
      "count": "integer",
      "next": "string",
      "previous": "string",
      "results": [
        {
          "id": "integer",
          "name": "string",
          "price": "decimal",
          "sales": "integer",
          "comments": "integer",
          "image": "string"
        }
      ]
    }
  }
  ```

### 2.2 商品详情
- **URL**: `/api/v1/goods/<sku_id>/`
- **Method**: GET
- **Description**: 获取商品详情
- **Response**:
  ```json
  {
    "code": 0,
    "data": {
      "id": "integer",
      "name": "string",
      "price": "decimal",
      "sales": "integer",
      "comments": "integer",
      "image": "string",
      "description": "string",
      "specs": [
        {
          "name": "string",
          "value": "string"
        }
      ]
    }
  }
  ```

## 3. 购物车模块 (carts)

### 3.1 购物车操作
- **URL**: `/api/v1/carts/`
- **Method**: POST/GET/PUT/DELETE
- **Description**: 购物车增删改查
- **Headers**: 
  - Authorization: Bearer {token} (可选)
- **Request Body (POST)**:
  ```json
  {
    "sku_id": "integer",
    "count": "integer",
    "selected": "boolean"
  }
  ```
- **Request Body (PUT)**:
  ```json
  {
    "sku_id": "integer",
    "count": "integer",
    "selected": "boolean"
  }
  ```
- **Request Body (DELETE)**:
  ```json
  {
    "sku_id": "integer"
  }
  ```
- **Response (GET)**:
  ```json
  {
    "code": 0,
    "data": {
      "carts": [
        {
          "id": "integer",
          "sku": {
            "id": "integer",
            "name": "string",
            "price": "decimal",
            "image": "string"
          },
          "count": "integer",
          "selected": "boolean"
        }
      ],
      "total_amount": "decimal",
      "total_count": "integer"
    }
  }
  ```

### 3.2 购物车选择
- **URL**: `/api/v1/carts/selection/`
- **Method**: PUT
- **Description**: 全选/取消全选
- **Headers**: 
  - Authorization: Bearer {token} (可选)
- **Request Body**:
  ```json
  {
    "selected": "boolean"
  }
  ```

## 4. 订单模块 (orders)

### 4.1 订单创建
- **URL**: `/api/v1/orders/`
- **Method**: POST
- **Description**: 创建订单
- **Headers**: 
  - Authorization: Bearer {token}
- **Request Body**:
  ```json
  {
    "address_id": "integer",
    "pay_method": "integer",
    "remark": "string"
  }
  ```
- **Response**:
  ```json
  {
    "code": 0,
    "data": {
      "order_id": "string",
      "order_number": "string"
    }
  }
  ```

### 4.2 订单列表
- **URL**: `/api/v1/orders/`
- **Method**: GET
- **Description**: 获取订单列表
- **Headers**: 
  - Authorization: Bearer {token}
- **Query Parameters**:
  - page: integer (默认1)
  - page_size: integer (默认10)
- **Response**:
  ```json
  {
    "code": 0,
    "data": {
      "count": "integer",
      "next": "string",
      "previous": "string",
      "results": [
        {
          "order_id": "string",
          "order_number": "string",
          "total_amount": "decimal",
          "pay_method": "integer",
          "status": "integer",
          "create_time": "datetime"
        }
      ]
    }
  }
  ```

## 5. 支付模块 (payment)

### 5.1 支付
- **URL**: `/api/v1/payment/<order_id>/`
- **Method**: GET
- **Description**: 获取支付链接
- **Headers**: 
  - Authorization: Bearer {token}
- **Response**:
  ```json
  {
    "code": 0,
    "data": {
      "alipay_url": "string"
    }
  }
  ```

### 5.2 支付状态
- **URL**: `/api/v1/payment/status/`
- **Method**: PUT
- **Description**: 查询支付状态
- **Headers**: 
  - Authorization: Bearer {token}
- **Request Body**:
  ```json
  {
    "order_id": "string"
  }
  ```
- **Response**:
  ```json
  {
    "code": 0,
    "data": {
      "status": "integer"
    }
  }
  ```

## 6. 搜索模块 (search)

### 6.1 商品搜索
- **URL**: `/api/v1/search/`
- **Method**: GET
- **Description**: 搜索商品
- **Query Parameters**:
  - keyword: string
  - category_id: integer (可选)
  - min_price: decimal (可选)
  - max_price: decimal (可选)
  - sort: string (可选)
  - page: integer (默认1)
  - page_size: integer (默认10)
- **Response**:
  ```json
  {
    "code": 0,
    "data": {
      "count": "integer",
      "next": "string",
      "previous": "string",
      "results": [
        {
          "id": "integer",
          "name": "string",
          "price": "decimal",
          "sales": "integer",
          "comments": "integer",
          "image": "string"
        }
      ]
    }
  }
  ```

### 6.2 搜索建议
- **URL**: `/api/v1/search/suggest/`
- **Method**: GET
- **Description**: 获取搜索建议
- **Query Parameters**:
  - keyword: string
- **Response**:
  ```json
  {
    "code": 0,
    "data": {
      "suggestions": ["string"]
    }
  }
  ```

### 6.3 热门搜索
- **URL**: `/api/v1/search/hot/`
- **Method**: GET
- **Description**: 获取热门搜索
- **Response**:
  ```json
  {
    "code": 0,
    "data": {
      "hot_words": ["string"]
    }
  }
  ```

## 7. 广告模块 (contents)

### 7.1 广告内容
- **URL**: `/api/v1/contents/contents/`
- **Method**: POST/GET
- **Description**: 创建/获取广告内容
- **Headers**: 
  - Authorization: Bearer {token} (POST需要)
- **Request Body (POST)**:
  ```json
  {
    "category": "integer",
    "title": "string",
    "url": "string",
    "image": "string",
    "text": "string",
    "sequence": "integer",
    "status": "integer"
  }
  ```
- **Response (GET)**:
  ```json
  {
    "code": 0,
    "data": [
      {
        "id": "integer",
        "category": "integer",
        "title": "string",
        "url": "string",
        "image": "string",
        "text": "string",
        "sequence": "integer",
        "status": "integer",
        "create_time": "datetime"
      }
    ]
  }
  ```

### 7.2 广告分类
- **URL**: `/api/v1/contents/categories/`
- **Method**: POST/GET
- **Description**: 创建/获取广告分类
- **Headers**: 
  - Authorization: Bearer {token} (POST需要)
- **Request Body (POST)**:
  ```json
  {
    "name": "string",
    "key": "string"
  }
  ```
- **Response (GET)**:
  ```json
  {
    "code": 0,
    "data": [
      {
        "id": "integer",
        "name": "string",
        "key": "string",
        "contents": [
          {
            "id": "integer",
            "title": "string",
            "url": "string",
            "image": "string",
            "text": "string",
            "sequence": "integer",
            "status": "integer"
          }
        ]
      }
    ]
  }
  ```

### 7.3 首页内容
- **URL**: `/api/v1/contents/index/`
- **Method**: GET
- **Description**: 获取首页内容
- **Response**:
  ```json
  {
    "code": 0,
    "data": {
      "index_banner": [
        {
          "id": "integer",
          "title": "string",
          "url": "string",
          "image": "string",
          "text": "string"
        }
      ],
      "index_new": [
        {
          "id": "integer",
          "title": "string",
          "url": "string",
          "image": "string",
          "text": "string"
        }
      ]
    }
  }
  ```

## 通用说明

### 响应格式
所有API响应都遵循以下格式：
```json
{
  "code": "integer",    // 状态码：0表示成功，非0表示错误
  "message": "string",  // 响应消息
  "data": "any"        // 响应数据
}
```

### 错误码说明
- 0: 成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 500: 服务器错误

### 认证方式
需要认证的API需要在请求头中添加：
```
Authorization: Bearer {token}
```

### 分页说明
支持分页的API都支持以下查询参数：
- page: 页码，默认1
- page_size: 每页数量，默认10

### 缓存说明
部分API使用了缓存机制，缓存时间根据具体业务需求设置。

### 限流说明
部分API使用了限流机制，具体限制根据业务需求设置。 
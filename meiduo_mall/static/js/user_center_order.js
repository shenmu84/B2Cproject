// 获取订单列表
axios.get(this.host + '/orders/', {
    responseType: 'json',
    withCredentials: true
})

// 获取订单详情
axios.get(this.host + '/orders/' + order_id + '/', {
    responseType: 'json',
    withCredentials: true
}) 
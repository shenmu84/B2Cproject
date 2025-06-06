var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        is_show_waiting: true,

        error_password: false,
        error_phone: false,
        error_sms_code: false,
        error_phone_message: '',
        error_sms_code_message: '',

        sms_code_tip: '获取短信验证码',
        sending_flag: false, // 正在发送短信标志

        password: '',
        mobile: '',
        sms_code: '',
        access_token: '',

        image_code:'',
        error_image_code_message:'',
        error_image_code:'',
        image_code_url:''
    },
    mounted: function(){
        // 获取图形验证码:
        this.generate_image_code()

        // 从路径中获取qq重定向返回的code
        var code = this.get_query_string('code');
        console.log('获取到的code:', code); // 添加日志
        
        axios.get(this.host + '/oauth_callback/?code=' + code, {
                responseType: 'json',
            withCredentials: true,
            crossDomain: true
            })
            .then(response => {
                console.log('后端响应数据:', response.data); // 添加日志
            if (response.data.code == 0) {
                    // 用户已绑定
                    var state = this.get_query_string('state');
                    location.href = '/manage/index.html';
                } else {
                    // 用户未绑定
                    this.access_token = response.data.access_token;
                    this.is_show_waiting = false;
                }
            })
            .catch(error => {
            console.log('错误详情:', error);
            if (error.response) {
                console.log('错误响应:', error.response.data);
                console.log('错误状态:', error.response.status);
            } else if (error.request) {
                console.log('请求错误:', error.request);
            } else {
                console.log('Error:', error.message);
            }
            this.is_show_waiting = false; // 出错时也显示表单
            alert('服务器异常，请稍后再试');
        });

        // 添加超时保护
        setTimeout(() => {
            if (this.is_show_waiting) {
                this.is_show_waiting = false;
                console.log('加载超时，强制显示表单');
            }
        }, 5000);
    },
    methods: {
              // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
		generate_image_code: function(){
			// 生成一个编号 : 严格一点的使用uuid保证编号唯一， 不是很严谨的情况下，也可以使用时间戳
			this.image_code_id = generateUUID();
			// 设置页面中图片验证码img标签的src属性
			this.image_code_url = this.host + "/image_codes/" + this.image_code_id + "/";
		},
        // 获取url路径参数
        get_query_string: function(name){
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
            }
            return null;
        },
        check_pwd: function (){
            var len = this.password.length;
            if(len<8||len>20){
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },
        check_phone: function (){
            var re = /^1[345789]\d{9}$/;
            if(re.test(this.mobile)) {
                this.error_phone = false;
            } else {
                this.error_phone_message = '您输入的手机号格式不正确';
                this.error_phone = true;
            }
        },
        check_sms_code: function(){
            if(!this.sms_code){
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        // 检查图片验证码
		check_image_code: function (){
			if(!this.image_code) {
				this.error_image_code_message = '请填写图片验证码';
				this.error_image_code = true;
			} else {
				this.error_image_code = false;
			}
		},
        // 发送手机短信验证码
        send_sms_code: function(){
            if (this.sending_flag == true) {
                return;
            }
            this.sending_flag = true;

            // 校验参数，保证输入框有数据填写
            this.check_phone();

            if (this.error_phone == true) {
                this.sending_flag = false;
                return;
            }

            // 向后端接口发送请求，让后端发送短信验证码
            // var url = this.host + '/sms_codes/' + this.mobile + '/'
            // 向后端接口发送请求，让后端发送短信验证码
            var url = this.host + '/sms_codes/' + this.mobile + '/' + '?image_code=' + this.image_code
                + '&image_code_id=' + this.image_code_id
            axios.get(url, {
                    responseType: 'json',
                    withCredentials:true,
                })
                .then(response => {
                    // 表示后端发送短信成功
                    // 倒计时60秒，60秒后允许用户再次点击发送短信验证码的按钮
                    var num = 60;
                    // 设置一个计时器
                    var t = setInterval(() => {
                        if (num == 1) {
                            // 如果计时器到最后, 清除计时器对象
                            clearInterval(t);
                            // 将点击获取验证码的按钮展示的文本回复成原始文本
                            this.sms_code_tip = '获取短信验证码';
                            // 将点击按钮的onclick事件函数恢复回去
                            this.sending_flag = false;
                        } else {
                            num -= 1;
                            // 展示倒计时信息
                            this.sms_code_tip = num + '秒';
                        }
                    }, 1000, 60)
                })
                .catch(error => {
                    if (error.response.status == 400) {
                        this.error_sms_code = '图片验证码有误';
                        this.error_sms_code_message = true;
                    } else {
                        console.log(error.response.data);
                    }
                    this.sending_flag = false;
                })
        },
       // 保存
        on_submit: function(){
            this.check_pwd();
            this.check_phone();
            this.check_sms_code();

            if(this.error_password == false && this.error_phone == false && this.error_sms_code == false) {
                axios.post(this.host + '/oauth_callback/', {
                        password: this.password,
                        mobile: this.mobile,
                        sms_code: this.sms_code,
                        access_token: this.access_token
                    }, {
                        responseType: 'json',
                        withCredentials:true,
                    })
                    .then(response => {
                        // 记录用户登录状态
                        location.href = '/manage/index.html'
                    })
                    .catch(error=> {
                        if (error.response.status == 400) {
                            this.error_sms_code_message = error.response.data.message;
                            this.error_sms_code = true;
                        } else {
                            console.log(error.response.data);
                        }
                    })
            }
        }
    }
});
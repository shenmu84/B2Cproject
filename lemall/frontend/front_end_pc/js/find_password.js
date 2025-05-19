var vm = new Vue({
    el: '#app',
    data: {
        host: 'http://localhost:8000',
        
        // 当前操作的步骤
        step: 1,

        // 第一步的数据
        username: '',
        image_code: '',
        image_code_id: '',
        image_code_url: '',

        // 第二步的数据
        mobile: '',
        sms_code: '',
        sms_code_tip: '获取短信验证码',
        sending_flag: false,

        // 第三步的数据
        password: '',
        password2: '',

        // 错误提示
        error_username: false,
        error_image_code: false,
        error_sms_code: false,
        error_password: false,
        error_password2: false,

        // 错误提示信息
        error_username_message: '',
        error_image_code_message: '',
        error_sms_code_message: '',
        error_password_message: '',
        error_password2_message: ''
    },
    mounted: function(){
        // 生成图形验证码
        this.generate_image_code();
    },
    methods: {
        // 生成图形验证码
        generate_image_code: function(){
            this.image_code_id = generateUUID();
            this.image_code_url = this.host + "/verifications/imagecodes/" + this.image_code_id + "/";
        },
        // 检查账号
        check_username: function(){
            if (!this.username) {
                this.error_username_message = '请填写账号';
                this.error_username = true;
                return;
            }
            if (!this.image_code) {
                this.error_image_code_message = '请填写验证码';
                this.error_image_code = true;
                return;
            }
            
            // 验证用户名和验证码
            axios.get(this.host + '/accounts/' + this.username + '/findpassword/check/', {
                    responseType: 'json',
                    params: {
                        text: this.image_code,
                        image_code_id: this.image_code_id
                    }
                })
                .then(response => {
                    this.mobile = response.data.mobile;
                    this.step = 2;
                })
                .catch(error => {
                    if (error.response.status == 400) {
                        this.error_image_code_message = '验证码错误';
                        this.error_image_code = true;
                    } else if (error.response.status == 404) {
                        this.error_username_message = '账号不存在';
                        this.error_username = true;
                    } else {
                        console.log(error.response.data);
                    }
                })
        },
        // 发送短信验证码
        send_sms_code: function(){
            if (this.sending_flag) {
                return;
            }
            this.sending_flag = true;
            
            // 发送短信验证码
            axios.get(this.host + '/verifications/smscodes/' + this.mobile + '/', {
                    responseType: 'json'
                })
                .then(response => {
                    // 表示发送成功
                    let num = 60;
                    let t = setInterval(() => {
                        if (num == 1) {
                            clearInterval(t);
                            this.sms_code_tip = '获取短信验证码';
                            this.sending_flag = false;
                        } else {
                            num -= 1;
                            this.sms_code_tip = num + '秒';
                        }
                    }, 1000);
                })
                .catch(error => {
                    alert(error.response.data.message);
                    this.sending_flag = false;
                })
        },
        // 检查短信验证码
        check_sms_code: function(){
            if (!this.sms_code) {
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
                return;
            }
            
            // 验证短信验证码
            axios.get(this.host + '/accounts/' + this.username + '/findpassword/smscode/', {
                    responseType: 'json',
                    params: {
                        sms_code: this.sms_code
                    }
                })
                .then(response => {
                    this.step = 3;
                })
                .catch(error => {
                    if (error.response.status == 400) {
                        this.error_sms_code_message = '验证码错误';
                        this.error_sms_code = true;
                    } else {
                        console.log(error.response.data);
                    }
                })
        },
        // 检查密码
        check_pwd: function(){
            if (!this.password) {
                this.error_password_message = '请填写密码';
                this.error_password = true;
                return;
            }
            if (this.password.length < 8 || this.password.length > 20) {
                this.error_password_message = '密码长度应为8-20个字符';
                this.error_password = true;
                return;
            }
            this.error_password = false;

            if (!this.password2) {
                this.error_password2_message = '请填写确认密码';
                this.error_password2 = true;
                return;
            }
            if (this.password != this.password2) {
                this.error_password2_message = '两次输入的密码不一致';
                this.error_password2 = true;
                return;
            }
            this.error_password2 = false;

            // 设置新密码
            axios.post(this.host + '/accounts/' + this.username + '/password/', {
                    password: this.password
                }, {
                    responseType: 'json'
                })
                .then(response => {
                    this.step = 4;
                })
                .catch(error => {
                    alert(error.response.data.message);
                })
        }
    }
});

// 生成UUID
function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
} 
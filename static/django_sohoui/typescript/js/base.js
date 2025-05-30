
var pcd = new Vue({
    el: '#app',
    data:{
        isCollapse: false,
        tabPosition: 'top',
        editableTabs: [
            {
                title: 'Tab 1',
                name: '1',
                content: 'Tab 1 content'
            }, 
            {
                title: 'Tab 2',
                name: '2',
                content: 'Tab 2 content'
            }
        ],
        tabIndex: 2,
        isFullScreen: false,
        isEyeProtection: false,
        dialogFormVisible: false,
        form: {
            old_password: '',
            new_password1: '',
            new_password2: '',
        },
        rules: {
            old_password: [
                { required: true, message: '请输入旧密码', trigger: 'blur' },
                { min: 6, max: 16, message: '密码长度在 6 到 16 个字符', trigger: 'blur' }
            ],
            // 添加密码验证，是否输入密码   
            new_password1: [
                {
                    required: true,
                    trigger:'blur',
                    validator:(rule, value, callback) => {
                        if (value === '') {
                            callback(new Error('请输入新密码'));
                        } else {
                        
                            callback();
                        }
                    },
                  
                }
            ],
            new_password2: [
                {
                    required: true,
                    trigger:'blur',
                    validator:(rule, value, callback)=>{
                        if (value === '') {
                            callback(new Error('请输入确认密码'));
                        } else if (value !== pcd.form.new_password1) {
                            callback(new Error('两次输入密码不一致!'));
                        }
                    },
                }
            ],
         
        },
        labelPosition: 'left',
    },  
    created(){
    },
    methods: {
        handleTabsEdit(targetName, action) {
            if (action === 'add') {
                this.editableTabs.push({
                    title: 'New Tab',
                    name: this.editableTabs.length + 1, 
                    content: 'New Tab content'
                });
            } else if (action === 'remove') {
                this.editableTabs = this.editableTabs.filter(tab => tab.name !== targetName);
            }
        },
        refresh(){
            // 刷新当前页面
            window.location.reload();
        },
        fullScreen(){
            // 全屏
            document.documentElement.requestFullscreen();
            this.isFullScreen = true;
        },
        compressScreen(){
            // 退出全屏
            document.exitFullscreen();
            this.isFullScreen = false;
        },
        changePassword(){
            this.$refs['change_password_form'].validate((valid) => {
                if (valid) {
                    this.dialogFormVisible = false;
                }
            });
            let formData = new FormData();
            formData.append('old_password', this.form.old_password);
            formData.append('new_password1', this.form.new_password1);
            formData.append('new_password2', this.form.new_password2);
            formData.append('csrfmiddlewaretoken', $('input[name="csrfmiddlewaretoken"]').val());
            axios.post('/admin/password_change/', formData).then(res => {
                // 密码错误，提示错误信息
                if (res.data !== '') {
                    this.$message({
                        message: '你的旧密码不正确。请重新输入!',
                        type: 'error'
                    });
                }else{
                    this.$message({
                        message: '密码修改成功',
                        type: 'success'
                    });
                    this.dialogFormVisible = false;
                    // 重置表单
                    this.$refs.change_password_form.resetFields();
                }
            });
        },
        logout(){
            let formData = new FormData();
            formData.append('csrfmiddlewaretoken', $('input[name="csrfmiddlewaretoken"]').val());
            axios.post('/admin/logout/', formData).then(res => {
                // 跳转到登录页
                window.location.href = '/admin/login/';
            });
        }
    }
})


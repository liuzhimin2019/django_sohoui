

Vue.component('change_form', {
    template: '#change_form_template',
    data(){
        return {
            form: {},
            // switchValue: true
        }
    },
    methods: {
        goBack(){
            window.history.back();
        },
        save() {
            // 获取表单数据
            var from_id = from_id
            var form = document.getElementById(from_id)
            // submit
            form.submit()
            // let formData = new FormData($('#{{ opts.model_name }}_form'));
            // console.log(formData)
        }
    }
})
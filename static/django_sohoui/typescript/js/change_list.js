Vue.component('change_list', {
    template: '#change_list_template',
    data(){
        return {
            radio: '2',
            results: result_list,
            result_headers: result_headers,
            filter_list: filter_list,
            search_placeholder: '搜索'+search_placeholder,
            search_value: search_value
        };
    },
    mounted() {
        // 获取当前url中query的参数
        const params = new URLSearchParams(window.location.search);
        this.search_value['q'] = params.get('q') || ''
        filter_list.forEach(filter => {
            if(params.get(filter.field) == 0){
                this.search_value[filter.field] = 0;
            }else{
                this.search_value[filter.field] = parseInt(params.get(filter.field)) || '';
            }
        });
        
    },
    methods: {
        get_query(key, val){
            this.search_value[key] = val;
            console.log(this.search_value)
        },
        search() {
            preSubmit();
            document.getElementById('changelist-search').submit();
        },
        add(){
            console.log(add_url)
            window.location.href = add_url
        },
        handleEdit(row) {
            window.location.href = row.change_url
        },
        reset(){
            //获取当前url，去掉？后面的参数
            const url = window.location.href.split('?')[0];
            window.location.href = url;
        }
    }
})
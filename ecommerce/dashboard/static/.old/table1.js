var vuetable = {
    props: ["products"],
    template: "\
    <table class='highlight responsive-table'>\
        <thead>\
            <tr>\
                <th>\
                    <label>\
                        <input @click='selectall' type='checkbox' name='select-all' id='select-all' />\
                        <span></span>\
                    </label>\
                </th>\
                <th v-for='header in headers' :key='header'>{{ header|capitalize }}</th>\
            </tr>\
        </thead>\
        <tbody>\
            <tr v-if='!product.deleted' v-for='(product, index) in products' :key='product.id'>\
                <td>\
                    <p>\
                        <label>\
                            <input @click='selectitem(index)' type='checkbox' :name='product.name|slugify' :id='product.name|slugify' :checked='product.checked'>\
                            <span></span>\
                        </label>\
                    </p>\
                </td>\
                <td><a :href='producturl(product.id)'>{{ product.id }}</a></td>\
                <td>{{ product.name }}</td>\
                <td>{{ product.reference }}</td>\
                <td>{{ product.price_ht|euros }}</td>\
                <td>\
                    <a :href='updateurl(product.id)'><i class='material-icons'>create</i></a>\
                    <a @click='deletesingleitem(product.id)'><i class='material-icons'>delete</i></a>\
                </td>\
            </tr>\
        </tbody>\
    </table>\
    ",
    data() {
        return {
            headers: ["iD", "name", "reference", "price", "update"]
        }
    },
    computed: {
        nondeletedproducts() {}
    },
    methods: {
        selectitem: function() {},
        selectall: function() {},
        deletesingleitem: function() {},
        updateurl: function(id) {return "/dashboard/products/" + id + "/update"},
        producturl: function(id) {return "/dashboard/products/" + id}
    },
    filters: {
        capitalize: function(header) {return header.toUpperCase()},
        slugify: function() {},
        euros: function(value) {return value + "€"}
    }
}
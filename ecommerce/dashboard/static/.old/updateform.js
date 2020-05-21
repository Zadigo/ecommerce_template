var formbutton = {
    props: ["formbuttonname"],
    template: "\
    <button type='submit' class='btn-large indigo lighten-1 waves-effect waves-light'>\
        <i class='material-icons left'>create</i>{{ formbuttonname }}\
    </button>\
    "
}

var updateform = {
    template: "\
    <form @submit.prevent='updateitem'>\
        <div class='row'>\
            <div v-for='field in fields' :key='field.name' :class='\"input-field col s12 \" + field.size'>\
                <input :type='field.type' :name='field.name' :id='field.name' :placeholder='field.placeholder' :value='product[field.query]'>\
            </div>\
        </div>\
        <formbutton v-bind:formbuttonname='formbuttonname' />\
    </form>\
    ",
    components: {formbutton},
    data() {
        return {
            // product: JSON.parse($("#product").text()),
            product: {},
            fields: [
                {query: "name", name: "name", size: "m12 l12", type: "text", placeholder: "Nom du produit"}
            ],
            formbuttonname: "Update"
        }
    },
    methods: {
        updateitem: function() {
            
        }
    }
}
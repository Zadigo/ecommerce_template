var csrf = function() {
    return $(".csrf input").val()
}

var formfields = JSON.parse(document.getElementById('form_fields').innerText)

var newreference = function() {
    return $("#new_reference").text()
}

var formbutton = {
    props: ["formbuttonname"],
    template: "\
    <button type='submit' class='btn-large indigo lighten-1 waves-effect waves-light'>\
        <i class='material-icons left'>create</i>{{ formbuttonname }}\
    </button>\
    "
}

var picturecanvas = {
    template: "\
    "
}

var createform = {
    template: "\
    <form @submit.prevent='createitem'>\
        <div class='row'>\
            <div v-for='field in fields' :key='field.name' \
                        class='input-field col s12' :class='field.size'>\
                <input v-if='field.type !== \"file\"' v-model='newproduct[field.name]' :type='field.type' \
                        :name='field.name' :id='field.name' :value='field.value' :placeholder='field.placeholder'>\
                <input v-else @change='getfiles' :type='field.type' />\
            </div>\
        </div>\
        <formbutton v-bind:formbuttonname='formbuttonname' />\
    </form>\
    ",
    components: {formbutton},
    data() {
        return {
            fields: formfields,
            newproduct: {},
            formbuttonname: "Create"
        }
    },
    methods: {
        previewimage: function() {

        },
        getfiles: function(event) {
            var fileslist = event.target.files
            var formdata = new FormData()

            this.previewimage()
        },
        createitem: function() {
            var self = this
            var formdata = new FormData()
            
            $.ajax({
                type: "POST",
                url: "/dashboard/products/new",
                data: {"product": self.$data.newproduct, "csrfmiddlewaretoken": csrf()},
                dataType: "json",
                success: function (response) {
                    window.location.href = response.redirect_url
                }
            });
        }
    }
}
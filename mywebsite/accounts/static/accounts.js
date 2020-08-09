var sendajax = function(formname, data) {
    data["form_id"] = formname
    data["csrfmiddlewaretoken"] = $(".csrf input[type='hidden']").val()
    $.ajax({
        type: "POST",
        url: window.location.href,
        data: data,
        dataType: "json",
        success: function (response) {
            M.toast({"html": "Profil mis à jour"})
            return response
        },
        error: function(response) {
            M.toast({"html": "Oops ! Une erreur est survenue"})
            return response
        }
    });
}

var submitbutton = {
    props: ["response"],
    template: "\
    <button type='submit' class='btn waves-effect waves-light light-blue lighten-1'><i class='material-icons left'>check</i>Valider</button>\
    "
}

var detailsform = {
    components: {submitbutton},
    template: "\
        <form @submit.prevent='modifyprofile'>\
            <div v-for='input in inputs' :key='input.name' class='input-field'>\
                <input v-model='userdata[input.name]' :type='input.type' :name='input.name' :id='input.id' :placeholder='input.placeholder' :autocomplete='input.autocomplete' />\
            </div>\
            <submitbutton />\
        </form>\
    ",
    data() {
        return {
            inputs: [
                {type: "text", name: "address", id: "address", placeholder: "Address", autocomplete: "street-address"},
                {type: "text", name: "city", id: "city", placeholder: "City", autocomplete: "address-level2"},
                {type: "text", name: "zip_code", id: "postal-code", placeholder: "Postal code", autocomplete: "postal-code"},
            ],
            userdata: {},
        }
    },
    methods: {
        modifyprofile: function() {
            response = sendajax('detailsform', this.$data.userdata)
        }
    }
}

var userform = {
    components: {submitbutton},
    template: "\
        <form @submit.prevent='modifyprofile'>\
            <div v-for='input in inputs' :key='input.name' class='input-field'>\
                <input v-model='userdata[input.name]' :type='input.type' :name='input.name' :id='input.id' :placeholder='input.placeholder' :autocomplete='input.autocomplete' />\
            </div>\
            <submitbutton />\
        </form>\
    ",
    data() {
        return {
            inputs: [
                {type: "text", name: "name", id: "name", placeholder: "Name", autocomplete: "given-name"},
                {type: "text", name: "surname", id: "surname", placeholder: "Surname", autocomplete: "family-name"}
            ],
            userdata: {}
        }
    },
    methods: {
        modifyprofile: function() {
            response = sendajax('userform', this.$data.userdata)
        }
    }
}

var profile = new Vue({
    el: "#app",
    components: {userform, detailsform}
})
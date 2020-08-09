var csrf = function() {
    return $(".csrf").find("input").val()
}

var initial = JSON.parse($("#forms").text())

var formcomponent = {
    props: ["fields", "formname"],
    template: "\
    <form @submit.prevent='submitform' :id='formname'>\
        <div v-for='field in fields' :key='field.id' class='input-field'>\
            <input v-model='datatosubmit[field.name]' :type='field.text' :name='field.name' id='field.name'\
                :autocomplete='field.autocomplete' :placeholder='field.placeholder'>\
        </div>\
        <button type='submit' class='btn-large' :class='{\"disabled\": hasdata}'>\
            <i class='material-icons left'>done</i>Valider\
        </button>\
    </form>\
    ",
    data() {
        return {
            datatosubmit: {}
        }
    },
    mounted() {
        // : Raises an error because the initial value is not
        // yet defined when the component is created
        // this.$data.datatosubmit = initial[this.$props.formname]
    },
    computed: {
        hasdata() {
            var keyslength = Object.keys(this.$data.datatosubmit).length > 0
            if (keyslength === true) {
                return false
            } else {
                return true
            }
        }
    },
    methods: {
        submitform: function() {
            var formdata = new FormData()
            formdata.append("form_id", this.$props.formname)
            formdata.append("csrfmiddlewaretoken", csrf())

            Object.keys(this.$data.datatosubmit).forEach(key => {
                formdata.append(key, this.$data.datatosubmit[key])
            })

            var promise = new Promise((resolve, reject) => {
                var xhr = new XMLHttpRequest()
                xhr.open("POST", window.location.href)
                xhr.send(formdata)
                resolve(xhr.response)
            })
            promise.then(response => {
                console.log(response)
            })
        }
    }
}

var profileapp = new Vue({
    el: '#profile_app',
    components: {formcomponent},
    data() {
        return {
            form1: [
                {id: 1, type: "text", name: "name", autocomplete: "family-name", placeholder: "Nom"},
                {id: 2, type: "text", name: "surname", autocomplete: "given-name", placeholder: "Prénom"}
            ],
            form2: [
                {id: 1, type: "text", name: "address", autocomplete: "address-level1", placeholder: "Addresse"},
                {id: 2, type: "text", name: "city", autocomplete: "address-level2", placeholder: "Département"},
                {id: 3, type: "text", name: "zip_code", autocomplete: "postal-code", placeholder: "Code postal"}
            ]
        }
    }
})
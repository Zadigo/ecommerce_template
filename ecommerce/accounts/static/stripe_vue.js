var stripecard = new Vue({
    el: "#app",
    template: "\
        <form @submit.prevent='createpayment' id='payment_form'>\
            <div id='card_element'></div>\
            <button class='btn red darken-3 waves-effect waves-light'>\
                <i class='material-icons left'>credit_card</i>\
                Payer\
            </button>\
        </form>\
    ",
    data() {
        return {
            stripe: undefined,
            card: undefined
        }
    },
    mounted() {
        this.$data.stripe = Stripe("pk_test_eo8zzqww6iuVFzWmLQEJ4F7K")
        var elements = this.$data.stripe.elements()
        var style = {
            base: {
                fontWeight: 500,
                fontFamily: 'Raleway, Roboto',
                fontSize: '16px'
            }
        }
        this.$data.card = elements.create('card', {style: style})
        this.$data.card.mount("#card_element")
    },
    methods: {
        createpayment: function() {
            var self = this
            this.$data.stripe.createToken(this.$data.card).then(function(result) {
                if(result.error) {
                    var errorElement = document.getElementById("card-errors")
                    errorElement.textContent = result.error.message 
                } else {
                    self.tokenhandler(result)
                }
            })
        },
        tokenhandler: function(data) {
            var processUri = window.location.href + 'payment-process/'
            var token = data.token.id

            // var addressForm = $('#address_form')
            // var informationForm = $("#information_form")

            // console.log(token)
        }
    }
})
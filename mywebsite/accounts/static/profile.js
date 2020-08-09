$(document).ready(function() {
    var uri = window.location.href;

    // BASE PROFILE FORM
    $('#base-profile-form').on('submit', function(e){
        e.preventDefault();

        var data = $(this).serialize();
        var form_id = '&form_id=' + $(this).attr('id');

        $.ajax({
            type: "POST",
            url: uri,
            data: data + form_id,
            dataType: "json",
            success: function (response) {
                // DO SOMETHING
            },
            error: function(response, data) {
                console.log(data);
            }
        });
    })

    // ADDRESS PROFILE FORM
    $('#address-profile-form').on('submit', function(e){
        e.preventDefault();

        var data = $(this).serialize();
        var form_id = '&form_id=' + $(this).attr('id');

        $.ajax({
            type: "POST",
            url: uri,
            data: data + form_id,
            dataType: "json",
            success: function (response) {
                // DO SOMETHING
            },
            error: function(response, data) {
                console.log(data);
            }
        });
    })
})
$(function() {
    $('#btnSignUp').click(function() {


        $.ajax({
            url: '/signUp',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
                alert("User created Sucessfully");
            },
            error: function(error) {
                console.log(error);
                alert(error);
            }
        });
    });
});
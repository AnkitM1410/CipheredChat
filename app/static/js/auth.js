$(document).ready(function() {
    var login_form=true

    function show_error_message(msg){
        $('#error_message').show()
        $('#error_message').text(msg)
    }

    $("#user_id_input").on("input", function () { 
        var user_id = $(this).val();
        if(user_id.length > 0){
            user_id = user_id.toLowerCase()
            $(this).val(user_id)
            $.ajax({
                type: "GET",
                url: window.location.origin + "/authentication/user_id_available/"+user_id,
                success: function (response) {
                    if(response){
                        // $("#user_id_input").removeClass("focus:ring-blue-500").removeClass("focus:ring-red-500").addClass("focus:ring-green-500")
                        $("#user_id_input").removeClass("bg-gray-700").removeClass("bg-red-700").addClass("bg-green-700")
                    }else{
                        $("#user_id_input").removeClass("bg-gray-700").removeClass("bg-green-700").addClass("bg-red-700")

                    }
                },
                error: function (response) {  }
            })
        }else{
            $("#user_id_input").removeClass("bg-green-600").removeClass("bg-red-600").addClass("bg-gray-600")

        }
     })

    $('#auth_form').on('submit', function (e) {
        e.preventDefault();

        var form_submitable = false
        var msg=''

        const form = $(this); // jQuery object for the form
        const formData = form.serializeArray(); // Get form data as an array of {name, value}
        const jsonData = {};

        if(login_form){
            formData.forEach(item => {
                if (item.name=='email_id' || item.name=='password' ){
                    jsonData[item.name] = item.value;
                }
            });

            if (jsonData.email_id || jsonData.password){
                jsonData['password'] = sha256(jsonData['password']);
                form_submitable=true
                submit_url=window.location.origin+'/authentication/login'
            }
        }else{
            formData.forEach(item => {
                    jsonData[item.name] = item.value;
            });

            if (jsonData.email_id || jsonData.user_id || jsonData.first_name || jsonData.last_name || jsonData.password || jsonData.confirm_password){
                if (jsonData.password==jsonData.confirm_password){
                jsonData['password'] = sha256(jsonData['password']);
                jsonData['confirm_password'] = sha256(jsonData['confirm_password']);
                form_submitable=true
                submit_url=window.location.origin+'/authentication/signup'
                }else{
                    show_error_message('Password and Confirm password do not match.')
                }
            }
        }

        if(form_submitable){
                $.ajax({
                    url: submit_url,
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(jsonData),
                    success: function (response) {
                        if (response.status==true){
                            if (!login_form){
                                window.location.href='/welcome'
                            }else{
                                show_error_message(response.msg);
                                window.location.href='/c'
                            }
                        }else{
                            show_error_message(response.msg);
                        }
                        
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        console.log("Login failed:", textStatus, errorThrown);
                    }
                });
        }

    });


    $("#form_switch").click(function() {
        if (login_form){
            $('#form_switch').text("Login");
            $('#form_switch_text').text("Already have an account ? ");
            $('#form_instruction').text('Create an account.');
            $('#submit_btn').text('Sign Up');
            $("#first_name input[type='text'], #last_name input[type='text'], #user_id input[type='text'], #password input[type='password'], #confirm_password input[type='password'], #terms_conditions").val('');
            $("#first_name, #last_name, #confirm_password, #terms_conditions, #user_id").show();
            $("#first_name_input, #last_name_input, #confirm_password_input, #terms_conditions_input, #user_id_input").prop('required', true);
        }else{
            $('#form_switch').text("Sign Up") 
            $('#form_switch_text').text("Don't have an account? ")
            $('#form_instruction').text('Login to your account.')
            $('#submit_btn').text('Login')
            $("#password input[type='password']").val('')
            $("#first_name, #last_name, #confirm_password, #terms_conditions, #user_id").hide()
            $("#first_name_input, #last_name_input, #confirm_password_input, #terms_conditions_input, #user_id_input").prop('required', false);
        }     
        login_form=!login_form
    });
});

$(document).ready(function() {
    // all custom jQuery will go here
    $("#prof_pic").change(function(){
  $("#prof_pic").text(this.files[0].name);
});

    $('.timepicker').mdtimepicker();


    // JQuery event handler for checking if email addresses match
    $("#NewEmail1, #NewEmail2").keyup(checkEmailMatch);
    // JQuery event handler for checking if passwords match
   $("#NewPass, #ConfirmNewPass").keyup(checkPasswordMatch);
   // JQuery event handler for only checking passwords (not email or other fields)
   $("#NewPass1, #NewPass2").keyup(onlyCheckPasswordMatch);
   // JQuery event handler for ensuring name fields are not empty
    $("#firstName, #lastName").keyup(nonEmptyFields);


});

       // We want to disable the "Submit" button until all forms are valid
       var passMatch = false;
       var emailMatch = false;
       var emailChangeMatch = false;
       var everythingValid = false;
       var enableNameSubmit = false;
       const NewPass1 = "NewPass1";
       const NewPass2 = "NewPass2";
       const newPassSubmit = "newPassSubmit";
       submitToggle();
       passwordSubmitToggle();
       nameSubmitToggle();
       emailSubmitToggle();


       // Used for matching email validation
        function checkEmailMatch() {
            var email = $("#NewEmail1").val();
            var confirmEmail = $("#NewEmail2").val();
            emailMatch = false; // If this function is reused, want to make sure it's false first
            emailChangeMatch = false;
            submitToggle(); // Start submit button as disabled
            emailSubmitToggle();

            // Emails do not match
            // Disable the submit button and inform the user
            if(email != confirmEmail) {
                emailMatch = false;
                emailChangeMatch = false;
                emailSubmitToggle();
                checkIfEverythingIsValid();
                submitToggle();
                $('#divCheckEmailMatch').html(("Email does not match.").fontcolor("red"));
            }
            // Emails match and are not left blank
                // Enable the submit button and inform the user that they successfully entered
                // the email address in correctly
            else if(email != ""){
                emailMatch = true;
                emailChangeMatch = true;
                $('#divCheckEmailMatch').html(("Valid email.").fontcolor("green"));
                checkIfEverythingIsValid();
                submitToggle();
                emailSubmitToggle();
            }


        }
        // Used for only forms that only involve validating passwords
        function onlyCheckPasswordMatch(){

            var password = $('#NewPass1').val();
            var confirmPassword = $('#NewPass2').val();
            passMatch = false;
            passwordSubmitToggle();
            // If the passwords do not match, display the error message and disable the submit button
            if (password != confirmPassword) {
                passMatch = false;
                passwordSubmitToggle();
                $("#divCheckPasswordMatch").html(("Passwords do not match.").fontcolor("red"));
            }
            // If the password match but are not in the acceptable format, disabled the submit button
            // and display the erorr message
            else {
                if((password.length < 5 || password.length > 12) || !(containsLowerCase(password) && containsUpperCase(password))
                    || !(containsSymbol(password) || containsNumber(password))) {
                   $("#divCheckPasswordMatch").html(("Password must be 5-12 characters long," +
                       "contain at least one symbol or number, one uppercase letter, and one lowercase letter").fontcolor('red'));
                   passMatch = false;
                   passwordSubmitToggle();
                }
                // Password is valid, make sure the submit button is enabled and inform the user
                // that the password is valid
                else {
                     $("#divCheckPasswordMatch").html(("Password is valid.").fontcolor('green'));
                    passMatch = true;
                    passwordSubmitToggle()

                }
            }



        }

        // Used for matching password validation
        // Pass this function "password HTML ID 1, password HTML ID2"
        function checkPasswordMatch() {
            var password = $("#NewPass").val();
            var confirmPassword = $("#ConfirmNewPass").val();
            everythingValid = false;
            submitToggle();
            if (password != confirmPassword) {
                passMatch = false;
                checkIfEverythingIsValid();
                submitToggle();
                $("#divCheckPasswordMatch").html(("Passwords do not match.").fontcolor("red"));
            }
            // Password length must be between 5-12 characters
            else {
                if((password.length < 5 || password.length > 12) || !(containsLowerCase(password) && containsUpperCase(password))
                    || !(containsSymbol(password) || containsNumber(password))) {
                   $("#divCheckPasswordMatch").html(("Password must be 5-12 characters long," +
                       "contain at least one symbol or number, one uppercase letter, and one lowercase letter").fontcolor('red'));
                   passMatch = false;
                   checkIfEverythingIsValid();
                   // Disable the submit button until password length is accepted
                   submitToggle();
                }
                // Password is valid
                else {
                     $("#divCheckPasswordMatch").html(("Password is valid.").fontcolor('green'));
                    passMatch = true;
                    // Make sure everything else is valid too (in addition to the password)
                    checkIfEverythingIsValid();
                    submitToggle();

                }
            }
        }
        // Validator to ensure that all form fields are filled out by the user
        function nonEmptyFields() {
            var firstName = $('#firstName').val();
            var lastName = $('#lastName').val();
            enableNameSubmit = false;
            nameSubmitToggle();

            // If either field is null, inform user that they need to fill it out and disable submit
            if(firstName==null || firstName=="", lastName ==null || lastName ==""){
                $("#divAllFieldsCompleted").html("You must fill out both first and last name to continue.".fontcolor('red'));
                enableNameSubmit = false;
                nameSubmitToggle();
            }
            else{
                $("#divAllFieldsCompleted").html("");
                enableNameSubmit = true;
                nameSubmitToggle()
            }
        }

        // Check if All forms are valid.
        function checkIfEverythingIsValid(){
            if(passMatch && emailMatch)
                everythingValid = true;
            else
                everythingValid = false;
        }

        // When the user selects a new profile picture, this displays the file name
        $('#prof_change').on('change',function(){
                // Name of the file
                var fileName = $('#prof_change').val();
                // Get rid of the path -- only show the file name
                fileName =  fileName.replace(/^.*[\\\/]/, '');
                // Replace "Choose image" with the file name
                $('.custom-file-label').html(fileName);
        })


        // Toggle the submit button. If all forms are valid, it will be enabled for clicking.
        function submitToggle(){
            if(document.getElementById('SubmitNewAcct') != null)
                document.getElementById('SubmitNewAcct').disabled = !everythingValid;
        }

        // Toggle submit button for a form that only contains password setting
        function passwordSubmitToggle(){
            if(document.getElementById('newPassSubmit') != null)
                document.getElementById('newPassSubmit').disabled = !passMatch;
        }

        // Function for toggling submit on name form
        function nameSubmitToggle(){
            if(document.getElementById('nameSubmit')!=null)
                document.getElementById('nameSubmit').disabled = !enableNameSubmit;
        }

        // For the change email page, this toggles the submit button
        function emailSubmitToggle(){
            if(document.getElementById('emailSubmit')!=null)
                document.getElementById('emailSubmit').disabled = !emailChangeMatch;
        }

        // ----- Partially referenced from https://stackoverflow.com/questions/19605150/regex-for-password-must-contain-at-least-eight-characters-at-least-one-number-a
        // Last accessed 11/29/2020
        // Regular expressions used for password checking

        // Make sure password contains a symbol
        function containsSymbol(password){
            regExp = new RegExp("[-!$%^&*()_+|~=`{}\\[\\]:\";'<>?,.\\/]")
            return regExp.test(password);
        }
        // Make sure that the password contains at least 1 number
        function containsNumber(password){
            const regExp = new RegExp("[0-9]+");
            return regExp.test(password);
        }

        // Make sure that the password contains at least 1 uppercase letter
        function containsUpperCase(password){
            const regExp = new RegExp("[A-Z]");
            return regExp.test(password);
        }

        // Make sure that the password contains at least 1 lowercase letter
        function containsLowerCase(password){
            const regExp = new RegExp('[a-z]');
            return regExp.test(password);
        }
        // --------- End of reference ------------------------------------------------

        // JQuery datepicker functions
        $(function () {
                $("#datepicker1").datepicker({
                format: 'DD/MM/YYYY',
            });

            });

         $(function () {
                $("#datepicker2").datepicker({
                format: 'DD/MM/YYYY',
            });

            });

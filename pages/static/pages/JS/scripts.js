$(document).ready(function() {
    // all custom jQuery will go here
    $("#prof_pic").change(function(){
  $("#prof_pic").text(this.files[0].name);
});

    $('.timepicker').mdtimepicker();




    /* When the user selects a graph type from the dropdown menu,
    clear a graph selection (if one is already selected) and call the appropriate
    function to insert the HTML code for the specific graph */
    $( "#GraphType" ).change(function() {
        if($('#GraphType').val=="Disabled")
            showNothing();
        else if($('#GraphType').val() == "Histogram") {
            showNothing();
            showHistogram();
        }
        else if($('#GraphType').val() == "X and Y Plot") {
            showNothing();
            show2DXY();
        }
        else if($('#GraphType').val() == "3D (X, Y, Z) Plot") {
            showNothing();
            show3DPlot();
        }
        else if($('#GraphType').val() == "Pie Chart") {
            showNothing()
            showPieChart();
        }
        else if($('#GraphType').val() == "Scatter Plot") {
            showNothing()
            showScatterPlot();

        }
        else if($('#GraphType').val() == "Bar Graph") {
            showNothing();
            showBarGraph();
        }
        else if($('#GraphType').val() == "Individual Statistic") {
            showNothing();
            showIndStat();
        }






});
    // Clear the HTML code for the Graph type
    function showNothing(){
        $('#GraphContainer').empty();

    }
    // Histogram HTML code
    function showHistogram() {
        var data = "<div class=\"graphOptions container border w-50 bg-dark\" id=\"Graph\"> </div> \
        <div class=\"row form-group\"> \
            <div class=\"col-6 auto\"> \
                <select name=\"Histogram\" id=\"Histogram\" class=\"col-sm text-center\"> \
                    <option value=\"disabled\" disable selected value>--- Statistic ---</option> \
                    \<option value = \"Age\">Age</option> \
                    \<option value = \"Distance From Campus\">Distance From Campus</option> \
                    \<option valule = \"Specific Visit Date\">Specific Visit Date</options>\
                    \<option value = \"G.P.A.\">G.P.A.</options>\
                </select> \
            </div> \
            \<div class=\"col-6-auto\">\
                \<div class='form-group'>\
                \<input type='frequency' class='form-control' id='freqDist' aria-describedby='freq' placeholder='Frequency Divisions'>\
                \</div> \
            </div>\
        </div>\
        <div class='row form-group'> \
          <button onClick='DropDownSelect('GraphType');'>Get Histogram</button> \
        </div>";
       $('#GraphContainer').append(data); // Insert it into the graph container in "VisualizationsPage.html"
}

    function show2DXY(){
        var data = "<div class=\"graphOptions container border w-50 bg-dark\" id=\"Graph\"> </div> \
        \<div class=\"row form-group\"> \
           \<div class='col-6 auto'> \
           \    <select name='X-Axis' id='X-Value' class='col-sm text-center'>\
           \        <option value='disabledX' disable selected value>--- X-Axis ---</option>\
           \        <option value='Months'>Months</option> \
           \        <option value='Days in Month'>Days in Month</option>\
           \        <option value='Days in week'>Days in week</option>\
           \        <option value='Single Day'>Single Day</option>\
           \        <option value='Year'>Year</option> \
           \    </select>\
           \</div>\
           \ <div class='col-6 auto'>\
           <select name='Y-Axis' id='Y-Value' class='col-sm text-center'> \
            <option value='disabledY' disable selected value>--- Y-Axis ---</option> \
                    <option value = 'All visitors'>All Visitors</option> \
                    <option value = 'Graduate Students'>Graduate Students</option> \
                    <option valule = 'Undergraduate Students'>Undergraduate Students</option>\
                    <option value = 'Ethnicity'>Ethnicity</option>\
                    <option value = 'Age'>Age</options>\
                    <option value = 'Gender'>Gender</option>\
                    <option value = 'Benefit Chapter'>Benefit Chapter</option>\
                </select> \
           </div> \
        </div>\
        <div class='row form-group justify-content-center'> \
          <button onClick='DropDownSelect('GraphType');'>Get Graph</button>\
        </div>";
        $('#GraphContainer').append(data); // Insert it into the graph container in "VisualizationsPage.html"
    }

    function show3DPlot(){
        var data = "<div class=\"graphOptions container border w-50 bg-dark\" id=\"Graph\"> </div> \
        \<div class=\"row form-group\"> \
           \<div class='col-4 auto'> \
           \    <select name='X-Axis' id='X-Value3D' class='col-sm text-center'>\
           \        <option value='disabledX' disable selected value>--- X-Axis ---</option>\
           \        <option value = 'All visitors'>All Visitors</option> \
                    <option value = 'Graduate Students'>Graduate Students</option> \
                    <option valule = 'Undergraduate Students'>Undergraduate Students</option>\
                    <option value = 'Ethnicity'>Ethnicity</option>\
                    <option value = 'Age'>Age</options>\
                    <option value = 'Gender'>Gender</option>\
                    <option value = 'Benefit Chapter'>Benefit Chapter</option>\
           \        <option value='Months'>Months</option> \
           \        <option value='Days in Month'>Days in Month</option>\
           \        <option value='Days in week'>Days in week</option>\
           \        <option value='Single Day'>Single Day</option>\
           \        <option value='Year'>Year</option> \
           \    </select>\
           \</div>\
           \ <div class='col-4 auto'>\
           <select name='Y-Axis' id='Y-Value3D' class='col-sm text-center'> \
            <option value='disabledY' disable selected value>--- Y-Axis ---</option> \
                    <option value = 'All visitors'>All Visitors</option> \
                    <option value = 'Graduate Students'>Graduate Students</option> \
                    <option valule = 'Undergraduate Students'>Undergraduate Students</option>\
                    <option value = 'Ethnicity'>Ethnicity</option>\
                    <option value = 'Age'>Age</options>\
                    <option value = 'Gender'>Gender</option>\
                    <option value = 'Benefit Chapter'>Benefit Chapter</option>\
           \        <option value='Months'>Months</option> \
           \        <option value='Days in Month'>Days in Month</option>\
           \        <option value='Days in week'>Days in week</option>\
           \        <option value='Single Day'>Single Day</option>\
           \        <option value='Year'>Year</option> \
                </select> \
           </div> \
           \ <div class='col-4 auto'>\
           <select name='Z-Axis' id='Z-Value3D' class='col-sm text-center'> \
            <option value='disabledZ' disable selected value>--- Z-Axis ---</option> \
                    <option value = 'All visitors'>All Visitors</option> \
                    <option value = 'Graduate Students'>Graduate Students</option> \
                    <option valule = 'Undergraduate Students'>Undergraduate Students</option>\
                    <option value = 'Ethnicity'>Ethnicity</option>\
                    <option value = 'Age'>Age</options>\
                    <option value = 'Gender'>Gender</option>\
                    <option value = 'Benefit Chapter'>Benefit Chapter</option>\
           \        <option value = 'Months'>Months</option> \
           \        <option value='Days in Month'>Days in Month</option>\
           \        <option value='Days in week'>Days in week</option>\
           \        <option value='Single Day'>Single Day</option>\
           \        <option value='Year'>Year</option> \
            \    </select> \
           </div> \
        </div>\
        <div class='row form-group justify-content-center'> \
          <button onClick='DropDownSelect('GraphType');'>Get 3D Graph</button>\
        </div>";
        $('#GraphContainer').append(data); // Insert it into the graph container in "VisualizationsPage.html"

    }

    // Add HTML code for pie chart
    function showPieChart() {
        var data = "<div class=\"graphOptions container border w-50 bg-dark\" id=\"Graph\"> </div> \
        <div class=\"row form-group\"> \
            <div class=\"col-6 auto\"> \
                <select name=\"PieChart\" id=\"PieChart\" class=\"col-sm text-center\"> \
                    <option value=\"disabled\" disable selected value>---Statistic---</option> \
                    \<option value = \"Academic Career\">Academic Career</option> \
                    \<option value = \"Ethnicity\">Ethnicity</options>\
                    \<option value = \"Age\">Age</options>\
                    \<option value = \"Gender\">Gender</options>\
                    \<option value = \"Benefit Chapter\">Benefit Chapter</options> \
                </select> \
            </div> \
        </div>\
        <div class='PlaceHolder' id='PlaceHolderRow'> </div>";
        $('#GraphContainer').append(data); // Insert it into the graph container in "VisualizationsPage.html"

        $("#PieChart").change(function () {
            $('#PlaceHolderRow').empty();
            if ($('#PieChart').val != "disabled") {
              var data="<div class=\"row form-group\" id='PieListTime'> \
                    <div class=\"col-6 auto\"> \
                        <select name=\"PieTime\" id=\"PieTime\" class=\"col-sm text-center\"> \
                            <option value=\"disabled\" disable selected value>Visit Period</option> \
                            \<option value = 'Total'>Total</option>\
                            \<option value = \"Year\">Year</option> \
                            \<option value = \"Month\">Month</options>\
                            \<option value = \"Week\">Week</options>\
                            \<option value = \"Day\">Day</options>\
                            \<option value = \"Hour\">Hour</options> \
                        </select> \
                    </div> \
                </div>\
            <div class='row form-group'> \
                <button onClick='DropDownSelect('GraphType');'>Get Pie Chart</button> \
            </div>";
                $('#PlaceHolderRow').append(data); // Insert it into the graph container in "VisualizationsPage.html"
            }
        });
    }

    function showScatterPlot() {
        var data = "<div class=\"graphOptions container border w-50 bg-dark\" id=\"Graph\"> </div> \
        \<div class=\"row form-group\"> \
           \<div class='col-6 auto'> \
           \    <select name='X-Axis' id='X-Value' class='col-sm text-center'>\
           \        <option value='disabledX' disable selected value>--- X-Axis ---</option>\
           \        <option value='Months'>Months</option> \
           \        <option value='Days in Month'>Days in Month</option>\
           \        <option value='Days in week'>Days in week</option>\
           \        <option value='Single Day'>Single Day</option>\
           \        <option value='Year'>Year</option> \
           \        <option value = 'All visitors'>All Visitors</option> \
                    <option value = 'Graduate Students'>Graduate Students</option> \
                    <option valule = 'Undergraduate Students'>Undergraduate Students</option>\
                    <option value = 'Ethnicity'>Ethnicity</option>\
                    <option value = 'Age'>Age</options>\
                    <option value = 'Gender'>Gender</option>\
                    <option value = 'Benefit Chapter'>Benefit Chapter</option>\
           \    </select>\
           \</div>\
           \ <div class='col-6 auto'>\
           <select name='Y-Axis' id='Y-Value' class='col-sm text-center'> \
            <option value='disabledY' disable selected value>--- Y-Axis ---</option> \
                    <option value = 'All visitors'>All Visitors</option> \
                    <option value = 'Graduate Students'>Graduate Students</option> \
                    <option valule = 'Undergraduate Students'>Undergraduate Students</option>\
                    <option value = 'Ethnicity'>Ethnicity</option>\
                    <option value = 'Age'>Age</options>\
                    <option value = 'Gender'>Gender</option>\
                    <option value = 'Benefit Chapter'>Benefit Chapter</option>\
                    <option value='disabledX' disable selected value>--- X-Axis ---</option>\
           \        <option value='Months'>Months</option> \
           \        <option value='Days in Month'>Days in Month</option>\
           \        <option value='Days in week'>Days in week</option>\
           \        <option value='Single Day'>Single Day</option>\
           \        <option value='Year'>Year</option> \
                </select> \
           </div> \
        </div>\
        <div class='row form-group justify-content-center'> \
          <button onClick='DropDownSelect('GraphType');'>Get Graph</button>\
        </div>";
        $('#GraphContainer').append(data); // Insert it into the graph container in "VisualizationsPage.html"
    }
        // If the user selects 'Bar Graph'
        function showBarGraph() {

        var data = "<div class=\"graphOptions container border w-50 bg-dark\" id=\"Graph\"> </div> \
            <div class=\"row form-group\"> \
                <div class=\"col-6 auto\"> \
                    <select name=\"Bar Graph\" id=\"Bar Graph\" class=\"col-sm text-center\"> \
                        \<option value=\"disabled\" disable selected value>--- Statistic ---</option> \
                        \<option value = \"Academic Career\">Academic Career</option> \
                        \<option value = \"Ethnicity\">Ethnicity</options>\
                        \<option value = \"Age\">Age</options>\
                        \<option value = \"Gender\">Gender</options>\
                        \<option value = \"Benefit Chapter\">Benefit Chapter</options> \
                    </select> \
                </div> \
                \<div class='col-6 auto'>\
                    <select name='Y-Axis' id='Y-Value' class='col-sm text-center'> \
                        <option value='disabledY' disable selected value>--- Y-Axis ---</option> \
                        <option value = 'All students'>All Visitors</option> \
                        <option value = 'G.P.A.'>G.P.A.</option> \
                        <option valule = 'Number of Undergraduate Students'>Undergraduate Students</option>\
                        <option valule = 'Number of Graduate Students'>Graduate Students</option> \
                        <option value='Number of Visits'>Number of Visits</option>\
                    </select> \
                </div> \
           </div>\
           <div class='row form-group justify-content-center'> \
                <button onClick='DropDownSelect('GraphType');'>Get Bar Graph</button> \
            </div>";
        $('#GraphContainer').append(data); // Insert it into the graph container in "VisualizationsPage.html"

        }

        // Function for showing individual statistic (e.g. average G.P.A, average age)
        function showIndStat()
        {
             var data = "<div class=\"graphOptions container border w-50 bg-dark\" id=\"Graph\"> </div> \
        \<div class=\"row form-group\"> \
           \<div class='col-4 auto'> \
           \    <select name='Statistic' id='Statistic' class='col-sm text-center'>\
           \        <option value='disabledX' disable selected value>--- Statistic ---</option>\
           \        <option value = 'Average # Daily visitors'>All Visitors</option> \
                    <option value = 'Average # Graduate Students'>Graduate Students</option> \
                    <option valule='Average # Undergraduate Students'>Undergraduate Students</option>\
                    <option value = 'Average G.P.A'>Ethnicity</option>\
           \    </select>\
           \</div>\
        </div>\
        <div class='row form-group justify-content-center'> \
          <button onClick='DropDownSelect('GraphType');'>Get Individual Statistic</button>\
        </div>";
        $('#GraphContainer').append(data); // Insert it into the graph container in "VisualizationsPage.
        }




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

            if(email != confirmEmail) {
                emailMatch = false;
                emailChangeMatch = false;
                emailSubmitToggle();
                checkIfEverythingIsValid();
                submitToggle();
                $('#divCheckEmailMatch').html(("Email does not match.").fontcolor("red"));
            }
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
            if (password != confirmPassword) {
                passMatch = false;
                passwordSubmitToggle();
                $("#divCheckPasswordMatch").html(("Passwords do not match.").fontcolor("red"));
            }
            else {
                if((password.length < 5 || password.length > 12) || !(containsLowerCase(password) && containsUpperCase(password))
                    || !(containsSymbol(password) || containsNumber(password))) {
                   $("#divCheckPasswordMatch").html(("Password must be 5-12 characters long," +
                       "contain at least one symbol or number, one uppercase letter, and one lowercase letter").fontcolor('red'));
                   passMatch = false;
                   passwordSubmitToggle();
                }
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
            else {
                if((password.length < 5 || password.length > 12) || !(containsLowerCase(password) && containsUpperCase(password))
                    || !(containsSymbol(password) || containsNumber(password))) {
                   $("#divCheckPasswordMatch").html(("Password must be 5-12 characters long," +
                       "contain at least one symbol or number, one uppercase letter, and one lowercase letter").fontcolor('red'));
                   passMatch = false;
                   checkIfEverythingIsValid();
                   submitToggle();
                }
                else {
                     $("#divCheckPasswordMatch").html(("Password is valid.").fontcolor('green'));
                    passMatch = true;
                    checkIfEverythingIsValid();
                    submitToggle();

                }
            }
        }

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

        // This is for changing the password. We only want to toggle "submit" when user changes
        // their password
        /*function newPassSubmitToggle(){
            document.getElementById('newPassSubmit').disabled = !passMatch;
        }*/

        function containsSymbol(str){
            regExp = new RegExp("[-!$%^&*()_+|~=`{}\\[\\]:\";'<>?,.\\/]")
            return regExp.test(str);
        }

        function containsNumber(str){
            const regExp = new RegExp("[0-9]+");
            return regExp.test(str);
        }

        function containsUpperCase(str){
            const regExp = new RegExp("[A-Z]");
            return regExp.test(str);
        }

        function containsLowerCase(str){
            const regExp = new RegExp('[a-z]');
            return regExp.test(str);
        }

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





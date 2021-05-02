// Disable custom scaling options by default
defaultOff('CustomizeBarGraph-autoscale','max_count', 'increment_by');
defaultOff('HistogramDetails-autoscale', 'hist_max', 'hist_increment');
defaultOff('CustomizeLineGraph-autoscale', 'line_max', 'line_increment');
defaultOff('CustomizeScatterPlot-autoscale', 'scatter_max', 'scatter_increment');

// This function ensures that the proper fields are disabled when the user first enters the
// corresponding page on the Reports Wizard
function defaultOff(groupName, max, inc) {
   var max_ct = document.getElementById(max);
   var inc_by = document.getElementById(inc);

   var title_input = document.getElementById('title');
   var report_type_input = document.getElementById('id_BarGraphAxes-report_type')
   var category = document.getElementById('id_BarGraphAxes-category');
   var gpa_to_compare = document.getElementById('id_BarGraphAxes-gpa_to_compare');

   var report_type_input_scatter = document.getElementById('id_ScatterPlotAxes-report_type')
   var category_scatter = document.getElementById('id_ScatterPlotAxes-category');
   var gpa_to_compare_scatter = document.getElementById('id_ScatterPlotAxes-gpa_to_compare');

   var use_cust_name_0 = document.getElementById('use_cust_name_0');
   var use_cust_name_1 = document.getElementById('use_cust_name_1');
   var cust_name = document.getElementById('cust_name');
   var checked_vals = [];

   // Disable the custom name form until user selects "use custom name" on the wizard form
   if (checked_vals == '' && use_cust_name_0 != null && use_cust_name_1 != null && cust_name != null) {

       use_cust_name_0.disabled = true;
       use_cust_name_1.disabled = true;
       cust_name.disabled = true;

   }

   // The default option for bar graphs is to blank out the GPA report selections until the user enables it
    // via the radio buttons
   if(report_type_input != null)
   {
       category.disabled = true;
       gpa_to_compare.disabled = true;
   }

   // Same as above, except with the scatter plot
   if(report_type_input_scatter != null)
   {
       category_scatter.disabled = true;
       gpa_to_compare_scatter.disabled = true;
   }

   // If the user does not select to use a custom title, disable the text entry for it
   if (title_input != null)
       title_input.disabled = true;

   // Disable "max count" and "increment by" text entry boxes if the user wants to autoscale
   if($('input[name='+ groupName + ']:checked').val() == null ||
   $('input[name=' + groupName + ']:checked').val() == 'Yes') {
       if(max_ct != null || inc_by != null) {
           max_ct.disabled = true;
           inc_by.disabled = true;
       }
    }
   // Otherwise, enable the text entry boxes
   else {
       if(max_ct != null || inc_by != null) {
           max_ct.disabled = false;
           max_ct.disabled = false;
       }
   }
}

// If the user selects "Yes" for a custom report title, enable
// the text entry box for it
$('input[name=SelectReportType-custom_title]').change(function(){
    var title_input = document.getElementById('title');

    if(this.value == 'Yes'){
        title_input.disabled = false;
    }
    else {
        title_input.disabled = true;
    }
});

// For Bar Graphs, this enables/disables certain boxes depending on whether the user wants a report
// the counts visits or a gpa comparison against demographics
$('input[name=BarGraphAxes-report_type]').change(function(){
    var selection = document.getElementById('id_BarGraphAxes-selection')
    var category = document.getElementById('id_BarGraphAxes-category')
    var gpa_to_compare = document.getElementById('id_BarGraphAxes-gpa_to_compare')

    // If the user wants a report that counts visits over time, disable the
    // GPA vs. demographics options and enable the axes dropdown for the visit count reports
    if(this.value == 'Count visits over time'){
        selection.disabled = false;
        category.disabled = true;
        gpa_to_compare.disabled = true;
    }
    // If the user wants a report that compares GPA against demographics, disable the axes dropdown
    // for the visit count reports and enable the GPA vs. demographics axes dropdowns
    else {
        selection.disabled = true;
        category.disabled = false;
        gpa_to_compare.disabled = false;
    }
})

// For Line/Scatter plots, this enables/disables certain boxes depending on whether the user wants a report
// the counts visits or a gpa comparison against demographics
$('input[name=ScatterPlotAxes-report_type]').change(function(){
    var selection = document.getElementById('id_ScatterPlotAxes-selection')
    var category = document.getElementById('id_ScatterPlotAxes-category')
    var gpa_to_compare = document.getElementById('id_ScatterPlotAxes-gpa_to_compare')

    // If the user wants a report that counts visits over time, disable the
    // GPA vs. demographics options and enable the axes dropdown for the visit count reports
    if(this.value == 'Count visits over time'){
        selection.disabled = false;
        category.disabled = true;
        gpa_to_compare.disabled = true;
    }
    // If the user wants a report that compares GPA against demographics, disable the axes dropdown
    // for the visit count reports and enable the GPA vs. demographics axes dropdowns
    else {
        selection.disabled = true;
        category.disabled = false;
        gpa_to_compare.disabled = false;
    }
})

// For Bar Graphs, this enables/disables "max count" and "increment by" text entry boxes
// depending on whether the user wants to autoscale or use custom axes
$('input[name=CustomizeBarGraph-autoscale]').change(function (){
    var max_ct = document.getElementById('max_count');
    var inc_by = document.getElementById('increment_by');
    // If autoscale is set to "yes", disable "max count" and "increment by" text entry boxes
    if(this.value == 'Yes'){
        max_ct.disabled = true;
        inc_by.disabled = true;
    }
    // If autoscale is set to "no", enable "max count" and "increment by" text entry boxes
    else {
        max_ct.disabled = false;
        inc_by.disabled = false;
    }
});

// For Histograms, this enables/disables "max count" and "increment by" text entry boxes
// depending on whether the user wants to autoscale or use custom axes
$('input[name=HistogramDetails-autoscale]').change(function (){
    var max_ct = document.getElementById('hist_max');
    var inc_by = document.getElementById('hist_increment');
    // If autoscale is set to "yes", disable "max count" and "increment by" text entry boxes
    if(this.value == 'Yes'){
        max_ct.disabled = true;
        inc_by.disabled = true;
    }
    // If autoscale is set to "no", enable "max count" and "increment by" text entry boxes
    else {
        max_ct.disabled = false;
        inc_by.disabled = false;
    }
});

// For Line/Scatter plots, this enables/disables "max count" and "increment by" text entry boxes
// depending on whether the user wants to autoscale or use custom axes
$('input[name=CustomizeScatterPlot-autoscale]').change(function (){
    var max_ct = document.getElementById('scatter_max');
    var inc_by = document.getElementById('scatter_increment');
    // If autoscale is set to "yes", disable "max count" and "increment by" text entry boxes
    if(this.value == 'Yes'){
        max_ct.disabled = true;
        inc_by.disabled = true;
    }
    // If autoscale is set to "no", enable "max count" and "increment by" text entry boxes
    else {
        max_ct.disabled = false;
        inc_by.disabled = false;
    }
});

// This function enables/disables the custom event name text entry box
// depending on whether the use wants to use a custom event name
$('#id_AttendanceDataForm-attendance_data').change(function() {
    var use_cust_name_0 = document.getElementById('use_cust_name_0');
    var use_cust_name_1 = document.getElementById('use_cust_name_1');
    var cust_name = document.getElementById('cust_name');
    var checked_vals = [];
    // Referenced on https://stackoverflow.com/questions/35305970/javascript-how-can-i-get-all-value-of-selected-checked-checkboxes-push-to-an-a
    // Last visited 3/22/2021
    $('input:checkbox[name=AttendanceDataForm-attendance_data]:checked').each(function() {
        checked_vals.push($(this).val());
    });
    // -- End of reference --------------------------------------
    // If the user checks "Event" in the location checkboxes for tracking visit data
    if(checked_vals.includes('Veteran Services Event')){
        use_cust_name_0.disabled = false;
        use_cust_name_1.disabled = false;
        // If the user wants to use a custom event name, enable its text entry box
        if(use_cust_name_0.checked){
            cust_name.disabled = false;
        }
        // Otherwise, disable the text entry box
        else{
            cust_name.disabled = true;
        }
    }
    // If the user does not include "Event" in the list of locations to track visits
    // disable all buttons related to custom events as they are not applicable
    else{
        use_cust_name_0.disabled = true;
        use_cust_name_1.disabled = true;
        cust_name.disabled = true;
    }

});

// When the user changes their entry in the checkbox for using a custom event name,
// this function will enable/disable the text entry for the custom event name
$('input[name=AttendanceDataForm-use_custom_event_name]').change(function(){
        var use_cust_name_0 = document.getElementById('use_cust_name_0');
        var cust_name = document.getElementById('cust_name');
        // If the user wants to use a custom event name, enable its text entry box
        if(use_cust_name_0.checked){
            cust_name.disabled = false;
        }
        // Otherwise, disable the text entry box
        else{
            cust_name.disabled = true;
        }

});

// Handles the special case when the user checks "Select All" for the list of locations
// to track visits
$('#id_AttendanceDataForm-select_all').click(function() {
    $('input:checkbox').not(this).prop('checked', this.checked);

    var use_cust_name_0 = document.getElementById('use_cust_name_0');
    var use_cust_name_1 = document.getElementById('use_cust_name_1');
    var cust_name = document.getElementById('cust_name');
    var checked_vals = [];
    // When the user checks "Select All" it automatically checks all locations
    // Referenced on https://stackoverflow.com/questions/35305970/javascript-how-can-i-get-all-value-of-selected-checked-checkboxes-push-to-an-a
    // Last visited 3/22/2021
    $('input:checkbox[name=AttendanceDataForm-attendance_data]:checked').each(function() {
        checked_vals.push($(this).val());
    });
    // -- End of reference --------------------------------------
    // When the user clicks "Select All," the "Event" box is automatically checked
    // Check if the user wants to use a custom event name
    if(checked_vals.includes('Veteran Services Event')){
        use_cust_name_0.disabled = false;
        use_cust_name_1.disabled = false;
        // If the user wants to use a custom event name, enable its corresponding text entry box
        if(use_cust_name_0.checked){
            cust_name.disabled = false;
        }
        // Otherwise, disable the text entry box
        else{
            cust_name.disabled = true;
        }
    }
    // Disable all buttons related to custom events if "Event" is not checked (i.e. it is not applicable)
    else{
        use_cust_name_0.disabled = true;
        use_cust_name_1.disabled = true;
        cust_name.disabled = true;
    }


});
// If the user unchecks any of the locations, automatically uncheck "Select All" if not already unchecked
// Referenced on https://stackoverflow.com/questions/17785010/jquery-uncheck-other-checkbox-on-one-checked
// Last visited on 2/17/2021
$('.Locations').click(function() {
    $('#id_AttendanceDataForm-select_all').prop('checked', false);

});
// --------- End of reference -------------------------------------------------------
defaultOff('CustomizeBarGraph-autoscale','max_count', 'increment_by');
defaultOff('HistogramDetails-autoscale', 'hist_max', 'hist_increment');
defaultOff('CustomizeLineGraph-autoscale', 'line_max', 'line_increment');
defaultOff('CustomizeScatterPlot-autoscale', 'scatter_max', 'scatter_increment');

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

   if (checked_vals == '' && use_cust_name_0 != null && use_cust_name_1 != null && cust_name != null) {

       use_cust_name_0.disabled = true;
       use_cust_name_1.disabled = true;
       cust_name.disabled = true;

   }

   if(report_type_input != null)
   {
       category.disabled = true;
       gpa_to_compare.disabled = true;
   }

   if(report_type_input_scatter != null)
   {
       category_scatter.disabled = true;
       gpa_to_compare_scatter.disabled = true;
   }

   if (title_input != null)
       title_input.disabled = true;

   if($('input[name='+ groupName + ']:checked').val() == null ||
   $('input[name=' + groupName + ']:checked').val() == 'Yes') {
       if(max_ct != null || inc_by != null) {
           max_ct.disabled = true;
           inc_by.disabled = true;
       }
    }
   else {
       if(max_ct != null || inc_by != null) {
           max_ct.disabled = false;
           max_ct.disabled = false;
       }
   }
}

$('input[name=SelectReportType-custom_title]').change(function(){
    var title_input = document.getElementById('title');

    if(this.value == 'Yes'){
        title_input.disabled = false;
    }
    else {
        title_input.disabled = true;
    }
});

$('input[name=BarGraphAxes-report_type]').change(function(){
    var selection = document.getElementById('id_BarGraphAxes-selection')
    var category = document.getElementById('id_BarGraphAxes-category')
    var gpa_to_compare = document.getElementById('id_BarGraphAxes-gpa_to_compare')

    if(this.value == 'Count visits over time'){
        selection.disabled = false;
        category.disabled = true;
        gpa_to_compare.disabled = true;
    }
    else {
        selection.disabled = true;
        category.disabled = false;
        gpa_to_compare.disabled = false;
    }
})

$('input[name=ScatterPlotAxes-report_type]').change(function(){
    var selection = document.getElementById('id_ScatterPlotAxes-selection')
    var category = document.getElementById('id_ScatterPlotAxes-category')
    var gpa_to_compare = document.getElementById('id_ScatterPlotAxes-gpa_to_compare')

    if(this.value == 'Count visits over time'){
        selection.disabled = false;
        category.disabled = true;
        gpa_to_compare.disabled = true;
    }
    else {
        selection.disabled = true;
        category.disabled = false;
        gpa_to_compare.disabled = false;
    }
})

$('input[name=CustomizeBarGraph-autoscale]').change(function (){
    var max_ct = document.getElementById('max_count');
    var inc_by = document.getElementById('increment_by');
    if(this.value == 'Yes'){
        max_ct.disabled = true;
        inc_by.disabled = true;
    }
    else {
        max_ct.disabled = false;
        inc_by.disabled = false;
    }
});

$('input[name=HistogramDetails-autoscale]').change(function (){
    var max_ct = document.getElementById('hist_max');
    var inc_by = document.getElementById('hist_increment');

    if(this.value == 'Yes'){
        max_ct.disabled = true;
        inc_by.disabled = true;
    }
    else {
        max_ct.disabled = false;
        inc_by.disabled = false;
    }
});



$('input[name=CustomizeLineGraph-autoscale]').change(function (){
    var max_ct = document.getElementById('line_max');
    var inc_by = document.getElementById('line_increment');

    if(this.value == 'Yes'){
        max_ct.disabled = true;
        inc_by.disabled = true;
    }
    else {
        max_ct.disabled = false;
        inc_by.disabled = false;
    }
});

$('#id_AttendanceDataForm-attendance_data').change(function() {
    var use_cust_name_0 = document.getElementById('use_cust_name_0');
    var use_cust_name_1 = document.getElementById('use_cust_name_1');
    var cust_name = document.getElementById('cust_name');
    var checked_vals = [];
    $('input:checkbox[name=AttendanceDataForm-attendance_data]:checked').each(function() {
        checked_vals.push($(this).val());
    });
    if(checked_vals.includes('Event')){
        use_cust_name_0.disabled = false;
        use_cust_name_1.disabled = false;

        if(use_cust_name_0.checked){
            cust_name.disabled = false;
        }
        else if (use_cust_name_0.checked){
            cust_name.disabled = true;
        }
        else{
            cust_name.disabled = true;
        }
    }
    else{
        use_cust_name_0.disabled = true;
        use_cust_name_1.disabled = true;
        cust_name.disabled = true;
    }

});

$('input[name=AttendanceDataForm-use_custom_event_name]').change(function(){
        var use_cust_name_0 = document.getElementById('use_cust_name_0');
        var cust_name = document.getElementById('cust_name');

        if(use_cust_name_0.checked){
            cust_name.disabled = false;
        }
        else if (use_cust_name_0.checked){
            cust_name.disabled = true;
        }
        else{
            cust_name.disabled = true;
        }

});

$('#id_AttendanceDataForm-select_all').click(function() {
    $('input:checkbox').not(this).prop('checked', this.checked);

    var use_cust_name_0 = document.getElementById('use_cust_name_0');
    var use_cust_name_1 = document.getElementById('use_cust_name_1');
    var cust_name = document.getElementById('cust_name');
    var checked_vals = [];
    $('input:checkbox[name=AttendanceDataForm-attendance_data]:checked').each(function() {
        checked_vals.push($(this).val());
    });
    if(checked_vals.includes('Event')){
        use_cust_name_0.disabled = false;
        use_cust_name_1.disabled = false;
        if(use_cust_name_0.checked){
            cust_name.disabled = false;
        }
        else if (use_cust_name_0.checked){
            cust_name.disabled = true;
        }
        else{
            cust_name.disabled = true;
        }
    }
    else{
        use_cust_name_0.disabled = true;
        use_cust_name_1.disabled = true;
        cust_name.disabled = true;
    }


});

$('.Locations').click(function() {
    $('#id_AttendanceDataForm-select_all').prop('checked', false);
});
defaultOff('CustomizeBarGraph-autoscale','max_count', 'increment_by');
defaultOff('HistogramDetails-autoscale', 'hist_max', 'hist_increment');
defaultOff('CustomizeLineGraph-autoscale', 'line_max', 'line_increment');
defaultOff('CustomizeScatterPlot-autoscale', 'scatter_max', 'scatter_increment');

function defaultOff(groupName, max, inc) {
   var max_ct = document.getElementById(max);
   var inc_by = document.getElementById(inc);

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

$('input[name=CustomizeScatterPlot-autoscale]').change(function (){
    var max_ct = document.getElementById('scatter_max');
    var inc_by = document.getElementById('scatter_increment');

    if(this.value == 'Yes'){
        max_ct.disabled = true;
        inc_by.disabled = true;
    }
    else {
        max_ct.disabled = false;
        inc_by.disabled = false;
    }
});

$('#id_AttendanceDataForm-select_all').click(function() {
    $('input:checkbox').not(this).prop('checked', this.checked);
});

$('.Locations').click(function() {
    $('#id_AttendanceDataForm-select_all').prop('checked', false);
});
var rows = ['zero','one','two','three','four','five','six','seven','eight','nine'];
i = 0;
j = 1;
let AddControl = document.querySelector('#AddControl');
let p = AddControl.querySelector('#' + rows[i]);

p.innerHTML = "<div class='row mb-1 justify-content-center' id='" + 'iii' + rows[i] +"'>"+j+"</div>" + "<div class='row mb-1' id='" + 'i' + rows[i] +"'>"+ 
                "<div class='col-md-3'>"+ 
                    "<input type='text' style='width:100%;' placeholder='NSHE ID' name='" + 'NSHEID' + i + "'></input>"+
                "</div>" +
                "<div class='col-md-3'>"+
                    "<input type='text' style='width:100%;' placeholder='First Name' name='" + 'fname' + i + "'></input>"+
                "</div>"+
                "<div class='col-md-3'>"+
                    "<input type='text' style='width:100%;' placeholder='Last Name' name='" + 'lname' + i + "'></input>"+
                "</div>"+
                "<div class='col-md-3'>"+
                    "<select name='" + 'location' + i + "' style='width:100%; height:100%'>" + "<option value='' selected disabled>Location</option>" + "<option value='VMC'>VMC</option>" + "<option value='Fitzgerald'>Fitzgerald</option>" + "<option value='Event'>Event</option>" + "</select>" +
                    // "<input type='text' style='width:100%;' placeholder='Location'></input>"+
                "</div>"+
            "</div>"+ //here
            "<div class='row' id='" + 'ii' + rows[i] +"'>"+
                "<div class='col-md-6'>"+ 
                    "<input type='datetime-local' style='width:100%;' name='" + 'checkintime' + i + "'></input>"+
                "</div>" +
                "<div class='col-md-6'>"+
                    "<input type='datetime-local' style='width:100%;' name='" + 'checkouttime' + i + "'></input>"+
                "</div>"
            "</div>";
// "</div>";
// "<div>" + i+ "</div>"+
// var i = 0;
function addRow() {
    if(i<9) {
        // alert(i);
        i++;
        j++;
        let p = AddControl.querySelector('#' + rows[i]);

        p.innerHTML = "<div class='row mb-1 justify-content-center' id='" + 'iii' + rows[i] +"'>"+j+"</div>" + "<div class='row mb-1' id='" + 'i' + rows[i] +"'>"+
        "<div class='col-md-3'>"+
            "<input type='text' style='width:100%;' placeholder='NSHE ID' name='" + 'NSHEID' + i + "'></input>"+
        "</div>" +
        "<div class='col-md-3'>"+
            "<input type='text' style='width:100%;' placeholder='First Name' name='" + 'fname' + i + "'></input>"+
        "</div>"+
        "<div class='col-md-3'>"+
            "<input type='text' style='width:100%;' placeholder='Last Name' name='" + 'lname' + i + "'></input>"+
        "</div>"+
        "<div class='col-md-3'>"+
            "<select name='" + 'location' + i + "' style='width:100%; height:100%'>" + "<option value='' selected disabled>Location</option>" + "<option value='VMC'>VMC</option>" + "<option value='Fitzgerald'>Fitzgerald</option>" + "<option value='Event'>Event</option>" + "</select>" +
            // "<input type='text' style='width:100%;' placeholder='Location'></input>"+
        "</div>"+
    "</div>"+
    "<div class='row' id='" + 'ii' + rows[i] +"'>"+
        "<div class='col-md-6'>"+ 
            "<input type='datetime-local' style='width:100%;' name='" + 'checkintime' + i + "'></input>"+
        "</div>" +
        "<div class='col-md-6'>"+
            "<input type='datetime-local' style='width:100%;' name='" + 'checkouttime' + i + "'></input>"+
        "</div>"
    "</div>";
    p.classList.add('manualBorder');

    }
}

function removeRow() {
    if(i>0) {
        let p = AddControl.querySelector('#' + rows[i]);
        p.classList.remove('manualBorder');
        var element = document.getElementById('i' + rows[i]).remove();
        var element = document.getElementById('ii' + rows[i]).remove();
        var element = document.getElementById('iii' + rows[i]).remove();

        j--;
        i--;
    }
    
}

function resetRows() {
    // i = 0;
}

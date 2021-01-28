$(document).ready(function() {
    
    /* Every time the window is scrolled this portion of javascript is run */
    $(window).scroll( function(){
    
        /* Check to see if this portion is visible */
        $('.hiddenPanel').each( function(i){
            
            var bottom_of_object = $(this).position().top + $(this).outerHeight()/2;
            var bottom_of_window = $(window).scrollTop() + $(window).height();
            
            /* If the panel is visible in the window it will fade in */
            if( bottom_of_window > bottom_of_object ){
                
                $(this).animate({'opacity':'1'},500);
                    
            }
        }); 
    });
});
$(document).ready(function(){
    if( $('#toggle-div').attr('name') === 'True'){
        $('.individual').show();
        $(".organization").hide();
    }
    else {
        $('.individual').hide();
        $('.organization').show();
    }
});

$('#user-type').on('change', function(){
    if( $('#user_type-0').is(':checked')){
        $('.individual').show();
        $(".organization").hide();
    }
    if( $('#user_type-1').is(':checked')) {
        $('.individual').hide();
        $('.organization').show();
    }
});
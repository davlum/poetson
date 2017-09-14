$(document).ready(function(){
    if( $('#toggle-div').attr('name') === 'True'){
        $('.individual').show();
        $(".organization").hide();
    }
    else {
        $('.individual').hide();
        $('.organization').show();
    }
    if( $('#user_type-0').is(':checked')){
        $('.individual').show();
        $(".organization").hide();
    }
    if( $('#user_type-1').is(':checked')) {
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

$(document).on("click", ".open-confirm-modal", function () {
     var partId = $(this).data('id');
     var entType = $(this).data('role');
     $(".modal-body #delete-button").attr('href', '/remove_'+ entType + '/' + partId + '/');
});
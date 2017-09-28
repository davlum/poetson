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
    $('#confirm-modal').css('top', $(window).scrollTop()+ ($(window).height()*0.4));
    $(".modal-body #delete-button").attr('href', '/retirar/'+ entType + '/' + partId + '/');
});


$(document).on("click", ".open-progress-modal", function () {
    $('#progress-modal').css('top', $(window).scrollTop()+ ($(window).height()*0.4));
});


$(function() {
    $('.varios-modal').each(function(){
        var vario_id = String($(this).find('option').val());
        $(this).find('a').each(function(){
           $(this).attr('data-id', vario_id);
        });
    });

    $('.li-link').on('click', function() {
       console.log('hey');
    });
});


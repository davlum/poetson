$(function(){
    var csrf_token = $('meta[name=csrf-token]').attr('content');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token)
            }
        }
    });

   $('.ajax-select').on('change', function(e){
        e.preventDefault();
        var request = $.ajax({
            type: "POST",
            url: "/estado/"+ $(this).data('role')+"/"+$(this).val()+"/"+$(this).data('id') +"/",
            success: function() {
                console.log('change state success');
            },
            error: function () {
                console.log('change state failed');
            }
        })
            .done( function(request){
        })
    })
});

$(function(){
    var csrf_token = $('meta[name=csrf-token]').attr('content');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token)
            }
        }
    });

   $('.ajax-permission').on('change', function(e){
        e.preventDefault();
        var request = $.ajax({
            type: "POST",
            url: "/permiso/"+$(this).data('id') +"/",
            data: JSON.stringify({
                permiso: $(this).val()
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: "json",
            success: function() {
                console.log('change permission success');
            },
            error: function () {
                console.log('change permission failed');
            }
        })
            .done( function(request){
        })
    });
   $('.ajax-banned').on('change', function(e){
        e.preventDefault();
        var request = $.ajax({
            type: "POST",
            url: "/prohibido/"+$(this).data('id') +"/",
            data: JSON.stringify({
                prohibido: $(this).val()
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: "json",
            success: function() {
                console.log('change prohibido sucess');
            },
            error: function() {
                console.log('change prohibido failed');
            }
        })
            .done( function(request){
        })
    })
});
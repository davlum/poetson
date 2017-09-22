$(function(){
    var csrf_token = "{{ csrf_token() }}";

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token)
            }
        }
    });

   $SCRIPT_ROOT = "{{ request.script_root|tojson|safe }}";

   $('.ajax-select').on('change', function(e){
        e.preventDefault();
        var request = $.ajax({
            type: "POST",
            url: "/estado/"+ $(this).data('role')+"/"+$(this).data('id') +"/",
            data: JSON.stringify({
                estado: String($(this).val())
            }),
            contentType: 'application/json; charset=utf-8',
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

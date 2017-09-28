$(document).ready(function() {

    function flash(message,category){
        // Function to create flask like flash messages
       var icon;
       if (category === 'danger'){
          icon='icon-exclamation-sign';
          category='danger';
          }
       else if (category === 'success')
          icon='icon-ok-sign';
       else
          icon='icon-info-sign';
       $('<div class="alert alert-'+category+'"><i class="'+icon+'"></i>&nbsp;<a class="close" data-dismiss="alert">×</a>'+ message +'</div>').prependTo($('#flash-message-div:first'));
    }

    if (sessionStorage.getItem("msg")){
        // Flash messages from after page reload ajax requests
        flash(sessionStorage.msg, sessionStorage.success);
        sessionStorage.clear();
    }

    if ( sessionStorage.reloadAfterPageLoad ) {
        // This only happens if somebody modifies the html itself
        alert('¡Algo salió mal!');
        sessionStorage.reloadAfterPageLoad = false;
    }

	var csrf_token = $('meta[name=csrf-token]').attr('content');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token)
            }
        }
    });

	$('#pista-form-submit').on('click', function(event) {

        event.preventDefault();

		var obra_id = $('#obra-id').val();

		if (obra_id !== '') {
			obra_id = parseInt(obra_id) || 0;
			if (obra_id < 1) {
				sessionStorage.reloadAfterPageLoad = true;
				location.reload()
			}
			obra_id = '/' + obra_id.toString() + '/';
		}

		var formData = new FormData($('#add-pista-form')[0]);

		var request = $.ajax({
			xhr : function() {
				var xhr = new window.XMLHttpRequest();

				xhr.upload.addEventListener('progress', function(e) {

					if (e.lengthComputable) {

						console.log('Bytes Loaded: ' + e.loaded);
						console.log('Total Size: ' + e.total);
						console.log('Percentage Uploaded: ' + (e.loaded / e.total));

						var percent = Math.round((e.loaded / e.total) * 100);

						$('#progressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');

					}

				});

				return xhr;
			},
			type : 'POST',
			url : '/poner/pista' + obra_id,
			data : formData,
			processData : false,
			contentType : false,
			failure: function(data) {
			    sessionStorage.msg = data.msg;
				sessionStorage.success = data.success;
				window.location = "/perfil#tab_pista";
			},
			success : function(data) {
			    sessionStorage.msg = data.msg;
			    sessionStorage.success = data.success;
				window.location = "/perfil#tab_pista";
			}
		})
            .done( function(request){
        });
	});

});

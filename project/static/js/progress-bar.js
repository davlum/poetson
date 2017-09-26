
function uploadFile() {
  $.ajax({
          xhr: function() {
            var xhr = new window.XMLHttpRequest();

            xhr.upload.addEventListener("progress", function(evt) {
              if (evt.lengthComputable) {
                var percentComplete = evt.loaded / evt.total;
                percentComplete = parseInt(percentComplete * 100);
                console.log(percentComplete);
                $("#progressBar").val(percentComplete);

              }
            }, false);

            return xhr;
          }
    });
}

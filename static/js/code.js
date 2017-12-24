$(document).ready(function() {
  "use strict";

  if("undefined" == typeof jQuery) {
    window.onload = function() {
      init_app();
    };
  }
  else {
    init_app();
  }

  function init_app() {
    var result;

    $('form .btn-danger').click(function() {
      result = confirm("Are you sure you want to delete this code snippet?");
      if (result) {
        $.ajax({
          url: window.location.href ,
          type: 'DELETE',
          beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFTOKEN', $('form [name="csrfmiddlewaretoken"]').val());
          },
          success: function(result) {
            window.location.replace(result.redirect);
          }
        });
      }
      return false;
    });

    // Replace default CKEditor.
    try {
      if (document.getElementById('cke_id_text')) {
        CKEDITOR.instances['id_text'].destroy();
      }
      CKEDITOR.replace('id_text');
    }
    catch (e) {
      console.log(e);
    }
    CKEDITOR.config.extraPlugins = 'codesnippet,autogrow';
    CKEDITOR.config.codeSnippet_theme = 'monokai_sublime';
    CKEDITOR.config.autoGrow_onStartup = true;
    CKEDITOR.config.toolbar = [['CodeSnippet'], ['Source'], ['Undo', 'Redo'], ['NumberedList', 'BulletedList']];
  }

});

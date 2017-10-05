$(document).ready(function() {
  "use strict";

  // Set up and initialize editable.
  $.fn.editable.defaults.mode = 'inline';

  var $content = $('#content');

  function set_active_link(link) {
    var a_selector = 'a[href="' + link + '"]';
    var $link = $(a_selector);
    $('li.active > a').parent().removeClass('active');
    $link.parent('li').addClass('active');
  }

  function page_init() {
    // Initialize datetimepicker.
    $content.find('.datetimepicker').datetimepicker({
      format: 'YYYY-MM-DD HH:mm',
    });
    $content.find('.datetimepicker-date').datetimepicker({
      format: 'YYYY-MM-DD',
    });

    // Initialize jscolor.
    jscolor.installByClassName('jscolor');
  }

  // Process ajax links.
  $(document).on('click', 'a.ajax-link', function(event) {
    event.preventDefault();
    if (!$(this).parent('li').hasClass("active")) {
      var $link = $(this);
      $.ajax({
        url: $link.attr("href") != '/' ? '/ajax' + $link.attr("href") : '/ajax',
        dataType: 'html',
      })
      .done(function(data) {
        $('#content').html(data);
        set_active_link($link.attr("href"));
        page_init();
        $(".modal-backdrop.in").remove();
        history.pushState({content: data}, null, $link.attr("href"));
      })
      .fail(function() {
        window.location.replace($link.attr("href"));
      });
    }
  });

  // Back button.
  $(window).on('popstate', function(event) {
    if (event.originalEvent.state.content !== null) {
      $('#content').html(event.originalEvent.state.content);
      set_active_link(window.location.pathname);
    }
  });

  // Show from if there are errors.
  $('.modal.error').modal('show');

  // Clean modal form on close.
  $(document).on('hidden.bs.modal', '.modal', function () {
    var $modal = $(this);

    // Clean inputs (but not security token) and textareas.
    $modal.find("input:not([name='csrfmiddlewaretoken']), textarea").val('');
    // Clean selects and select2.
    $modal.find('select').prop('selectedIndex', 0).trigger('change.select2');

    // Clean ckeditors.
    if (typeof CKEDITOR !== 'undefined') {
      for (var i in CKEDITOR.instances) {
        // Check if the textarea still exists.
        if ($modal.find($(CKEDITOR.instances[i].element['$'])).length) {
          CKEDITOR.instances[i].setData('');
        }
      }
    }
  });

  // Show modal edit form.
  $(document).on('click', 'a.edit', function() {
    var $card = $(this).closest('.card-container');
    var $modal = $card.closest('#content').find('.modal');
    var $field;
    var card = $card.data('json');
    var key;

    // Show modal, remove errors and set hidden id field.
    $modal.modal();
    $modal.find('.alert').remove();
    $modal.find('#id_id').val(card.pk);

    // Update all fields.
    for (key in card.fields) {
      $field = $modal.find('#id_' + key);
      $field.val(card.fields[key]);

      if ($field.is('textarea.ckeditor')) {
        // We need update ckeditor too.
        if ('id_' + key in CKEDITOR.instances) {
            CKEDITOR.instances['id_' + key].setData(card.fields[key]);
        }
      }
      else if ($field.is('select')) {
        // We need update select2 too.
        $field.trigger('change.select2');
      }
    }

    return false;
  });

  // Flashcards.
  $(document).on('click', '.flip', function() {
    $(this).find('.card').toggleClass('flipped');
  });

  // Initialize datetimepicker and jscolor.
  page_init();

});

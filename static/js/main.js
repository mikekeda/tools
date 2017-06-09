$(document).ready(function() {
  "use strict";

  function set_active_link(link) {
    var a_selector = 'a[href="' + link + '"]';
    var $link = $(a_selector);
    $('li.active > a').parent().removeClass('active');
    $link.parent('li').addClass('active');
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

  // Flashcards.
  $(document).on('click', '.flip', function() {
    $(this).find('.card').toggleClass('flipped');
  });

  // Datetimepicker.
  $('.datetimepicker').datetimepicker({
    format: 'YYYY-MM-DD HH:mm',
    debug: true,
  });

  // Show from if there are errors.
  $('.modal.error').modal('show');

  // Set up and initialize editable.
  $.fn.editable.defaults.mode = 'inline';

});


$( document ).ready(function() {

  function set_active_link (link) {
    var a_selector = 'a[href="' + link + '"]';
    var $link = $(a_selector);
    $('li.active > a').parent().removeClass('active');
    $link.parent('li').addClass('active');
  }

  /* change modal title when slide changes */
  $(document).on('click', '#modal-carousel', function(event) {
    $(".modal-title").html($(this).find(".active img").attr("title"));
  });

  /* when clicking a thumbnail */
  $("#content").on('click', ".thumbnails .thumbnail", function(event) {
    if ($(event.target).is("img")) {
      var $content = $(".carousel-inner");
      var $title = $(".modal-title");

      $content.empty();
      $title.empty();

      var $repoCopy = $(".thumbnails .thumbnail img").clone();

      var active_index = $(this).parent().index();
      var $active = $($repoCopy[active_index]);

      $title.html($active.attr("title"));
      $content.append($repoCopy);
      $repoCopy.each(function(index, el) {
        if (index == active_index) {
          var slide = '<a href ="' + $(this).data('slug') + '" class="item active ajax-link"></a>';
        }
        else {
          var slide = '<a href ="' + $(this).data('slug') + '" class="item ajax-link"></a>';
        }
        $(this).wrap(slide);
      });

      // show the modal
      $("#modal-gallery").modal("show");
      event.preventDefault();
    };
  });

  /* Process ajax links */
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
      })
    };
  });

  /* Back button */
  $(window).on("popstate", function(event) {
    if (event.originalEvent.state.content !== null) {
      $('#content').html(event.originalEvent.state.content);
      set_active_link (window.location.pathname);
    }
  });

});

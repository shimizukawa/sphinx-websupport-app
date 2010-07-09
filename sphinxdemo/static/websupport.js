(function($) {
   var currentNode, commentListEmpty, replyTemplate, commentTemplate, popup;

  function init() {
    replyTemplate = $('#reply_template').html();
    commentTemplate = $('#comment_template').html();
    var popupTemplate = $('#popup_template').html();
    var popup = $(renderTemplate(popupTemplate, opts));
    $('body').append(popup);

    $('a#comment_close').click(function(event) {
      event.preventDefault();
      hide();
    });

    $('form#comment_form').submit(function(event) {
      event.preventDefault();
      addComment($('form#comment_form'));
    });

    $('a.reply').live("click", function(event) {
      openReply($(this).attr('id').substring(2));
      return false;
    });

    $('a.close_reply').live("click", function(event) {
      closeReply($(this).attr('id').substring(2));
      return false;
    });
  };

  /**
   * Show the comments popup window.
   */
  function show(nodeId) {
    currentNode = nodeId.substring(1);

    $('form#comment_form')
      .find('textarea,input')
	.removeAttr('disabled').end()
      .find('input[name="parent"]')
	.val('s' + currentNode);

    // Set the commentPopup's id and display it.
    var clientWidth = document.documentElement.clientWidth;
    var popupWidth = $('div.popup_comment').width();

    $('div#focuser').show();
    $('div.popup_comment')
      .css({
	'top': 100+$(window).scrollTop(),
	'left': clientWidth/2-popupWidth/2,
	'position': 'absolute'
      })
      .show();

    getComments();
  };

  /**
   * Hide the comments popup window.
   */
  function hide() {
    $('div#focuser').hide();
    $('div.popup_comment').hide();
    $('ul#comment_ul').empty();
    $('h3#comment_notification').show();
    $('form#comment_form').each(function() {
      this.reset();
    });
  };

  /**
   * Perform an ajax request to get comments for a node
   * and insert the comments into the comments tree.
   */
  function getComments() {
    $.ajax({
      type: 'GET',
      url: opts.getCommentsURL,
      data: {parent: 's' + currentNode},
      success: function(data, textStatus, request) {
	if (data.comments.length == 0) {
	  $('ul#comment_ul').html('<li>No comments yet.</li>');
	  commentListEmpty = true;
	}
	else {
	  $.each(data.comments, function() {
	    insertComment(this);
	  });
	  commentListEmpty = false;
	}
	$('h3#comment_notification').hide()
      },
      error: function(request, textStatus, error) {
	alert('error');
      },
      dataType: 'json'
    });
  };

  /**
   * Insert an individual comment into the comment tree.
   */
  function insertComment(comment) {
    var div = createCommentDiv(comment);

    if (comment.node != null)
      var list = $('ul#comment_ul');
    else
      var list = $('#cl' + comment.parent);

    list.append($('<li></li>').html(div));

    $.each(comment.children, function() {
      insertComment(this);
    });
  };

  /**
   * Add a comment via ajax and insert the comment into the comment tree.
   */
  function addComment(form) {
    form.find('textarea,input').attr('disabled', 'disabled');

    var parent = form.find('input[name="parent"]').val();
    var text = form.find(' textarea[name="comment"]').val();
    $.ajax({
      type: "POST",
      url: opts.addCommentURL,
      dataType: 'json',
      data: {parent: parent,
	     text: text},
      success: function(data, textStatus, error) {
	form.find('textarea').val('');
	form.find('textarea,input').removeAttr('disabled');
	if (commentListEmpty) {
	  $('ul#comment_ul').empty();
	  commentListEmpty = false;
	}
	insertComment(data.comment);
      },
      error: function(request, textStatus, error) {
	form.find('textarea,input').removeAttr('disabled');
	alert(error);
      }
    });
  };

  /**
   * Open a reply form used to reply to an existing comment.
   */
  function openReply(id) {
    // Swap out the reply link for the hide link
    $('#rl' + id).hide();
    $('#cr' + id).show();

    // Add the reply li to the children ul.
    $('#cl' + id)
      .prepend(renderTemplate(replyTemplate, {id: id}))
      // Setup the submit handler for the reply form.
      .find('#rf' + id)
	.submit(function(event) {
	  event.preventDefault();
	  addComment($('#rf' + id));
	  closeReply(id);
	});
  };

  /**
   * Close the reply form opened with openReply.
   */
  function closeReply(id) {
    $('#rd' + id).remove();
    // Swap out the hide link for the reply link
    $('#cr' + id).hide();
    $('#rl' + id).show();
  };

  /**
   * Create a Div used to display a comment.
   */
  function createCommentDiv(comment) {
    var context = $.extend({}, comment, opts);
    var div = renderTemplate(commentTemplate, context);

    return $(div);
  };

  /**
   * A simple template renderer. Placeholders such as <%id%> are replaced
   * by context['id']. context['id'] is always escaped.
   */
  function renderTemplate(template, context) {
    var esc = $('<span></span>');

    function handle(ph) {
      var cur = context;
      $.each(ph.split('.'), function() {
	cur = cur[this];
      });
      return esc.text(cur || "").html();
    }

    return template.replace(/<%([\w\.]*)%>/g, function(){
      return handle(arguments[1]);
    });
  };

  /**
   * Add a link the user uses to open the comments popup.
   */
  $.fn.comment = function() {
    return this.each(function() {
      $(this).append(
	$('<a href="#" class="sphinx_comment"></a>')
	  .html(opts.commentHTML)
	  .click(function(event) {
	    event.preventDefault();
	    show($(this).parent().attr('id'));
	  }));
    });
  };

  var opts = jQuery.extend({
    addCommentURL: '/add_comment',
    getCommentsURL: '/get_comments',
    commentHTML: '<img src="/static/comment.png" alt="comment" />',
    upArrow: '/static/up.png',
    downArrow: '/static/down.png'
  }, COMMENT_OPTIONS);

  $(document).ready(function() {
    init();
  });

})(jQuery);

$(document).ready(function() {
  $('.spxcmt').comment();

  /** Highlight search words in search results. */
  $("div.context").each(function() {
    var params = $.getQueryParameters();
    var terms = (params.q) ? params.q[0].split(/\s+/) : [];
    var result = $(this);
    $.each(terms, function() {
      result.highlightText(this.toLowerCase(), 'highlighted');
    });
  });
});
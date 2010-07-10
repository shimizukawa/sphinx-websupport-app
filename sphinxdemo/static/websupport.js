(function($) {
   var currentNode, commentListEmpty, replyTemplate, commentTemplate, popup;

  function init() {
    // Preload the replyTemplate and commentTemplate.
    replyTemplate = $('#reply_template').html();
    commentTemplate = $('#comment_template').html();
    // Create our popup div, the same div is recycled each time comments
    // are displayed.
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

    $('.vote').live("click", function() {
      processVote($(this));
      return false;
    });

    $('a.reply').live("click", function() {
      openReply($(this).attr('id').substring(2));
      return false;
    });

    $('a.close_reply').live("click", function() {
      closeReply($(this).attr('id').substring(2));
      return false;
    });
  };

  /**
   * Show the comments popup window.
   */
  function show(nodeId) {
    currentNode = nodeId.substring(1);

    // Reset the main comment form, and set the value of the parent input.
    $('form#comment_form')
      .find('textarea,input')
	.removeAttr('disabled').end()
      .find('input[name="parent"]')
	.val('s' + currentNode);

    // Position the popup and show it.
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
    // Prettify the comment rating.
    comment.pretty_rating = comment.rating + ' point' +
      (comment.rating == 1 ? '' : 's');
    // Create a div for this comment.
    var context = $.extend({}, comment, opts);
    var div = $(renderTemplate(commentTemplate, context));
    div.data('comment', comment);

    // If the user has voted on this comment, highlight the correct arrow.
    if (comment.vote) {
      var dir = comment.vote == 1 ? 'u' : 'd';
      div.find('#' + dir + 'v' + comment.id).hide();
      div.find('#' + dir + 'u' + comment.id).show();
    }

    // If this comments parent is a node, it will be appended to the main
    // comment list, otherwise it goes in it's parent's child list.
    if (comment.node != null)
      var list = $('ul#comment_ul');
    else
      var list = $('#cl' + comment.parent);
    list.append($('<li></li>').html(div));

    // Recursively insert any children.
    $.each(comment.children, function() {
      insertComment(this);
    });
  };

  /**
   * Add a comment via ajax and insert the comment into the comment tree.
   */
  function addComment(form) {
    // Disable the form that is being submitted.
    form.find('textarea,input').attr('disabled', 'disabled');

    // Send the comment to the server.
    $.ajax({
      type: "POST",
      url: opts.addCommentURL,
      dataType: 'json',
      data: {parent: form.find('input[name="parent"]').val(),
	     text: form.find(' textarea[name="comment"]').val()},
      success: function(data, textStatus, error) {
	// Reset the form.
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
   * Function to process a vote when a user clicks an arrow.
   */
  function processVote(link) {
    var id = link.attr('id');

    // If it is an unvote, the new vote value is 0,
    // Otherwise it's 1 for an upvote, or -1 for a downvote.
    if (id.charAt(1) == 'u')
      var value = 0;
    else
      var value = id.charAt(0) == 'u' ? 1 : -1;

    // The data to be sent to the server.
    var d = {
      comment_id: id.substring(2),
      value: value
    };

    // Swap the vote and unvote links.
    link.hide();
    var newLink = $('#' + id.charAt(0) + (id.charAt(1) == 'u' ? 'v' : 'u') + d.comment_id);
    newLink.show();

    // If this is not an unvote, and the other vote arrow has
    // already been pressed, unpress it.
    if (d.value != 0) {
      var other = $('#' + (d.value == 1 ? 'd' : 'u') + 'u' + d.comment_id);
      if (other.is(':visible')) {
	other.hide();
	$('#' + (d.value == 1 ? 'd' : 'u') + 'v' + d.comment_id).show();
      }
    }

    // Change the score value displayed to the user.
    var div = $('div#cd' + d.comment_id);
    // Update the comment data associated with the div.
    var data = div.data('comment');
    data.rating += (data.vote == 0) ? d.value : (d.value - data.vote);
    data.vote = d.value;
    div.data('comment', data);
    // Change the rating text.
    div.find('.rating:first')
      .text(data.rating + ' point' + (data.rating == 1 ? '' : 's'));

    // Send the vote information to the server.
    $.ajax({
      type: "POST",
      url: opts.processVoteURL,
      data: d,
      error: function(request, textStatus, error) {
	alert(textStatus);
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
    // Remove the reply div from the DOM.
    $('#rd' + id).remove();
    // Swap out the hide link for the reply link
    $('#cr' + id).hide();
    $('#rl' + id).show();
  };

  /**
   * A simple template renderer. Placeholders such as <%id%> are replaced
   * by context['id']. Items are always escaped.
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
    processVoteURL: '/process_vote',
    addCommentURL: '/add_comment',
    getCommentsURL: '/get_comments',
    commentHTML: '<img src="/static/comment.png" alt="comment" />',
    upArrow: '/static/up.png',
    downArrow: '/static/down.png',
    upArrowPressed: '/static/up-pressed.png',
    downArrowPressed: '/static/down-pressed.png',
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
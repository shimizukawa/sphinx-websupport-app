
jQuery.fn.comment = function() {
  $(this).append(' <a href="#" class="sphinx_comment"><img src="/static/comment.png" alt="comment" /></a>');
  $("a.sphinx_comment").click(function() {
    var id = $(this).parent().attr('id');
    alert('[ comment stub ' + id + ' ]');
    return false;
  });
}

$(document).ready(function() {
  $("div.context").each(function() {
    var params = $.getQueryParameters();
    var terms = (params.q) ? params.q[0].split(/\s+/) : [];
    var result = $(this);
    $.each(terms, function() {
      result.highlightText(this.toLowerCase(), 'highlighted');
    });
  });
});


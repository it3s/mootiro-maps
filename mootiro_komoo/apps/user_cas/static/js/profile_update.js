(function() {
  var $;

  $ = jQuery;

  $(function() {
    $('#form-profile').ajaxform({
      clean: false,
      onSuccess: function(data) {
        var $messageBox, msgTemplate, renderedContent;
        console.log(data);
        $messageBox = $('.form-message-box');
        if ($messageBox.length) $messageBox.remove();
        msgTemplate = _.template($('#form-message-box').html());
        renderedContent = msgTemplate({
          msg: gettext('Seus dados públicos foram salvos com sucesso!')
        });
        $('#form-profile .form-actions').before(renderedContent);
        $('#form-profile .alert').fadeIn();
        return false;
      }
    });
    $('#form-personal').ajaxform({
      clean: false,
      onSuccess: function(data) {
        var $messageBox, msgTemplate, renderedContent;
        console.log(data);
        $messageBox = $('.form-message-box');
        if ($messageBox.length) $messageBox.remove();
        msgTemplate = _.template($('#form-message-box').html());
        renderedContent = msgTemplate({
          msg: gettext('Seus dados pessoais foram salvos com sucesso!')
        });
        $('#form-personal .form-actions').before(renderedContent);
        $('#form-personal .alert').fadeIn();
        return false;
      }
    });
    $('#form-profile').komooFormHintBoxes({
      'contact': {
        hint: 'Este Contanto ficará visível para outros usuários do MootiroMaps!',
        top: '30%'
      }
    });
    return $('.alert .close').live('click', function() {
      return $(this).parent().slideUp();
    });
  });

}).call(this);

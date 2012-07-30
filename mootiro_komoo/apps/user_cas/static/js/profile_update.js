(function() {
  var $;

  $ = jQuery;

  window.Signature = Backbone.Model.extend({
    imageName: function() {
      var modelName;
      if (this.model_name === 'organizationbranch') {
        modelName = 'organization';
      } else {
        modelName = this.model_name;
      }
      return "/static/img/updates-page/" + modelName + "-feed.png";
    },
    toJSON: function(attr) {
      var defaultJSON;
      defaultJSON = Backbone.Model.prototype.toJSON.call(this, attr);
      return _.extend(defaultJSON, {
        imageName: this.imageName
      });
    }
  });

  window.SignatureView = Backbone.View.extend({
    className: 'signature',
    initialize: function() {
      _.bindAll(this, 'render');
      return this.template = _.template($('#signature-template').html());
    },
    render: function() {
      var renderedContent;
      console.log('rendering model: ', this.model.toJSON());
      renderedContent = this.template(this.model.toJSON());
      $(this.el).html(renderedContent);
      return this;
    }
  });

  window.SignaturesList = Backbone.Collection.extend({
    model: Signature
  });

  window.SignaturesListView = Backbone.View.extend({
    initialize: function() {
      _.bindAll(this, 'render');
      this.template = _.template($('#signatures-list-collection').html());
      return this.collection.bind('reset', this.render);
    },
    render: function() {
      var $signatures, collection,
        _this = this;
      $(this.el).html(this.template({}));
      $signatures = this.$('.signatures-list');
      collection = this.collection;
      collection.each(function(sign) {
        var view;
        view = new SignatureView({
          model: sign,
          collection: collection
        });
        return $signatures.append(view.render().el);
      });
      this.$('#signatures-manage-btn').click(function() {
        return alert('manage mailing options');
      });
      return this;
    }
  });

  $(function() {
    var loadedSignatures, signaturesListView;
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
    $('#form-profile').komooFormHintBoxes({
      'contact': {
        hint: 'Este Contanto ficará visível para outros usuários do MootiroMaps!',
        top: '30%'
      }
    });
    $('.alert .close').live('click', function() {
      return $(this).parent().slideUp();
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
    loadedSignatures = new SignaturesList();
    loadedSignatures.reset(window.KomooNS.signatures);
    signaturesListView = new SignaturesListView({
      collection: loadedSignatures
    });
    return $('.signatures-list-wrapper').append(signaturesListView.render().el);
  });

}).call(this);

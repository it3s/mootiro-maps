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
    },
    deleteSignature: function() {
      var self;
      console.log('Deleting signature ', this.attributes);
      if (confirm(gettext('Are you sure you want to delete your signature for this object?'))) {
        self = this;
        return $.post('/user/profile/signature/delete/', {
          id: this.get('signature_id')
        }, function(data) {
          console.dir(data);
          return self.trigger('deleteSignature', self);
        }, 'json');
      }
    }
  });

  window.SignatureView = Backbone.View.extend({
    className: 'signature',
    events: {
      'click .cancel-subscription-btn': 'cancelSubscription'
    },
    initialize: function() {
      _.bindAll(this, 'render', 'cancelSubscription', 'remove');
      this.template = _.template($('#signature-template').html());
      return this.model.bind('deleteSignature', this.remove);
    },
    render: function() {
      var renderedContent;
      console.log('rendering model: ', this.model.toJSON());
      renderedContent = this.template(this.model.toJSON());
      $(this.el).html(renderedContent);
      return this;
    },
    cancelSubscription: function() {
      this.model.deleteSignature();
      return this;
    },
    remove: function() {
      $(this.el).slideUp(300, function() {
        return $(this).remove();
      });
      return this;
    }
  });

  window.SignaturesList = Backbone.Collection.extend({
    model: Signature
  });

  window.SignaturesListView = Backbone.View.extend({
    events: {
      'click #signatures-manage-btn': 'mailingOptions'
    },
    initialize: function() {
      _.bindAll(this, 'render', 'mailingOptions');
      this.template = _.template($('#signatures-list-collection').html());
      return this.collection.bind('reset', this.render);
    },
    render: function() {
      var $signatures, collection;
      $(this.el).html(this.template({}));
      $signatures = this.$('.signatures-list');
      collection = this.collection;
      collection.each(function(sign) {
        var view;
        view = new SignatureView({
          model: sign
        });
        return $signatures.append(view.render().el);
      });
      return this;
    },
    mailingOptions: function() {
      alert('manage mailing options');
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

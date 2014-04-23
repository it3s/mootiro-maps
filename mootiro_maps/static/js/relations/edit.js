(function() {

  function isValidDate(date) {
    if (!date || date.length === 0) { return true; }
    var matches = /^(\d{2})[-\/](\d{2})[-\/](\d{4})$/.exec(date);
    if (matches == null) { return false; }

    var d = matches[1];
    var m = matches[2] - 1;
    var y = matches[3];
    var composedDate = new Date(y, m, d);
    return composedDate.getDate() == d &&
           composedDate.getMonth() == m &&
           composedDate.getFullYear() == y;
  };

  function isNumber(num) {
    return !isNaN(parseFloat(num));
  }

  var autocompleteWidget = function(container) {
    return {
      container: container,

      init: function() {
        this.input = this.container.find('.target_autocomplete');
        this.field = this.container.find('.target');
        this.dropdown = this.container.find('select[name=relation_type]');
        this.metadataBtn = this.container.find('.metadata-btn');
        this.metadataForm = this.container.find('.metadata-form');
        this.startPlugin();
        return this;
      },

      onFocus: function(_this, ui) {
        _this.input.val(ui.item.label);
        return false;
      },

      onSelect: function(_this, ui) {
        _this.input.val(ui.item.label);
        _this.field.val(ui.item.value);
        _this.container.trigger('relations:update');
        return false;
      },

      onChange: function(_this, ui) {
        if(!ui.item || !_this.input.val()){
          _this.field.val('');
          _this.input.val('');
          _this.container.trigger('relations:update');
        }
      },

      startPlugin: function() {
        var _this = this;
        _this.input.autocomplete({
          source: _this.input.attr('data-autocomplete'),
          focus:  function(event, ui) { return _this.onFocus(_this, ui); },
          select: function(event, ui) { return _this.onSelect(_this, ui); },
          change: function(event, ui) { return _this.onChange(_this, ui); },
        });

        _this.dropdown.change(function() { _this.container.trigger('relations:update'); });
      },

      loadValues: function(obj) {
        this.input.val(obj.target_name);
        this.field.val(obj.target_oid);
        this.dropdown.find('option[value="' +  obj.direction + obj.rel_type + '"]').attr('selected', 'selected');
        this.container.trigger('relations:update');
      }
    };
  };

  var relationsManager = function() {
    return {
      init: function() {
        this.relationsList = $('.relations-edit .relations-list');
        this.relationTpl = $('#relation-item-tpl').html();
        this.addButton = $('.add-relation');
        this.input = $(".relations-edit input[name='relations_json']");
        this.submitBtn = $(".relations-edit input[type='submit']");

        this.bindEvents();

        this.loadInitialData();
        this.addNewRelation();  // starts with at least one relation entry
      },

      loadInitialData: function() {
        var _this = this;
        var relations = _this.relationsList.data('relations');
        _.each(relations, function(rel) {
          var widget = _this.addNewRelation();
          widget.loadValues(rel);
        });
      },

      addNewRelation: function() {
        var _this = this;
        var relationItem = $(_this.relationTpl);
        this.relationsList.append(relationItem);
        relationItem.on('relations:update', function() { _this.updateInput(_this); });
        return autocompleteWidget(relationItem).init();
      },

      onRemove: function(_this, el) {
        el.closest('.relation-item').remove();
        _this.updateInput(_this);
      },

      onClickMetadata: function(_this, el) {
        var icon = el.find('i');
        var metadataForm = el.closest('.relation-item').find('.metadata-form');
        if (icon.is('.icon-plus')) {
          icon.removeClass('icon-plus').addClass('icon-minus');
          metadataForm.slideDown();
        } else {
          icon.removeClass('icon-minus').addClass('icon-plus');
          metadataForm.slideUp();
        }
      },

      validateDateInput: function(_this, el) {
        var date = el.val();
        if (isValidDate(date)) {
          el.removeClass('error');
          el.closest('.date-field').find('.error-msg').slideUp();
          if ($('.relations-edit .error').length === 0) _this.submitBtn.removeAttr('disabled');
        } else {
          el.addClass('error');
          el.closest('.date-field').find('.error-msg').slideDown();
          _this.submitBtn.attr('disabled', 'disable');
        }
      },

      validateNumberInput: function(_this, el) {
        var number = el.val();
        if (!number || number.lenght === 0 || isNumber(number)) {
          el.removeClass('error');
          el.closest('.number-field').find('.error-msg').slideUp();
          if ($('.relations-edit .error').length === 0) _this.submitBtn.removeAttr('disabled');
        } else {
          el.addClass('error');
          el.closest('.number-field').find('.error-msg').slideDown();
          _this.submitBtn.attr('disabled', 'disable');
        }
      },

      updateInput: function(_this) {
        var relations = [];
        _this.relationsList.find('.relation-item').each(function(i, el) {
          var $el = $(el);
          var rel = $el.find('[name=relation_type]').val();
          var target = $el.find('.target').val()
          if (target && target.length > 0 && rel && rel.length > 0) {
            relations.push({
              direction: rel[0],
              rel_type : rel.substring(1, rel.length),
              target   : target,
            })
          }
        });
        _this.input.val(JSON.stringify(relations));
      },

      bindEvents: function() {
        var _this = this;
        _this.addButton.click(function(){ _this.addNewRelation() });
        $('.relations-edit .remove-btn').live('click', function(evt) {
          _this.onRemove(_this, $(evt.target));
        });

        $('.relations-edit .metadata-btn').live('click', function(evt) {
          var el = $(evt.target);
          var target = el.is('i') ? el.parent() : el; // kludge for fixing weird behavior when click exactly over the icon
          _this.onClickMetadata(_this, target);
        });

        $('.date-input').live('change', function(evt) { _this.validateDateInput(_this, $(evt.target)); });
        $('.number-input').live('change', function(evt) { _this.validateNumberInput(_this, $(evt.target)); });
      }
    };
  };

  $(function(){
    relationsManager().init();
  });

})();

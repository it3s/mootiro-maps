(function() {

  var autocompleteWidget = function(container) {
    return {
      container: container,

      init: function() {
        this.input = this.container.find('.target_autocomplete');
        this.field = this.container.find('.target');
        this.dropdown = this.container.find('select[name=relation_type]');
        this.startPlugin();
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
    };
  };

  var relationsManager = function() {
    return {
      init: function() {
        this.relationsList = $('.relations-edit .relations-list');
        this.relationTpl = $('#relation-item-tpl').html();
        this.addButton = $('.add-relation');
        this.input = $(".relations-edit input[name='relations_json']");

        this.addNewRelation();  // starts with at least one relation entry
        this.bindEvents();
      },

      addNewRelation: function() {
        var _this = this;
        var relationItem = $(_this.relationTpl);
        this.relationsList.append(relationItem);
        relationItem.on('relations:update', function() { _this.updateInput(_this); });
        autocompleteWidget(relationItem).init();
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
      }
    };
  };

  $(function(){
    relationsManager().init();
  });

})();

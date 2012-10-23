(function() {

  define(['jquery', 'underscore', 'backbone', 'text!templates/widgets/_autocomplete.html', 'jquery-ui'], function($, _, Backbone, tplt) {
    var AutocompleteView;
    AutocompleteView = Backbone.View.extend({
      className: 'autocomplete',
      inputName: 'autocomplete',
      autocompleteSource: '/autocomplete/',
      initialize: function(inputName, autocompleteSource) {
        this.inputName = inputName || this.inputName;
        this.autocompleteSource = autocompleteSource || this.autocompleteSource;
        return this.template = _.template(tplt);
      },
      clear: function() {
        this.$input.val('');
        return this.$value.val('');
      },
      val: function() {
        console.log('value', this.$value.val());
        return this.$value.val();
      },
      render: function() {
        var renderedContent,
          _this = this;
        renderedContent = this.template({
          name: this.inputName
        });
        this.$el.html(renderedContent);
        this.$input = this.$el.find("#id_" + this.inputName + "_autocomplete");
        this.$value = this.$el.find("#id_" + this.inputName);
        this.$input.autocomplete({
          source: this.autocompleteSource,
          focus: function(event, ui) {
            _this.$input.val(ui.item.label);
            return false;
          },
          select: function(event, ui) {
            _this.$input.val(ui.item.label);
            _this.$value.val(ui.item.value);
            return false;
          },
          change: function(event, ui) {
            if (!ui.item || !_this.$input.val()) return _this.clear();
          }
        });
        return this;
      }
    });
    return AutocompleteView;
  });

}).call(this);

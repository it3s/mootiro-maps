$(function(){

  var autocompleteWidget = function(container) {
    return {
      container: container,

      init: function() {
        this.input = this.container.find('.target_autocomplete');
        this.field = this.container.find('.target');
        this.startPlugin();
      },

      startPlugin: function() {
        var _this = this;
        _this.input.autocomplete({
          source: _this.input.attr('data-autocomplete'),
          focus: function(event, ui) {
            _this.input.val(ui.item.label);
            return false;
          },
          select: function(event, ui) {
            _this.input.val(ui.item.label);
            _this.field.val(ui.item.value);
            return false;
          },
          change: function(event, ui) {
            if(!ui.item || !_this.input.val()){
                _this.field.val('');
                _this.input.val('');
            }
          }
        });
      },
    };
  }

  var addNewRelation = function() {
    var relationTpl = $('#relation-item-tpl').html();
    var relationItem = $(relationTpl);
    $('.relations-edit .relations-list').append(relationItem);
    autocompleteWidget(relationItem).init();
  }

  $('.add-relation').click(function(){
    addNewRelation();
  });

  addNewRelation();

});

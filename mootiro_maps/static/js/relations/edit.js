$(function(){
  var autocompleteWidget = function(container) {
    return {
      container: container,

      init: function() {
        this.startPlugin();
      },

      startPlugin: function() {
        var _this = this;
        _this.container.autocomplete({
          source: _this.container.attr('data-autocomplete'),
          focus: function(event, ui) {
            $("#id_target_autocomplete").val(ui.item.label);
            return false;
          },
          select: function(event, ui) {
            $("#id_target_autocomplete").val(ui.item.label);
            $("#id_target").val(ui.item.value);
            return false;
          },
          change: function(event, ui) {
            if(!ui.item || !$("#id_target_autocomplete").val()){
                $("#id_target_autocomplete").val('');
                $("#id_target").val('');
            }
          }
        });
      },
    };
  }

  var target_autocomplete =  $("#id_target_autocomplete");
  autocompleteWidget(target_autocomplete).init();

});

$(function(){

  $("#id_target_autocomplete").autocomplete({
    source: [
      'object 1',
      'blablabal',
      'resource bla',
    ],
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
});

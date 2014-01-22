// ContactsWidget Module
var ContactsWidget = {
  onChange: function() {
    // TODO implement-me
    // change events callback
  },

  listen: function() {
    // TODO implement-me
    // listen for change events
  },

  onLoad: function() {
    var field = $("#id_contacts");
    var initialValues = JSON.parse(field.val());

    this.loadInitialValues(initialValues);
    this.listen();
  },

  loadInitialValues: function(initialValues) {
    var module = this;  // reference for the ContactsWidget module itself

    _.each(initialValues, function(value, key) {
      if (typeof value !== "undefined" && value !== null) {
        module.renderKeyValuePair(key, value);
      }
    });
  },

  renderKeyValuePair: function(key, value) {
    console.log("rendering contacts: key=%s value=%s", key, value);
  },


};

$(function() {
  ContactsWidget.onLoad();
});

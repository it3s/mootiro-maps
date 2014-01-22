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
    this.field = $("#id_contacts");
    this.contactsListField = $(".contacts-list");
    var initialValues = JSON.parse(this.field.val());

    this.loadInitialValues(initialValues);
    this.listen();
  },

  getKeyName: function(key) {
    return this.field.data("key-names")[key];
  },

  keyOrder: function() {
    return [
      'address',
      'compl',
      'city',
      'postal_code',
      'phone',
      'facebook',
      'email',
      'twitter',
      'site',
      '---',
    ];
  },

  loadInitialValues: function(initialValues) {
    var module = this;  // reference for the ContactsWidget module itself

    _.each(module.keyOrder(), function(key) {
      var value = initialValues[key];
      module.renderKeyValuePair(key, module.getKeyName(key), value);
    });
  },

  renderKeyValuePair: function(key, keyName, value) {
    console.log("rendering contacts: key=%s value=%s", key, value);
    this.contactsListField.append("" +
      "<div class=\"contact-kv\">" +
        "<label>" + keyName + "</label>" +
        "<input type='text' value='" + (value || "") + "' data-key='" + key + "' />" +
      "</div>"
    );
  },


};

$(function() {
  ContactsWidget.onLoad();
});

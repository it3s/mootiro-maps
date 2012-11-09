(function() {

  define(['backbone', 'underscore', 'text!templates/map/_searchbox.html'], function(Backbone, _, tplt) {
    var SearchBoxView;
    SearchBoxView = Backbone.View.extend({
      events: {
        'click .search': 'onSearchBtnClick',
        'change .location-type': 'onTypeChange'
      },
      initialize: function() {
        return this.template = _.template(tplt);
      },
      render: function() {
        var renderedContent;
        renderedContent = this.template();
        this.$el.html(renderedContent);
        return this;
      },
      onTypeChange: function() {
        var type;
        type = this.$('.location-type').val();
        if (type === 'address') {
          this.$('.latLng-container').hide();
          return this.$('.address-container').show();
        } else {
          this.$('.address-container').hide();
          return this.$('.latLng-container').show();
        }
      },
      onSearchBtnClick: function() {
        var position, type;
        type = this.$('.location-type').val();
        position = type === 'address' ? this.$('.address').val() : [parseFloat(this.$('.lat').val().replace(',', '.')), parseFloat(this.$('.lng').val().replace(',', '.'))];
        this.search(type, position);
        return false;
      },
      search: function(type, position) {
        if (type == null) type = 'address';
        this.trigger('search', {
          type: type,
          position: position
        });
        return this;
      }
    });
    return {
      SearchBoxView: SearchBoxView
    };
  });

}).call(this);

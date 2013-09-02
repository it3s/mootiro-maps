(function(){var e=Object.prototype.hasOwnProperty,t=function(t,n){function i(){this.constructor=t}for(var r in n)e.call(n,r)&&(t[r]=n[r]);return i.prototype=n.prototype,t.prototype=new i,t.__super__=n.prototype,t};define(["require","googlemaps","./component"],function(e){var n,r,i,s,o,u;return o=e("googlemaps"),n=e("./component"),window.komoo==null&&(window.komoo={}),(u=window.komoo).event==null&&(u.event=o.event),i=function(e){function n(){n.__super__.constructor.apply(this,arguments)}return t(n,e),n.prototype.name="Generic Provider",n.prototype.alt="Generic Data Provider",n.prototype.tileSize=new o.Size(256,256),n.prototype.maxZoom=32,n.prototype.expiration=6e5,n.prototype.enabled=!0,n.prototype.init=function(e){return this.options=e,this.addrLatLngCache={},this.fetchedTiles={}},n.prototype.setMap=function(e){return this.map=e,this.map.googleMap.overlayMapTypes.insertAt(0,this),typeof this.handleMapEvents=="function"?this.handleMapEvents():void 0},n.prototype.enable=function(){return this.enabled=!0},n.prototype.disable=function(){return this.enabled=!1},n.prototype.getUrl=function(e,t){var n,r;return n=this.getAddrLatLng(e,t),r=this.fetchUrl+n,this.map.getProjectId()&&(r+="&project="+this.map.getProjectId()),r},n.prototype.getAddrLatLng=function(e,t){var n,r,i,s,u,a,f;return n="x="+e.x+",y="+e.y+",z="+t,this.addrLatLngCache[n]?this.addrLatLngCache[n]:(i=1<<t,a=this.map.googleMap.getProjection(),s=new o.Point((e.x+1)*this.tileSize.width/i,e.y*this.tileSize.height/i),u=new o.Point(e.x*this.tileSize.width/i,(e.y+1)*this.tileSize.height/i),r=a.fromPointToLatLng(s),f=a.fromPointToLatLng(u),this.addrLatLngCache[n]="bounds="+r.toUrlValue()+","+f.toUrlValue()+"&zoom="+t)},n}(n),r=function(e){function n(){n.__super__.constructor.apply(this,arguments)}return t(n,e),n.prototype.name="Feature Provider",n.prototype.alt="Feature Provider",n.prototype.fetchUrl="/get_geojson?",n.prototype.init=function(e){return n.__super__.init.call(this,e),this.keptFeatures=komoo.collections.makeFeatureCollection(),this.openConnections=0,this._addrs=[],this._requestQueue={}},n.prototype.handleMapEvents=function(){var e=this;return this.map.subscribe("idle",function(){var t;return t=e.map.googleMap.getBounds(),e.keptFeatures.forEach(function(e){if(!t.intersects(e.getBounds()))return e.setMap(null)}),e.keptFeatures.clear()}),this.map.subscribe("zoom_changed",function(){var t,n,r,i;r=e._requestQueue,i=[];for(t in r)n=r[t],i.push(n.abort());return i})},n.prototype.releaseTile=function(e){var t;if(this.enabled===!1)return;if(this.fetchedTiles[e.addr])return t=this.map.getBounds(),this.map.data.when(this.fetchedTiles[e.addr].features,function(e){var n=this;return e.forEach(function(e){if(e.getBounds){if(!t.intersects(e.getBounds()))return e.setMap(null);if(!t.contains(e.getBounds().getNorthEast()||!t.contains(e.getBounds().getSouthWest())))return n.keptFeatures.push(e),e.setMap(n.map)}else if(e.getPosition&&!t.contains(e.getPosition()))return e.setVisible(!1),e.setMap(null)})})},n.prototype.getTile=function(e,t,n){var r,i,s,o,u=this;return s=n.createElement("DIV"),r=this.getAddrLatLng(e,t),s.addr=r,this.enabled===!1||this.map.options.ajax===!1?(this.map.publish("features_request_completed"),s):(i=new Date,this.fetchedTiles[r]&&i-this.fetchedTiles[r].date<=this.expiration?(typeof (o=this.fetchedTiles[r].features).setMap=="function"&&o.setMap(this.map),s):(this.openConnections===0&&this.map.publish("features_request_started"),this.openConnections++,this.map.publish("features_request_queued"),this._requestQueue[r]=$.ajax({url:this.getUrl(e,t),dataType:"json",type:"GET",success:function(e){var t;return t=u.map.data.deferred(),u._addrs.push(r),u.fetchedTiles[r]={geojson:e,features:t.promise(),date:new Date}},error:function(e,t){var n,r;if(t==="abort")return;return typeof console!="undefined"&&console!==null&&console.error("[provider - ajax error] "+t),r=$("#server-error"),r.parent().length===0&&(r=$("<div>").attr("id","server-error"),$("body").append(r)),n=$("<div>").html(e.responseText),r.append(n)},complete:function(){var e,t,n;u.map.publish("features_request_unqueued"),u.openConnections--;if(u.openConnections===0){u.map.publish("features_request_completed");while(u._addrs.length>0)r=u._addrs.pop(),e=u.fetchedTiles[r].geojson,t=u.map.loadGeoJSON(JSON.parse(e),!1,!0,!0),typeof (n=u.fetchedTiles[r].features).resolve=="function"&&n.resolve(t),u.fetchedTiles[r].features=t;return delete u._requestQueue[r],u.map.publish("features_loaded",u.map.getFeatures())}}}),s))},n}(i),s=function(e){function n(){n.__super__.constructor.apply(this,arguments)}return t(n,e),n.prototype.getUrl=function(e,t){var r,i,s,o,u;r=n.__super__.getUrl.call(this,e,t),o=[],u=this.map.featureTypes;for(s in u)i=u[s],(this.map.getProjectId()!=null||s==="Community"||i.minZoomPoint<=t&&i.maxZoomPoint>=t||i.minZoomGeometry<=t&&i.maxZoomGeometry>=t)&&o.push(""+i.appLabel+"."+i.modelName);return r+="&models="+o.join(",")},n}(r),window.komoo.providers={GenericProvider:i,FeatureProvider:r,ZoomFilteredFeatureProvider:s,makeFeatureProvider:function(e){return new r(e)}},window.komoo.providers})}).call(this);
/**
 * MultiMarker for Google Maps.
 *
 * @name multimarker.js
 * @fileOverview Group Google Maps Markers together.
 * @version 0.1.0
 * @author Luiz Armesto
 * @copyright (c) 2012 it3s
 */

define(["googlemaps"],function(e){return MultiMarker=function(t){t=t||{},this.markers_=new e.MVCArray(t.markers||[]),this.positions_=new e.MVCArray(t.positions||[]),this.map_=t.map,this.visible_=t.visible,this.clickable_=t.clickable,this.draggable_=t.draggable,this.icon_=t.icon,this.zIndex=t.zIndex||0},MultiMarker.prototype.getPosition=function(){return this.markers_.getAt(0).getPosition()},MultiMarker.prototype.getPositions=function(){this.positions_.clear();for(var e=0;e<this.markers_.getLength();e++)this.positions_.push(this.markers_.getAt(e).getPosition());return this.positions_},MultiMarker.prototype.setPositions=function(e){if(e.length!=this.markers_.getLength())throw"Invalid length.";this.positions_.clear();for(var t=0;t<this.markers_.getLength();t++)this.markers_.getAt(t).setPosition(e[t]),this.positions_.push(e[t])},MultiMarker.prototype.addMarker=function(t,n){var r=this;this.markers_.push(t),n||this.icon_&&t.setIcon(this.icon_),e.event.addListener(t,"click",function(n){e.event.trigger(r,"click",n,t)}),e.event.addListener(t,"mouseover",function(n){e.event.trigger(r,"mouseover",n,t)}),e.event.addListener(t,"mouseout",function(n){e.event.trigger(r,"mouseout",n,t)}),e.event.addListener(t,"mousemove",function(n){e.event.trigger(r,"mousemove",n,t)})},MultiMarker.prototype.addMarkers=function(e,t){for(var n=0;n<e.length;n++)this.addMarker(e[n],t)},MultiMarker.prototype.getMarkers=function(){return this.markers_},MultiMarker.prototype.setDraggable=function(e){for(var t=0;t<this.markers_.getLength();t++)this.markers_.getAt(t).setDraggable(e);this.draggable_=e},MultiMarker.prototype.getDraggable=function(){return this.draggable_},MultiMarker.prototype.setMap=function(e){for(var t=0;t<this.markers_.getLength();t++)this.markers_.getAt(t).setMap(e);this.map_=e},MultiMarker.prototype.getMap=function(){return this.map_},MultiMarker.prototype.setIcon=function(e){for(var t=0;t<this.markers_.getLength();t++)this.markers_.getAt(t).setIcon(e);this.icon_=e},MultiMarker.prototype.getIcon=function(){return this.icon_},MultiMarker.prototype.setVisible=function(e){for(var t=0;t<this.markers_.getLength();t++)this.markers_.getAt(t).setVisible(e);this.visible_=e},MultiMarker.prototype.getVisible=function(){return this.visible_},MultiMarker})
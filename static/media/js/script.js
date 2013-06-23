var jPanelMenu = {};
$(function() {	
	jPanelMenu = $.jPanelMenu({
		menu: '#jPanelMenu-menu',
    trigger: '.menu-trigger'
	});
	jPanelMenu.on();

});

$(document).ready(function() {
  $("#datepicker1").datepicker();
$("#datepicker2").datepicker();
});


	function initialize() {
	  var myLatlng = new google.maps.LatLng(41,-87);
	  var mapOptions = {
	    zoom: 8,
	    center: myLatlng,
	    mapTypeId: google.maps.MapTypeId.ROADMAP
	  }
	  var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

	  var marker = new google.maps.Marker({
	      position: myLatlng,
	      map: map,
	      title: 'Hello World!'
	  });
	}

	google.maps.event.addDomListener(window, 'load', initialize);
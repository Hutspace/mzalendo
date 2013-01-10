(function () {

  function initialize_map() {

    var map_element = document.getElementById("map-drilldown-canvas");
    if (!map_element) return false;

    // start with the default bounds for kenya
    var map_bounds = {
      north: 5, 
      east:  44,
      south: -5,
      west:  33.5
    };

    var map_has_been_located = false;

    var myOptions = {
      mapTypeId: google.maps.MapTypeId.TERRAIN,
      maxZoom: 10
    };

    var map = new google.maps.Map(map_element, myOptions);

    map.fitBounds( make_bounds( map_bounds ) );

    // Add crosshairs at the center - see merging of answers at 
    // http://stackoverflow.com/questions/4130237
    var crosshairs_path = window.mzalendo_settings.static_url + 'images/crosshairs.png?' + window.mzalendo_settings.static_generation_number 

    var reticleImage = new google.maps.MarkerImage(
       crosshairs_path,                 // marker image
       new google.maps.Size(63, 63),    // marker size
       new google.maps.Point(0,0),      // marker origin
       new google.maps.Point(32, 32)    // marker anchor point
    );
    
    var reticleShape = {
      coords: [32,32,32,32],           // 1px
      type: 'rect'                     // rectangle
    };
    
    var reticleMarker = new google.maps.Marker({
      map: map,
      icon: reticleImage, 
    });
    
    reticleMarker.bindTo('position', map, 'center'); 
    
  }
  
  function make_bounds ( bounds ) {
      var sw = new google.maps.LatLng( bounds.south, bounds.west );
      var ne = new google.maps.LatLng( bounds.north, bounds.east );
      return new google.maps.LatLngBounds( sw, ne );
  }
  
  mzalendo_run_when_document_ready(
      function () {
          google.load(
              'maps', '3',
              {
                  callback: initialize_map,
                  other_params:'sensor=false'
              }
          );
      }
  );
})();
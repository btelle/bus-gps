var tracker = {
    line_id: null,
    map: null,
    mapbox_token: "pk.eyJ1IjoiYnJhbmRvbi10ZWxsZSIsImEiOiJjam5yeGl2bTMwMjBnM2twMzk0aG5oeDR6In0.iyT8aAhYlM9gDjXOw6CzRw",
    map_markers: {},
    init: function() {
        console.log('Application started');
        tracker.line_id = $('#leaflet-container').attr('data-line-id');

        var start_point = [
            parseFloat($('#leaflet-container').attr('data-start-lat')),
            parseFloat($('#leaflet-container').attr('data-start-long'))
        ]

        tracker.map = L.map('leaflet-container').setView(start_point, 13);
        L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            maxZoom: 18,
            id: 'mapbox.streets',
            accessToken: tracker.mapbox_token
        }).addTo(tracker.map);

        L.MakiMarkers.accessToken = tracker.mapbox_token;
        setInterval(tracker.update_locations, 5000);
    },
    update_locations: function() {
        $.ajax({
            url: "/api/locations/" + tracker.line_id,
            success: function(data, status) {
                for (i in data.buses) {
                    var bus = data.buses[i];

                    if (tracker.map_markers[bus.id]) {
                        tracker.map.removeLayer(tracker.map_markers[bus.id]);
                    }
                    
                    var icon = L.MakiMarkers.icon({icon: "bus", color: "#f90", size: "m"});
                    tracker.map_markers[bus.id] = L.marker([
                        parseFloat(bus.location.latitude),
                        parseFloat(bus.location.longitude)
                    ], {
                        icon: icon
                    });

                    tracker.map.addLayer(tracker.map_markers[bus.id]);
                    tracker.map_markers[bus.id].bindPopup(tracker.format_popup(bus));
                }
            }
        });
    },
    format_popup: function(bus) {
        html = "<b>Bus " + bus.id + "</b><br />";
        html += "Latitude: <code>" + bus.location.latitude.toString() + "</code><br />";
        html += "Longitude: <code>" + bus.location.longitude.toString() + "</code><br />";
        html += "Direction: <code>" + bus.direction + "</code><br />";
        html += "Published At: <code>" + bus.published_at + "</code><br />";

        return html;
    }
};

$(document).ready(function(){
    tracker.init();
});

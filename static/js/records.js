"use strict";

fetch('/get_token')
    .then(response => response.json())
    .then(data => {
        var mapboxToken = data.mapbox_token;
     
        mapboxgl.accessToken = mapboxToken;
        const map = new mapboxgl.Map({
            container: 'map',
            style: 'mapbox://styles/mapbox/navigation-night-v1',
            center: [-73.9, 40.7],
            zoom: 15 // starting zoom (0-22), higher number is more detail
        });
    });



"use strict";

// alert("JS is connected");
console.log("JS is connected");

// alert(`Hello ${process.env.MPBX_API_KEY}`);
console.log("Hello ${process.env.MPBX_API_KEY}");
// console.log(process.env.MPBX_API_KEY);


fetch('/get_token')
    .then(response => response.json())
    .then(data => {
        var mapboxToken = data.mapbox_token;
        console.log(mapboxToken)
        // Use mapboxToken in your Mapbox GL JS code
    });
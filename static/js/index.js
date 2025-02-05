
"use strict";


function getValue() {
    var input = document.getElementById("search");
    var input_value = input.value;
    return input_value
}

async function sendValue() {
    var user_input = getValue();
    const url = "https://geosearch.planninglabs.nyc/v2/autocomplete?text="+user_input;

    try {
        const response = await fetch(url);
        if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
        }

        const json = await response.json();
        return json
    } catch (error) {
        console.error(error.message);
    }
}

async function parseData() {
    var address_data = await sendValue();
    const address_labels = []
    address_data.features.forEach(element => {
        address_labels.push(element.properties.label)
    });
    return address_labels
}

async function createDropdown() {
    var search_input = document.getElementById("search");
    var address_list = await parseData()
    if (address_list) {
        var datalist = document.getElementById("addresses");
        datalist.replaceChildren();
        address_list.forEach(address => {
            var datalist = document.getElementById("addresses");
            const option = document.createElement('li');
            const span = document.createElement('span');
            span.textContent = address;
            option.className = "address-element";
            option.addEventListener('click', () => {
                search_input.value = span.textContent;
                search_input.focus()
                datalist.replaceChildren();
              });
            option.appendChild(span)
            datalist.appendChild(option);
        });
    }
}

var text_box = document.getElementById("search");
var addresses = document.getElementById("addresses");
text_box.addEventListener('input', function(event) {
    addresses.innerHTML = '';
    createDropdown();
});


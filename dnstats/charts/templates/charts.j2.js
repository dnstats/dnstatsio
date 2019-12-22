let options =  {
            tooltips: {
                enabled: true,
                type: "placeholder",
                string: "{label}: {value}, {percentage}%",
                styles: {
                    fadeInSpeed: 500,
                    backgroundColor: "#e5e5e5",
                    backgroundOpacity: 0.8,
                    color: "#ffffcc",
                    borderRadius: 4,
                    fontSize: 20,
                    padding: 3
                }
            },
            labels: {
                mainLabel: {
                    color: "#ffffff",
                    fontSize: 25
                },
                percentage: {
                    decimalPlaces: 3,
                    fontSize: 25
                }
            },
            size: {
                canvasHeight: 800,
                canvasWidth: 800,
                pieOuterRadius: "90%"
            },
            effect: {
                load: {
                    effect: 'none'
                }
            }
	};

{% for category in categories %}
    // Begin {{ category[1] }}_
    let {{ category[2] }}_id = document.getElementById('{{ category[2] }}');
    let {{ category[2] }}_data = {data: {
                content: [
    {% for data_point in category[3] %}{label: "{{ data_point['name'] }}", value: {{ data_point['value'] }},},
{% endfor %}
    ]}};
    let  {{ category[2] }}_chartOpts = Object.assign({{ category[2] }}_data, options);
    let {{ category[2] }}_chart = new d3pie({{ category[2] }}_id, {{ category[2] }}_chartOpts);
    // End {{ category[1] }}_
{% endfor %}
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
                    borderRadius: 2,
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
                    fontSize: 12,
                    color: '#f2f2f2',
                }
            },
            size: {
                canvasHeight: 650,
                canvasWidth: 650,
                pieOuterRadius: "65%"
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
    {% for data_point in category[3] %}{label: "{{ data_point['name'] }}", value: {{ data_point['value'] }}, color: "{{ data_point['color'] }}",},
{% endfor %}
    ]}};
    let  {{ category[2] }}_chartOpts = Object.assign({{ category[2] }}_data, options);
    let {{ category[2] }}_chart = new d3pie({{ category[2] }}_id, {{ category[2] }}_chartOpts);
    // End {{ category[1] }}_
{% endfor %}

let margin = {top: 10, right: 30, bottom: 30, left: 40},
    width = 460 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

{% for histogram in histograms %}
    let {{histogram[2]}}_svg = d3.select('{{ histogram[2] }}').attr("viewBox", [0, 0, width, height]);
    let {{histogram[2]}}_data = {{ histogram[3] }};
    function {{histogram[2]}}_draw(data) {
        let {{histogram[2]}}_x = d3.scaleBand().range([0, width]).domain(data.map(function (d) { return d.grade}));
        {{histogram[2]}}_svg.append("{{histogram[2]}}").attr("transform", "translate(0," + height + ")").call(d3.axisBottom({{histogram[2]}}_x));
        let {{histogram[2]}}_y = d3.scaleLinear().domain([0, 100]).range([0, height]);
        {{histogram[2]}}_svg.append("{{histogram[2]}}").call(d3.axisLeft({{histogram[2]}}_y));
        {{histogram[2]}}_svg.selectAll("{{histogram[2]}}_bars")
                            .data(data).enter()
                            .attr("x", function(d) { return {{histogram[2]}}_x(d.grade); })
                            .attr("y", function (d) { return  {{histogram[2]}}_y(d.count); })
                            .attr("width", {{histogram[2]}}_x.bandwidth())
                            .attr("height", function (d) { return height - y(d.value) })
                            .attr("fill", '#72e572');

    };
    {{histogram[2]}}_draw({{histogram[2]}}_data);


{% endfor %}
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

const margin = 60;
const width = 550 - 2 * margin;
const height = 550 - 2 * margin;

{% for histogram in histograms %}

    const {{histogram[2]}}_svg = d3.select('#{{ histogram[2] }}')
    const {{histogram[2]}}_data = {{histogram[3]}};

    const {{histogram[2]}}_chart = {{histogram[2]}}_svg.append('g')
    .attr('transform', `translate(${margin}, ${margin})`);


    const {{histogram[2]}}_xScale = d3.scaleLinear()
    .range([0, width])
    .domain([0, d3.max({{histogram[2]}}_data.map((s) =>  { return s; }))]);

    const {{histogram[2]}}_histogram = d3.histogram().value((s) => { return s }).domain({{histogram[2]}}_xScale.domain())
            .thresholds({{histogram[2]}}_xScale.ticks(5));

    const {{histogram[2]}}_bins = {{histogram[2]}}_histogram({{histogram[2]}}_data)

{{histogram[2]}}_chart.append('g')
    .attr('transform', `translate(0, ${height})`)
    .call(d3.axisBottom({{histogram[2]}}_xScale));

    const {{histogram[2]}}_yScale = d3.scaleLinear()
    .range([height, 0])
    .domain([0, d3.max({{histogram[2]}}_bins, (s) => { return s.length })]);

    {{histogram[2]}}_chart.append('g')
    .call(d3.axisLeft({{histogram[2]}}_yScale));


    {{histogram[2]}}_chart.append("g")
    .data({{histogram[2]}}_bins)
    .enter()
    .append('rect')
        .attr('x', 1)
        .attr("transform", (d) => { return "translate(" + {{histogram[2]}}_xScale(d.x0) + "," + {{histogram[2]}}_yScale(d.length) + ")"; })
        .attr('width', (d) => { return {{histogram[2]}}_xScale(d.x1) - {{histogram[2]}}_xScale(d.x0)  - 1; })
        .attr("height", (d) => { return height - {{histogram[2]}}_yScale(d.length); })
        .style("fill", "#69b3a2");


{% endfor %}
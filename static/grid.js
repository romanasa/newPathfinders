function gridData() {
	var data = new Array();
	var xpos = 1; //starting xpos and ypos at 1 so the stroke will show when we make the grid below
	var ypos = 1;
	var width = 50;
	var height = 50;
	var click = 0;

	// iterate for rows
	for (var row = 0; row < 10; row++) {
		data.push( new Array() );

		// iterate for cells/columns inside rows
		for (var column = 0; column < 10; column++) {
			data[row].push({
				x: xpos,
				y: ypos,
				width: width,
				height: height,
				click: click
			})
			// increment the x position. I.e. move it over by 50 (width variable)
			xpos += width;
		}
		// reset the x position after a row is complete
		xpos = 1;
		// increment the y position for the next row. Move it down 50 (height variable)
		ypos += height;
	}
	return data;
}

var gridData = gridData();
// I like to log the data to the console for quick debugging
console.log(gridData);

maze = [
[0,1,0,0,0,0,0,0,0,0],
[0,1,0,0,1,1,1,1,0,0],
[0,0,0,0,1,0,0,0,0,0],
[0,0,0,0,1,0,0,0,0,0],
[0,1,0,0,0,0,0,0,0,0],
[0,1,0,0,1,1,1,1,0,0],
[0,1,0,0,0,0,0,0,0,0],
[0,1,0,0,0,0,0,0,0,0],
[0,1,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0]
]

coins1 = [[3,0], [6,4], [2, 8], [9, 9], [0, 4], [3, 6]]
coins2 = [[3,0], [0, 4], [3, 6]]

function gridprepare(data) {
	var new_data = new Array();
	var xpos = 1; //starting xpos and ypos at 1 so the stroke will show when we make the grid below
	var ypos = 1;
	var width = 50;
	var height = 50;
	var click = 0;

	// iterate for rows
	for (var row = 0; row < 10; row++) {
		new_data.push( new Array() );

		// iterate for cells/columns inside rows
		for (var column = 0; column < 10; column++) {
			new_data[row].push({
				x: xpos,
				y: ypos,
				fill: data[row][column],
			})
			// increment the x position. I.e. move it over by 50 (width variable)
			xpos += width;
		}
		// reset the x position after a row is complete
		xpos = 1;
		// increment the y position for the next row. Move it down 50 (height variable)
		ypos += height;
	}
	return new_data;
}


console.log(maze);

var grid = d3.select("#grid")
	.append("svg")
	.attr("width","510px")
	.attr("height","510px");

var row = grid.selectAll(".row")
	.data(gridprepare(maze))
	.enter().append("g")
	.attr("class", "row");

var column = row.selectAll(".square")
	.data(function(d) { return d; })
	.enter().append("rect")
	.attr("class","square")
	.attr("x", function(d) { return d.x; })
	.attr("y", function(d) { return d.y; })
	.attr("width", "50")
	.attr("height", "50")
	.style("fill", function(d) {
	    if (d.fill) { return "#222" }
	    return "#fff"
	})
	.style("stroke", "#222");

points = null;

function draw_points(points_data) {
    if ( points != null ) {
        points.remove()
    }
    points = grid.selectAll(".points")
             .data(points_data)
             .enter().append("g")
             .attr("class", "point");

    points.append("circle")
          .attr("cx", function(d) { return d.x * 50 + 25})
          .attr("cy", function(d) { return d.y * 50 + 25})
          .attr("r", "20")
          .attr("fill", "orange");
}

//var coins_plot = grid.selectAll(".points")
//    .data(coins1)
//    .enter().append("g")
//    .attr("class", "point");
//
//    coins_plot.append("circle")
//    .attr("cx", function(d) { console.log(d); return d[0] * 50 + 25})
//    .attr("cy", function(d) { return d[1] * 50 + 25})
//    .attr("r", "20")
//`    .attr("fill", "orange");


//players_data = [ [4,7], [8,5], [6,3]]

//var players = grid.selectAll()
//    .data(players_data)
//    .enter().append("g")
//    .attr("class", "player");
//
//    players.append("rect")
//    .attr("x", function(d) { return d[0] * 50 + 6; })
//	.attr("y", function(d) { return d[1] * 50 + 6; })
//	.attr("width", "40")
//	.attr("height", "40")
//	.style("fill", "#fff")
//	.style("stroke", "#222");
//
//    players.append("circle")
//    .attr("cx", function(d) { return d[0] * 50 + 16})
//    .attr("cy", function(d) { return d[1] * 50 + 21})
//    .attr("r", "7")
//    .attr("fill", "#222");
//
//    players.append("circle")
//    .attr("cx", function(d) { return d[0] * 50 + 36})
//    .attr("cy", function(d) { return d[1] * 50 + 21})
//    .attr("r", "7")
//    .attr("fill", "#222");


players = null;

function draw_players(players_data) {
    // Remove previous players form plot
    if (players != null) {
        players.remove()
    }

    players = grid.selectAll()
              .data(players_data)
              .enter().append("g")
              .attr("class", "player");

    players.append("rect")
           .attr("x", function(d) { return d.x * 50 + 6; })
	       .attr("y", function(d) { return d.y * 50 + 6; })
	       .attr("width", "40")
	       .attr("height", "40")
	       .style("fill", "#fff")
	       .style("stroke", "#222");

    players.append("circle")
           .attr("cx", function(d) { return d.x * 50 + 16})
           .attr("cy", function(d) { return d.y * 50 + 21})
           .attr("r", "7")
           .attr("fill", "#222");

    players.append("circle")
           .attr("cx", function(d) { return d.x * 50 + 36})
           .attr("cy", function(d) { return d.y * 50 + 21})
           .attr("r", "7")
           .attr("fill", "#222");
}


function refresh_game() {
    d3.json("/v1/api/players", function (json) {
        draw_players(json.players)
    });

    d3.json("/v1/api/points", function (json) {
        draw_points(json.points)
    });
    setTimeout(refresh_game, 1000);
}

refresh_game()

function gridprepare(data) {
	var new_data = new Array();
	var xpos = 1; //starting xpos and ypos at 1 so the stroke will show when we make the grid below
	var ypos = 1;
	var width = 50;
	var height = 50;

	// iterate for rows
	for (var row = 0; row < 10; row++) {
		new_data.push( new Array() );

		// iterate for cells/columns inside rows
		for (var column = 0; column < 10; column++) {
			new_data[row].push({
				x: xpos,
				y: ypos,
				fill: data[row][column],
				width: width,
				height: height
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

// Draw maze
var grid = d3.select("#grid")
	.append("svg")
	.attr("width","510px")
	.attr("height","510px");

function draw_maze(maze_data) {
    var raw = grid.selectAll(".row")
	              .data(gridprepare(maze_data))
	              .enter().append("g")
	              .attr("class", "raw");

    raw.selectAll(".square")
	   .data(function(d) { return d; })
	   .enter().append("rect")
	   .attr("class","square")
	   .attr("x", function(d) { return d.x; })
	   .attr("y", function(d) { return d.y; })
	   .attr("width", function(d) { return d.width; })
	   .attr("height", function(d) { return d.height; })
	   .style("fill", function(d) {
	       if (d.fill) { return "#222" }
	       return "#fff"
	   })
	   .style("stroke", "#222");
}

d3.json("/v1/api/maze", function (json) {
        draw_maze(json.maze)
});

//Draw points on playboard
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

// Draw players on playboard.
pallete = ["green", "red", "blue", "yellow", "magenta", "white"]
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
	       .style("fill", function(d, i) { return pallete[i] })
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

// Write score table


columns = ["name", "score"];
var table = d3.select('#scores').append('table');
var thead = table.append('thead');
var	tbody = table.append('tbody');
thead.append('tr')
     .selectAll('th')
     .data(columns).enter()
     .append('th')
     .text(function (d) { return d; });
var rows = null;

function print_scores(points_data) {
    if (rows != null) {
        rows.remove();
    }
    rows = tbody.selectAll('tr')
		            .data(points_data)
		            .enter()
		            .append('tr')
		            .style("color", function(d,i) {return pallete[i]});
    var cells = rows.selectAll('td')
		            .data(function (row) {
		                return columns.map(function (d) {
		                   return {column: d, value: row[d]};
		                });
		            })
		            .enter()
		            .append('td')
		            .append('p')
		            .text(function (d) { return d.value; });

}


//Refresh points and players positions peridically
function refresh_game() {
    d3.json("/v1/api/players", function (json) {
        draw_players(json.players);
        print_scores(json.players);
    });
    d3.json("/v1/api/points", function (json) {
        draw_points(json.points);
    });
    setTimeout(refresh_game, 100);
}

refresh_game()

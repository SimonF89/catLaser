var svg = document.getElementById("playground");

console.log(points[2]['fields']['x']);

for (i = 0; i < points.length; i++) {
    drawPoint(points[i]['fields']['x'], points[i]['fields']['y']);
    console.log(points[i] + "" + points[i]['fields']['x'] + "  " + points[i]['fields']['y']);
}

function drawPoint(x, y) {
    var color = getRandomColor();
    svg.innerHTML += '<circle cx="' + x + '" cy="' + y + '" r="40" stroke="' + color + '" stroke-width="3" fill="red" />';
}

var color = getRandomColor();
container.innerHTML = '<line x1="0" y1="0" x2="200" y2="200" style="stroke:' + color + ';stroke-width:2" />Sorry, your browser does not support inline SVG.';

function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}
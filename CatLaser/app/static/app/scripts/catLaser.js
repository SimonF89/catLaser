var tmp = playgrounds.replace(/&#39;/gm, '"').replace(/False/gm, 'false').replace(/True/gm, 'true');
playgrounds = JSON.parse(tmp);
var svg = document.getElementById("playground");
var svgContainer = document.getElementById("canvasContainer");
var pointsContainer = document.getElementById("pointsContainer");
var svgScale;
var id = 0;
for (i = 0; i < playgrounds.length; i++) {
    if (playgrounds[i].active === true) {
        id = i;
    }
}
var activePlayground = playgrounds[id];
svgScale = resizeSVG(svg, activePlayground["minX"], activePlayground["maxX"], activePlayground["minY"], activePlayground["maxY"]);
DrawPlayground(activePlayground);

window.onresize = function (event) {
    redrawSVG();
};

//////////////////////////////////////////////////////////////////////////////
/////////////////////////////  SVG-Drawing  //////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

function redrawSVG() {
    svgScale = resizeSVG(svg, activePlayground["minX"], activePlayground["maxX"], activePlayground["minY"], activePlayground["maxY"]);
    svg.innerHTML = "";
    DrawPlayground(activePlayground);
}

function resizeSVG(svg, minX, maxX, minY, maxY) {
    var x = svgContainer.offsetWidth - 30;
    var y = x * 0.7;
    svg.style.width = x;
    svg.style.height = y;
    pointsContainer.style.maxHeight = (y + 50) + "px";
    // calc scale and offset for SVG
    offsetX = -minX;
    offsetY = -minY;
    scaleX = (maxX - minX) / x;
    scaleY = (maxY - minY) / y;
    return [offsetX, offsetY, scaleX, scaleY];
}

function DrawPlayground(playground) {
    for (i = 0; i < playground['edges'].length; i++) {
        var edges = playground['edges'];
        var edge = edges[i];
        if (!edge.color) {
            edge.color = getRandomColor();
        }
        svg.innerHTML += getSvgLine(edge.A.x, edge.A.y, edge.B.x, edge.B.y, edge.color);
    }
    for (i = 0; i < playground['run_points'].length; i++) {
        var run_points = playground['run_points'];
        var run_point = run_points[i];
        svg.innerHTML += getSvgCircle(run_point.x, run_point.y, "black", "red");
    }
    if (currentPos) {
        svg.innerHTML += getSvgCircle(currentPos.x, currentPos.y, "black", "black");
    }
    if (SimulationTargets) {
        for (i = 0; i < SimulationTargets.length; i++) {
            svg.innerHTML += getSvgCircle(SimulationTargets[i].x, SimulationTargets[i].y, "silver", "yellow");
        }
    }
}

function getSvgLine(x1, y1, x2, y2, color) {
    var Xoff = svgScale[0];
    var Yoff = svgScale[1];
    var Xscale = svgScale[2];
    var Yscale = svgScale[3];
    x1 = (x1 + Xoff) / Xscale;
    x2 = (x2 + Xoff) / Xscale;
    y1 = (y1 + Yoff) / Yscale;
    y2 = (y2 + Yoff) / Yscale;
    return '<line x1=' + x1 + ' y1=' + y1 + ' x2=' + x2 + ' y2=' + y2 + ' style="stroke:' + color + ';stroke-width:2" />';
}

function getSvgCircle(x1, y1, stroke, fill) {
    color = getRandomColor();
    var Xoff = svgScale[0];
    var Yoff = svgScale[1];
    var Xscale = svgScale[2];
    var Yscale = svgScale[3];
    x1 = (x1 + Xoff) / Xscale;
    y1 = (y1 + Yoff) / Yscale;
    return '<circle cx=' + x1 + ' cy=' + y1 + ' r="10" stroke=' + stroke + ' stroke-width="3" fill=' + fill + ' />';
}

function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

//////////////////////////////////////////////////////////////////////////////
////////////////////////////  Update-Status  /////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

var data_url = document.getElementById("link_from_django_to_js").getAttribute("change_status_url");

function draw(element) {
    started = false;
    var name = element.getAttribute("data");
    for (i = 0; i < playgrounds.length; i++) {
        if (playgrounds[i].name === name) {
            id = i;
            playgrounds[i]["active"] = false;
        }
    }
    activePlayground = playgrounds[id];
    redrawSVG(svg, activePlayground);
}

function setActive(element) {
    started = false;
    var name = element.getAttribute("data");
    for (i = 0; i < playgrounds.length; i++) {
        if (playgrounds[i].name === name) {
            id = i;
            playgrounds[i]["active"] = false;
        }
    }
    ajaxPOST(playgrounds[id].name);
    activePlayground = playgrounds[id];
    activePlayground["active"] = true;
    resetSimulation();
}

function ajaxPOST(name) {
    $.ajax({
        type: 'POST',
        url: data_url,
        data: { 'playground_name':name },
        dataType: 'json',
        success: function (result) { return result; },
        error: function (result) {
            alert("error occurred on DAM4KMU-ajax-request, with following data: " + JSON.stringify({ 'playground_name': name }));
            return null;
        }
    });
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////  Simulation  //////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

// TODO calculate maxSpeed from activePlayground.Laser.z and max-Alpha of Servo
// TODO calculate maxSpeed from activePlayground.Laser.z and max-Alpha of Servo
// TODO calculate maxSpeed from activePlayground.Laser.z and max-Alpha of Servo
var maxSpeed = 400;                         // mm per second
var started = false;
var updateRate = 20;                        // millis
var minMaxSpeed = [1000, 5000];           // mm per second per axis!
var featureID = 0;
var minMaxFeatureDuration = [1000, 3000];  // millis
var featureDuration = 0;                    // millis
var eventProbability = 80;                  // %
var eventID = null;
var minMaxEventDuration = [500, 5000];      // millis
var eventDuration = 0;                      // millis
var SimulationTargets = [];
var tmpTargets = [];
var SimulationCurrentSpeed = 10;                       // mm per second
var initPosition = { 'x': 20, 'y': 20, 'speed': SimulationCurrentSpeed, 'OnOff': true };
var currentPos = initPosition;
var TmpCurrentPos = initPosition;
var arrived = false;

function resetSimulation() {
    SimulationCurrentSpeed = 10;
    SimulationTargets = [];
    tmpTargets = [];
    currentPos = initPosition;
    arrived = false;

    if (activePlayground.maxX > activePlayground.maxY) {
        if (activePlayground.maxY > maxSpeed) {
            minMaxSpeed = [maxSpeed / 5, maxSpeed];
        }
        else {
            minMaxSpeed = [activePlayground.maxY / 10, activePlayground.maxY / 2];
        }
    }
    resetEventValues();
    resetFeatureValues();
    redrawSVG(svg, activePlayground);
}

window.setInterval(function () {
    if (started) {
        console.log("featureID: " + featureID);
        console.log("eventID: " + eventID);
        console.log("featureDuration: " + featureDuration);
        console.log("eventDuration: " + eventDuration);
    }
}, 2000);

window.setInterval(function () {
    if (started) {
        if (activePlayground["active"] !== true) {
            started = false;
            alert("current Playground not active!");
        }
        else {
            if (SimulationTargets.length <= 1) {
                var newPoint = calcNextPoint();
                if (Array.isArray(newPoint)) {
                    SimulationTargets.concat(newPoint);
                }
                else {
                    SimulationTargets.push(newPoint);
                }
                arrived = false;
            }
            if (SimulationTargets.length > 1) {
                if (arrived) {
                    SimulationTargets.shift(); // pops first element (currentTarget)
                    // according to eventProbability a Event happens on currentTarget-Point, if no other event is running atm.
                    if (getRndInteger(0, 100) < eventProbability && eventDuration <= 0) {
                        eventID = 0; //getRndInteger(0, 7);
                        SimulationCurrentSpeed = getRndInteger(minMaxSpeed[0], minMaxSpeed[1]);
                        eventDuration = getRndInteger(minMaxFeatureDuration[0], minMaxFeatureDuration[1]);
                        /////////////////// DEBUG
                        /////////////////// DEBUG
                        console.log("calculating new points for Event: " + eventID);
                        /////////////////// DEBUG
                        /////////////////// DEBUG
                        // save current status of current Targets and position
                        tmpTargets = SimulationTargets;
                        TmpCurrentPos = currentPos;
                        var newPoint = calcNextEventPoint(eventID);
                        if (Array.isArray(newPoint)) {
                            SimulationTargets = SimulationTargets.concat(newPoint);
                        }
                        else {
                            SimulationTargets.push(newPoint);
                        }
                        SimulationTargets.push(currentPos);
                        SimulationTargets = SimulationTargets.concat(tmpTargets);
                    }
                    arrived = false;
                }
                SimulationCurrentSpeed = SimulationTargets[0].speed;
                currentPos = goTowardsNextTarget();
                redrawSVG();
                arrived = arrivedTarget();
            }
        }
    }
    if (eventDuration >= 0) {
        eventDuration = eventDuration - updateRate;
    }
    else {
        if (featureDuration >= 0) {
            featureDuration = featureDuration - updateRate;
        }
    }
}, updateRate);

function goTowardsNextTarget() {
    var target = SimulationTargets[0];
    var DirX = target.x - currentPos.x;
    var DirY = target.y - currentPos.y;
    DirX = DirX / Math.sqrt(Math.pow(DirX, 2) + Math.pow(DirY, 2));
    DirY = DirY / Math.sqrt(Math.pow(DirX, 2) + Math.pow(DirY, 2));
    if (isNaN(DirX)) {
        DirX = 0;
    }
    if (isNaN(DirY)) {
        DirY = 0;
    }
    //svgScale = [offsetX, offsetY, scaleX, scaleY]
    var x = currentPos.x + DirX * SimulationCurrentSpeed / 1000 * updateRate / svgScale[2];
    var y = currentPos.y + DirY * SimulationCurrentSpeed / 1000 * updateRate / svgScale[3];
    var newPoint = { 'x': x, 'y': y, 'speed': SimulationCurrentSpeed, 'OnOff': true };
    //console.log("currentPos: " + JSON.stringify(currentPos) + ", \ncurrentTarget: " + JSON.stringify(target) + ", \nDirX: " + DirX + ", \nDirY: " + DirY + ", \nnew x: " + x + ", \nnew y: " + y + ", \nnewPoint: " + JSON.stringify(newPoint));
    return newPoint;
}

function arrivedTarget() {
    var target = SimulationTargets[0];
    var tol = SimulationCurrentSpeed / 1000 * updateRate / 3; // adjust the 1 if it works overruns the Target
    var xmin = currentPos.x - tol;
    var xmax = currentPos.x + tol;
    var ymin = currentPos.y - tol;
    var ymax = currentPos.y + tol;
    if (xmin <= target.x && target.x <= xmax && ymin <= target.y && target.y <= ymax) {
        return true;
    }
    else {
        return false;
    }
}

function StartSimulation(boolstart) {
    if (activePlayground["active"] === true) {
        if (boolstart) {
            started = true;
        }
        else {
            started = false;
        }
    }
    else {
        started = false;
        alert("current Playground not active!");
    }
}

function getRndInteger(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function calcNextPoint() {
    if (featureDuration > 0) {
        return calcNextFeaturePoint(featureID);
    }
    else { // eventDuration <= 0 && featureDuration <= 0
        var newPoint;
        resetFeatureValues();
        var min = 0;
        if (activePlayground["run_points"].length <= 0) {
            var min = 1;  // ignores all Features with runpoints
        }
        featureID = getRndInteger(min, 1);
        SimulationCurrentSpeed = getRndInteger(minMaxSpeed[0], minMaxSpeed[1]);
        featureDuration = getRndInteger(minMaxFeatureDuration[0], minMaxFeatureDuration[1]);
        newPoint = calcNextFeaturePoint(featureID);
        // catch errors in new Point-Calculation
        if (newPoint.x > activePlayground.maxX || newPoint.y > activePlayground.maxY) {
            newPoint = initPosition;
            alert("feature: " + featureID + ", generated a not valid Target!");
        }
        return newPoint;
    }
}

//////////////////////////////////////////////////////////////////////////////
///////////////////////////////  Features  ///////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

function calcNextFeaturePoint(_featureID) {
    switch (_featureID) {
        case 0: return FeatureABC();
        case 1: return FeatureZickZack();
        case 2: return FeatureEdgeRun();

        default: return FeatureABC();
    }
}

var ABCcounter = -1;
var ABCstep = 1;
function FeatureABC() {
    var run_points = activePlayground["run_points"];
    if (run_points.length === 0) {
        featureDuration = 0;
        alert("no Run-Points defined! Simulation stoped!");
        started = false;
        return currentPos;
    }
    else {
        ABCcounter = ABCcounter + ABCstep;
        if (ABCcounter >= run_points.length) {
            ABCstep = -ABCstep;
            ABCcounter = ABCcounter + ABCstep;
        }
        else if (ABCcounter < 0) {
            ABCstep = -ABCstep;
            ABCcounter = ABCcounter + ABCstep;
        }
        return { 'x': run_points[ABCcounter].x, 'y': run_points[ABCcounter].y, 'speed': SimulationCurrentSpeed, 'OnOff': true };
    }
}

var ZickZackcurrentDir = { 'x': 1, 'y': 1 };
function FeatureZickZack() {
    var edges = activePlayground['edges'];
    var M;
    if (SimulationTargets.length > 0) {
        M = SimulationTargets[SimulationTargets.length - 1];
    }
    else {
        M = currentPos;
    }
    var Dir = ZickZackcurrentDir;
    // calculate all hits of 2D Raycast with edges
    // AND calculate the distance to nearest edge (shortestDistance)
    var shortestDistance = 1000000;
    for (i = 0; i < edges.length; i++) {
        var _x = M.x + Dir.x * 1000000;
        var _y = M.y + Dir.y * 1000000;
        var pointer = { 'x': _x, 'y': _y };
        var P = get_line_intersection(M, pointer, edges[i].A, edges[i].B);

        if (P.x !== -6666 && P.y !== -6666) {
            var distance = Math.sqrt(Math.pow(M.x - P.x, 2) + Math.pow(M.y - P.y, 2));
            if (distance < shortestDistance) {
                shortestDistance = distance;
            }
        }
    }
    // catch error - if shortestDistance is still the init value, something went wrong!
    if (shortestDistance === 1000000) {
        alert("something went wrong in FeatureZickZack.");
        return currentPos;
        // if this happens, maybe the currentPos wasent in the Playground anymore!
    }
    // calculate new Position according to Dir and distance to next edge (shortestDistance)
    var offset = getRndInteger(shortestDistance / 20, shortestDistance);
    var DirAbs = Math.sqrt(Math.pow(Dir.x, 2) + Math.pow(Dir.y, 2));
    var factor = (shortestDistance - offset) / DirAbs;
    var newX = M.x + Dir.x * factor;
    var newY = M.y + Dir.y * factor;

    // rotate Dir Vector Randomly
    var randomX = getRndInteger(-100, 100) / 100;
    var randomY = getRndInteger(-100, 100) / 100;
    ZickZackcurrentDir = { 'x': randomX, 'y': randomY };

    return { 'x': newX, 'y': newY, 'speed': SimulationCurrentSpeed, 'OnOff': true };
}

function FeatureEdgeRun() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentSpeed, 'OnOff': true }
}

// will be executed after a new Playground is loaded
function resetFeatureValues() {
    ABCcounter = -1;
    ABCstep = 1;
}

//////////////////////////////////////////////////////////////////////////////
////////////////////////////////  Events  ////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

function calcNextEventPoint(_eventID) {
    switch (_eventID) {
        case 0: return EventCircle();
        case 1: return EventSinCos();
        case 2: return EventBlink();
        case 3: return EventStandStill();
        case 4: return EventWollkneul();
        case 5: return EventForwardBackward();
        default: // EventGoOn()
            eventDuration = 0;
            return currentPos;
    }
}

function EventCircle() {
    var Resolution = 20;
    var CircleMaxRadius = 200;
    var CircleRadius = getRndInteger(50, CircleMaxRadius);
    var CircleRotFactor = getRndInteger(10, 20);        // Between 1 and 2 rotations per second with factor 10 cause its an integer
    var TimeSteps = eventDuration * CircleRotFactor / Resolution;
    var AngleSteps = 360 / Resolution;

    var newPoints = [];
    var newX = 0, newY = 0, angle = 0, t = 0;
    while (t < eventDuration) {
        newX = CircleRadius * Math.cos(toRadians(angle));
        newY = CircleRadius * Math.sin(toRadians(angle));
        var x = TmpCurrentPos.x + newX;
        var y = TmpCurrentPos.y + newY;
        newPoints.push({ 'x': x, 'y': y, 'speed': SimulationCurrentSpeed, 'OnOff': true });
        angle = angle + AngleSteps;
        if (angle > 360) {
            angle = angle - 360;
        }
        t = t + TimeSteps;
    }
    return newPoints;
}

// generates two mirrored sinus on each side of the y-axis along the x-axis
function EventSinCos() {
    var ArcLengthSinPerPi = 3.82019;
    var SinCosResolution = 20;
    var SinCosMaxRadius = 200;     // mm
    var SinCosRadius = getRndInteger(50, SinCosMaxRadius);     // mm
    var SinCosCurrentAngle = 0;
    var stepsT = (SinCosRadius / SinCosResolution) / SimulationCurrentSpeed;
    var stepsX = SinCosRadius / SinCosResolution;

    var newPoints = [];
    var newX = 0, tmpX = 0, newY = 0, t = 0;
    while (t < eventDuration) {
        tmpX = tmpX + stepsX;
        if (tmpX >= 4 * SinCosRadius) {
            tmpX = 0
        }
        if (tmpX <= SinCosRadius || 3 * SinCosRadius < tmpX && tmpX < 4 * SinCosRadius) {
            newY = Math.sin(tmpX / SinCosRadius * Math.PI);
            newX = tmpX;
        }
        else {
            newY = - Math.sin((tmpX - SinCosRadius) / SinCosRadius * Math.PI);
            newX = SinCosRadius - tmpX;
        }
        var x = TmpCurrentPos.x + newX;
        var y = TmpCurrentPos.y + newY;
        newPoints.push({ 'x': x, 'y': y, 'speed': SimulationCurrentSpeed, 'OnOff': true });
        t = t + stepsT;
    }
    return newPoints;
}

function EventBlink() {
    eventDuration = 0;
    return currentPos; // { 'x': x, 'y': y, 'speed': currentSpeed, 'OnOff': true };
}

function EventStandStill() {
    eventDuration = 0;
    return currentPos; // { 'x': x, 'y': y, 'speed': currentSpeed, 'OnOff': true };
}

function EventWollkneul() {
    eventDuration = 0;
    return currentPos; // { 'x': x, 'y': y, 'speed': currentSpeed, 'OnOff': true };
}

function EventForwardBackward() {
    eventDuration = 0;
    return currentPos; // { 'x': x, 'y': y, 'speed': currentSpeed, 'OnOff': true };
}

// will be executed after a new Playground is loaded
function resetEventValues() {

}

/////////////////////// Features-Events-Functions  ///////////////////////////

function get_line_intersection(A1, A2, B1, B2) {
    var a = A2.y - A1.y;
    var b = -B2.y + B1.y;
    var c = A2.x - A1.x;
    var d = -B2.x + B1.x;
    var C1 = B1.y - A1.y;
    var C2 = B1.x - A1.x;

    var tmp = a * d - b * c;
    if (tmp) {
        var invMa = d / tmp;
        var invMb = -b / tmp;
        var invMc = -c / tmp;
        var invMd = a / tmp;

        var m = invMa * C1 + invMb * C2;
        var n = invMc * C1 + invMd * C2;
        if (0 <= m && m <= 1 && 0 <= n && n <= 1) {
            var x = A1.x + m * (A2.x - A1.x);
            var y = A1.y + m * (A2.y - A1.y);
            return { 'x': x, 'y': y};
        }
        else {
            return { 'x': -6666, 'y': -6666};
        }
    }
    else {
        return { 'x': -6666, 'y': -6666};
    }
}

function toRadians(angle) {
    return angle * (Math.PI / 180);
}







////////////////////////// MUST BE FIXED!!!
////////////////////////// MUST BE FIXED!!!
////////////////////////// MUST BE FIXED!!!
function EventSpiral() {
    var CircleMaxRadius = 2000;         // mm
    var CircleMaxSpeed = 1000;          // mm per second
    var CircleMaxSpirals = 3;
    var CircleResolution = 30;

    var AngleSteps = 360 / CircleResolution;
    var stepR = CircleMaxRadius / (CircleResolution * CircleMaxSpirals);
    var currentR = 0;
    var t = 0;
    var newPoints = [];
    var newX, newY;
    var currentAngle = 0;
    var newPos = currentPos;
    while (t < eventDuration) {
        currentR = currentR + stepR;
        if (currentR > CircleMaxRadius) {
            stepR = -stepR;
            currentR = currentR + stepR;
        }
        if (currentR <= 0) {
            stepR = -stepR;
            currentR = currentR + stepR;
        }
        newX = currentR * Math.sin(toRadians(currentAngle));
        newY = currentR * Math.cos(toRadians(currentAngle));
        currentAngle = currentAngle + AngleSteps;
        // add new point to array
        var A = newPos;
        var x = TmpCurrentPos.x + newX;
        var y = TmpCurrentPos.y + newY;
        newPos = { 'x': x, 'y': y, 'speed': SimulationCurrentSpeed, 'OnOff': true };
        var B = newPos;
        newPoints.push(newPos);
        // calc passed time to arrive to new point
        var distance = Math.sqrt(Math.pow(B.x - A.x, 2) + Math.pow(B.y - A.y, 2));
        t = t + distance / SimulationCurrentSpeed;
    }
    return newPoints;
}
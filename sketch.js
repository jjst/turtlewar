var colors = [
    [0, 0, 0],
    [255, 255, 255],
    [255, 0, 0],
    [0, 255, 0],
    [0, 0, 255],
    [0, 255, 255],
    [255, 0, 255],
    [255, 255, 0]
];

var instructions = [
    ["down"],
    ["color", 7],
    ["forward", 200],
    ["rotate", 90],
    ["color", 4],
    ["forward", 200],
    ["rotate", 90],
    ["color", 2],
    ["forward", 200],
    ["rotate", 30],
    ["color", 3],
    ["forward", 200],
];

var penDown = false;
var currentColor = colors[0];
var transforms = [];

function setup() {
    createCanvas(
        windowWidth,
        windowHeight
    );
    var initialPosition = {
        x: windowWidth / 2, 
        y: windowHeight / 2
    };
    transforms.push(["translate", initialPosition.x, initialPosition.y]);
    background(0, 0, 0);
    angleMode(DEGREES);
}

function draw() {
    if(instructions.length == 0) {
        return;
    }
    applyTransforms(transforms);
    stroke(currentColor);
    var [command, value] = instructions.shift();
    switch(command) {
        case "color":
            currentColor = colors[value];
            break;
        case "down":
            penDown = true;
            break;
        case "up":
            penDown = false;
            break;
        case "rotate":
            transforms.push(["rotate", value]);
            break;
        case "forward":
            transforms.push(["translate", value + 1, 0]);
            if(penDown) {
                line(0, 0, value, 0);
            }
            break;
    }
}

function applyTransforms(transforms) {
    transforms.forEach(function(transform) {
        var transform = transform.slice();
        transformType = transform.shift();
        switch(transformType) {
            case "rotate":
                var [angle] = transform;
                rotate(angle);
                break;
            case "translate":
                var [x, y] = transform;
                translate(x, y);
                break;
        }
    });
}

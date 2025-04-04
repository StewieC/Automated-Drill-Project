// Pin definitions for DC motor
const int enA = 7;  // PWM pin for speed control
const int in1 = 6;  // Direction pin 1
const int in2 = 5;  // Direction pin 2

// Motor control variable
int speed = 0;

void setup() {
    Serial.begin(9600);      // Start serial communication
    pinMode(enA, OUTPUT);
    pinMode(in1, OUTPUT);
    pinMode(in2, OUTPUT);
    digitalWrite(in1, LOW);  // Default state
    digitalWrite(in2, LOW);
    Serial.println("DC Motor Control Ready");
    Serial.println("Commands: 'start', 'stop', 'speed X' (X = 0-255)");
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        command.trim();  // Remove whitespace
        handleCommand(command);
    }
    runDCMotor(speed);  // Continuously run motor at set speed
}

void handleCommand(String command) {
    Serial.println("Received: " + command);
    if (command == "start") {
        speed = 255;  // Full speed
        Serial.println("Motor started at speed 255");
    } else if (command == "stop") {
        speed = 0;
        Serial.println("Motor stopped");
    } else if (command.startsWith("speed ")) {
        int newSpeed = command.substring(6).toInt();
        if (newSpeed >= 0 && newSpeed <= 255) {
            speed = newSpeed;
            Serial.println("Speed set to: " + String(speed));
        } else {
            Serial.println("Invalid speed. Use 0-255.");
        }
    } else {
        Serial.println("Unknown command. Use 'start', 'stop', or 'speed X'");
    }
}

void runDCMotor(int speed) {
    if (speed > 0) {
        digitalWrite(in1, LOW);   // Forward direction
        digitalWrite(in2, HIGH);
        analogWrite(enA, speed);  // Set speed via PWM
    } else {
        digitalWrite(in1, LOW);   // Stop
        digitalWrite(in2, LOW);
        analogWrite(enA, 0);
    }
}
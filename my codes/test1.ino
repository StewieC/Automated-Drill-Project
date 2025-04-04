// Pin definitions for DC motor
const int enA = 7;    // PWM pin for speed control
const int in1 = 6;    // Direction pin 1
const int in2 = 5;    // Direction pin 2

// Pin definitions for stepper motor
const int stepPin = 3;  // Step signal
const int dirPin = 4;   // Direction signal
const int enPin = 9;    // Enable pin (LOW to enable)

// Motor control variables
int dcSpeed = 0;         // DC motor speed (0-255)
int stepDelay = 1000;    // Stepper delay in microseconds (500-5000)
bool motorsRunning = false;  // Shared running state

void setup() {
    Serial.begin(9600);
    
    // DC motor setup
    pinMode(enA, OUTPUT);
    pinMode(in1, OUTPUT);
    pinMode(in2, OUTPUT);
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
    
    // Stepper motor setup
    pinMode(stepPin, OUTPUT);
    pinMode(dirPin, OUTPUT);
    pinMode(enPin, OUTPUT);
    digitalWrite(enPin, LOW);  // Enable stepper driver
    digitalWrite(dirPin, LOW); // Fixed forward direction
    
    Serial.println("Dual Motor Control Ready");
    Serial.println("Commands: 'start', 'stop', 'dc_speed X' (X = 0-255), 'step_speed X' (X = 500-5000 us)");
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        handleCommand(command);
    }
    
    if (motorsRunning) {
        runDCMotor(dcSpeed);
        runStepperMotor();
        Serial.println("DC_SPEED:" + String(dcSpeed) + ",STEP_RUNNING:1");
    } else {
        runDCMotor(0);  // Stop DC motor
        Serial.println("DC_SPEED:0,STEP_RUNNING:0");
    }
    delay(10);  // Control feedback rate
}

void handleCommand(String command) {
    Serial.println("Received: " + command);
    if (command == "start") {
        motorsRunning = true;
        if (dcSpeed == 0) dcSpeed = 255;  // Default DC speed if not set
        Serial.println("Motors started");
    } else if (command == "stop") {
        motorsRunning = false;
        Serial.println("Motors stopped");
    } else if (command.startsWith("dc_speed ")) {
        int newSpeed = command.substring(9).toInt();
        if (newSpeed >= 0 && newSpeed <= 255) {
            dcSpeed = newSpeed;
            Serial.println("DC speed set to: " + String(dcSpeed));
        } else {
            Serial.println("Invalid DC speed. Use 0-255.");
        }
    } else if (command.startsWith("step_speed ")) {
        int newSpeed = command.substring(11).toInt();
        if (newSpeed >= 500 && newSpeed <= 5000) {
            stepDelay = newSpeed;
            Serial.println("Step delay set to: " + String(stepDelay) + " us");
        } else {
            Serial.println("Invalid step speed. Use 500-5000 us.");
        }
    } else {
        Serial.println("Unknown command. Use 'start', 'stop', 'dc_speed X', 'step_speed X'");
    }
}

void runDCMotor(int speed) {
    if (speed > 0) {
        digitalWrite(in1, LOW);   // Forward direction
        digitalWrite(in2, HIGH);
        analogWrite(enA, speed);  // Set speed via PWM
    } else {
        digitalWrite(in1, LOW);
        digitalWrite(in2, LOW);
        analogWrite(enA, 0);
    }
}

void runStepperMotor() {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(stepDelay);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(stepDelay);
}
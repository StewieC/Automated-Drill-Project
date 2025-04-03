// Pin definitions
const int limitSwitchPin = 2;
const int stepPin = 3;
const int dirPin = 4;
const int enPin = 9;
const int enA = 7;
const int in1 = 6;
const int in2 = 5;

// Motor control variables
int dcSpeed = 0;              // DC motor speed (0-255)
int stepperFeedRate = 5000;   // Stepper delay in microseconds (default slow)
bool motorRunning = false;    // Controls whether motors are running
bool checkstop = false;       // Emergency stop flag
int currentPosition = 0;      // Stepper position

// Stepper motor feed rates
const int stepperDelayHigh = 1000;  // Faster feed rate
const int stepperDelayLow = 5000;   // Slower feed rate

// Setup serial communication
void setup() {
  Serial.begin(9600);
  pinMode(enA, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(enPin, OUTPUT);
  digitalWrite(enPin, LOW);
  pinMode(limitSwitchPin, INPUT_PULLUP);
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);

  Serial.println("Arduino Ready");
  while (!Serial.available() || Serial.readStringUntil('\n') != "Python Ready") {
    delay(100);
  }
}

void loop() {
  int limitSwitchState = digitalRead(limitSwitchPin);

  // Check for emergency stop
  checkSerialForEmergencyStop();

  // Process serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    handleCommand(command);
  }

  // Run both motors simultaneously if running
  if (motorRunning) {
    runDCMotor(dcSpeed);        // Run DC motor
    runStepperMotor(1);         // Run stepper motor (1 step per loop)
  }

  // Limit switch handling
  if (limitSwitchState == HIGH) {
    handleLimitSwitch();
  }

  // Feedback to Python
  Serial.println("CURRENT SPEED:" + String(dcSpeed));
  Serial.println("CURRENT POSITION:" + String(currentPosition));
}

void checkSerialForEmergencyStop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "stopmachine") {
      emergencyStop();
    }
  }
}

void handleCommand(String command) {
  if (command == "stopmachine") {
    emergencyStop();
    Serial.println("STOPPED");
  } else if (command.startsWith("setSpeed")) {
    int newSpeed = command.substring(8).toInt();
    if (newSpeed >= 0 && newSpeed <= 255) {
      dcSpeed = newSpeed;
      Serial.println("DC SPEED SET TO: " + String(dcSpeed));
    } else {
      Serial.println("Invalid speed. Please enter a value between 0 and 255.");
    }
  } else if (command == "slowdrill") {
    dcSpeed = 100;
    Serial.println("DC SPEED SET TO 100 (Slow drill mode)");
  } else if (command == "fastdrill") {
    dcSpeed = 255;
    Serial.println("DC SPEED SET TO 255 (Fast drill mode)");
  } else if (command == "highFeedRate") {
    stepperFeedRate = stepperDelayHigh;
    Serial.println("Stepper High Feed Rate selected.");
  } else if (command == "slowFeedRate") {
    stepperFeedRate = stepperDelayLow;
    Serial.println("Stepper Slow Feed Rate selected.");
  } else if (command == "start") {
    if (dcSpeed > 0) {  // Ensure a valid speed is set
      motorRunning = true;
      Serial.println("Machine Started");
    } else {
      Serial.println("Error: Set DC motor speed before starting.");
    }
  }
}

void emergencyStop() {
  analogWrite(enA, 0);      // Stop DC motor
  digitalWrite(enPin, HIGH); // Disable stepper motor
  dcSpeed = 0;
  motorRunning = false;
  checkstop = true;
}

void runDCMotor(int speed) {
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  analogWrite(enA, speed);  // Set DC motor speed via PWM
}

void runStepperMotor(int steps) {
  digitalWrite(dirPin, LOW);
  digitalWrite(enPin, LOW);
  for (int i = 0; i < steps; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(stepperFeedRate);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(stepperFeedRate);
    currentPosition++;
  }
}

void handleLimitSwitch() {
  motorRunning = false;  // Stop motors when limit switch is triggered
  for (int m = 0; m < 5 && !checkstop; m++) {
    for (int i = 0; i < 600 && !checkstop; i++) {
      digitalWrite(dirPin, HIGH);
      digitalWrite(enPin, LOW);
      digitalWrite(stepPin, HIGH);
      delayMicroseconds(stepperFeedRate);
      digitalWrite(stepPin, LOW);
      delayMicroseconds(stepperFeedRate);
      currentPosition++;
      checkSerialForEmergencyStop();
    }
  }
}
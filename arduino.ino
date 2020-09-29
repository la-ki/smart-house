#include <LiquidCrystal.h>

const int rs = 12;
const int en = 11;
const int d4 = 5;
const int d5 = 4;
const int d6 = 3;
const int d7 = 2;

LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
int trig = 9;
int echo = 10;

void setup() {
    analogReference(INTERNAL);
    Serial.begin(9600);
    pinMode(trig, OUTPUT);
    pinMode(echo, INPUT);
    lcd.begin(16, 2);
    lcd.clear();
}

void loop() {
    razdaljina();
    temperatura();
    svetlost();

    delay(500);

    lcd.setCursor(1, 0);
    lcd.print("Poslednja konf.");

    if (Serial.available()) {
        delay(100);
        while(Serial.available() > 0) {
            char vreme = Serial.read();
            lcd.setCursor(0, 1);
            lcd.while(vreme);
        }
    }
}

float temperatura() {
    float temp;
    float reading;
    int tempPin = A1;

    reading = analogRead(tempPin);
    temp = reading/9.31;

    Serial.println(temp);
}

int svetlost() {
    int svetlostPin = A0;
    int svetlostCitanje;

    svetlostCitanje = analogRead(svetlostPin);

    Serial.println(svetlostCitanje);
}

int razdaljina() {
    long trajanje;

    int razdaljinaCM;

    digitalWrite(trig, LOW);
    delayMicroseconds(2);
    digitalWrite(trig, HIGH);
    delayMicroseconds(10);
    digitalWrite(trig, LOW);

    trajanje = pulseIn(echo, HIGH);
    razdaljinaCM = trajanje*0.034/2;
    Serial.println(razdaljinaCM);
}
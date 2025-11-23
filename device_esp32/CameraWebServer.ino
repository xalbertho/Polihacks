#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

// ===========================
// Select camera model in board_config.h
// ===========================
#include "board_config.h"

// ===========================
// WiFi credentials
// ===========================
const char *ssid = "Pixel_1685";
const char *password = "12345678";

// ===========================
// Servidor al que mandaremos la foto
// (por ejemplo, un Flask en tu PC)
// ===========================
const char* serverUrl = "http://192.168.0.100:5000/upload"; // <-- CAMBIA ESTO

// ========= SENSOR CAPACITIVO ==========
// GPIO 12 corresponde al touch pad T5
#define TOUCH_PIN        T5          // GPIO 12
#define TOUCH_MARGIN     10          // diferencia baseline - threshold (MENOR = más sensible)

uint16_t touchBaseline = 0;
uint16_t touchThreshold = 0;

void startCameraServer();
void setupLedFlash();

// ===========================
// Calibrar touch al inicio
// ===========================
void calibrateTouch()
{
  const int samples = 50;
  uint32_t sum = 0;

  Serial.println("Calibrando touch... no toques el sensor!");

  for (int i = 0; i < samples; i++) {
    uint16_t v = touchRead(TOUCH_PIN);
    sum += v;
    delay(20);
  }

  touchBaseline = sum / samples;
  // Threshold = baseline - margen
  touchThreshold = (touchBaseline > TOUCH_MARGIN) ? (touchBaseline - TOUCH_MARGIN) : 5;

  Serial.printf("Touch calibrado. Baseline=%u, Threshold=%u (margin=%d)\n",
                touchBaseline, touchThreshold, TOUCH_MARGIN);
  Serial.println("Ahora sí, toca el sensor para disparar foto.");
}

// ===========================
// Enviar foto al servidor
// ===========================
void sendPhotoToServer(uint8_t *data, size_t len)
{
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi no conectado, no se puede enviar la foto.");
    return;
  }

  HTTPClient http;
  Serial.println("Enviando foto al servidor...");

  http.begin(serverUrl); // URL del servidor
  http.addHeader("Content-Type", "image/jpeg");

  int httpCode = http.POST(data, len);

  if (httpCode > 0) {
    Serial.printf("Respuesta del servidor: %d\n", httpCode);
    String payload = http.getString();
    Serial.printf("Payload: %s\n", payload.c_str());
  } else {
    Serial.printf("Error en POST: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}

// ===========================
// Capturar foto al tocar
// ===========================
void takePhotoFromTouch()
{
  Serial.println("Capturando foto por sensor capacitivo...");

  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Error: Fallo en la captura de la cámara");
    return;
  }

  Serial.printf("Foto capturada! Tamaño: %u bytes\n", fb->len);

  // Enviar al servidor
  sendPhotoToServer(fb->buf, fb->len);

#if defined(LED_GPIO_NUM)
  // Pequeño destello de flash para indicar captura (opcional)
  digitalWrite(LED_GPIO_NUM, HIGH);
  delay(100);
  digitalWrite(LED_GPIO_NUM, LOW);
#endif

  // Liberar el frame buffer
  esp_camera_fb_return(fb);
}

// ===========================
// SETUP
// ===========================
void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // ===========================
  // CONFIGURACIÓN DE CÁMARA
  // ===========================
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y4_GPIO_NUM;
  config.pin_d5 = Y5_GPIO_NUM;
  config.pin_d6 = Y6_GPIO_NUM;
  config.pin_d7 = Y7_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;  // para streaming

  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      config.jpeg_quality = 10;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    config.frame_size = FRAMESIZE_240X240;
#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
  }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  // Inicializar cámara
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();

  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);
    s->set_brightness(s, 1);
    s->set_saturation(s, -2);
  }

  if (config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_QVGA);   // puedes subirlo a VGA si aguanta
  }

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif

#if defined(CAMERA_MODEL_ESP32S3_EYE)
  s->set_vflip(s, 1);
#endif

#if defined(LED_GPIO_NUM)
  setupLedFlash();
#endif

  // ===========================
  // WiFi
  // ===========================
  Serial.printf("Conectando a WiFi: %s\n", ssid);
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // Servidor de streaming (si quieres seguir usando la web UI)
  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' para ver el stream");

  // Calibrar touch (más sensible)
  calibrateTouch();
}

// ===========================
// LOOP
// ===========================
void loop() {
  static bool lastTouch = false;

  uint16_t touchValue = touchRead(TOUCH_PIN);
  bool isTouch = (touchValue < touchThreshold);

  // Debug opcional:
  // Serial.printf("touchValue=%u, isTouch=%d\n", touchValue, isTouch);

  if (isTouch && !lastTouch) {
    Serial.printf("TOQUE detectado! touchValue=%u (threshold=%u)\n",
                  touchValue, touchThreshold);
    takePhotoFromTouch();
  }

  lastTouch = isTouch;
  delay(50);
}

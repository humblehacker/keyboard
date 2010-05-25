#ifndef __MATRIX_DISCOVERY_H__
#define __MATRIX_DISCOVERY_H__

extern "C" {
#include <LUFA/Drivers/USB/Class/HID.h>
}

#include "matrix_discovery_defs.h"

class MatrixDiscovery
{
public:
  static MatrixDiscovery &instance() { return _instance; }

  void init();
  uint8_t get_report(USB_KeyboardReport_Data_t *report);
  void hid_puts(const char *str);
  void write_output_char(USB_KeyboardReport_Data_t *report);

private:
  static MatrixDiscovery _instance;
  enum { OUTPUT_BUFSIZE = 128 };
  enum State { LEARN, DISPLAY, AWAITING_INPUT, IDLE } _state;
  char _output_buffer[OUTPUT_BUFSIZE];
  char *_output_end_pos;
  uint8_t _output_current_pos;
};

#endif // __MATRIX_DISCOVERY_H__

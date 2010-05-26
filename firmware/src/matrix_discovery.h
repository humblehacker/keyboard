#ifndef __MATRIX_DISCOVERY_H__
#define __MATRIX_DISCOVERY_H__

extern "C" {
#include <LUFA/Drivers/USB/Class/HID.h>
}

#include "matrix_discovery_defs.h"
#include "hid_usages.h"

class MatrixDiscovery
{
public:
  static MatrixDiscovery &instance() { return _instance; }

  void init();
  uint8_t get_report(USB_KeyboardReport_Data_t *report);
  void scan_matrix();

private:
  void write_output_char(USB_KeyboardReport_Data_t *report);

  void activate_row(int row);
  bool check_column(int col);

private:
  static MatrixDiscovery _instance;
  enum State { LEARN, DISPLAY, AWAITING_INPUT, IDLE } _state;
  bool _send_empty_report;
};

#endif // __MATRIX_DISCOVERY_H__

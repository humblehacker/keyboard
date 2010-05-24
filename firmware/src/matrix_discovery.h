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

  uint8_t get_report(USB_KeyboardReport_Data_t *report);

private:
  static MatrixDiscovery _instance;
};

#endif // __MATRIX_DISCOVERY_H__

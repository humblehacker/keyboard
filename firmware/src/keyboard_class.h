/*
                    The HumbleHacker Keyboard Project
                 Copyright © 2008-2010, David Whetstone
               david DOT whetstone AT humblehacker DOT com

  This file is a part of The HumbleHacker Keyboard Project.

  The HumbleHacker Keyboard Project is free software: you can redistribute
  it and/or modify it under the terms of the GNU General Public License as
  published by the Free Software Foundation, either version 3 of the
  License, or (at your option) any later version.

  The HumbleHacker Keyboard Project is distributed in the hope that it will
  be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
  Public License for more details.

  You should have received a copy of the GNU General Public License along
  with The HumbleHacker Keyboard Project.  If not, see
  <http://www.gnu.org/licenses/>.

*/

#ifndef __KEYBOARD_CLASS_H__
#define __KEYBOARD_CLASS_H__

extern "C" {
#include <LUFA/Drivers/USB/Class/HID.h>
}

#include "matrix.h"
#include "binding.h"
#include "bound_key.h"
#include "active_keys.h"

class Keyboard
{
public:
  static
  Keyboard*  instance();

  void       init();
  uint8_t    get_report(USB_KeyboardReport_Data_t *report);

private:
  void       reset();

  void       scan_matrix();

  uint8_t    fill_report(USB_KeyboardReport_Data_t *report);
  bool       is_processing_macro();

  bool       momentary_mode_engaged();
  bool       modifier_keys_engaged();
  void       check_mode_toggle();
  void       process_keys();
  void       toggle_map(KeyMap mode_map);

  void       update_bindings();
  void       init_active_keys();
  BoundKey*  first_active_key();
  BoundKey*  next_active_key();

private:
  uint32_t                  _row_data[NUM_ROWS];
  uint8_t                   _num_keys;
  ActiveKeys                _active_keys;
  const MacroTarget        *_macro;
  bool                      _error_roll_over;
  KeyMap                    _active_keymap;
  KeyMap                    _current_keymap;
  KeyMap                    _default_keymap;
  USB_KeyboardReport_Data_t _report;
  static Keyboard _instance;
};

#endif // __KEYBOARD_CLASS_H__

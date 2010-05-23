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

#define NUM_MODIFIERS 8
#define MAX_KEYS      6
#define MAX_ACTIVE_CELLS (MAX_KEYS + NUM_MODIFIERS)

class Keyboard
{
public:
  static void      init();
  static void      reset();

  static void      scan_matrix();

  static bool      is_error();
  static uint8_t   fill_report(USB_KeyboardReport_Data_t *report);
  static bool      is_processing_macro();

  static bool      momentary_mode_engaged();
  static bool      modifier_keys_engaged();
  static void      check_mode_toggle();
  static void      process_keys();
  static void      toggle_map(KeyMap mode_map);

  static void      update_bindings();
  static void      init_active_keys();
  static BoundKey* first_active_key();
  static BoundKey* next_active_key();

private:
  static uint32_t  row_data[NUM_ROWS];
  static uint8_t   modifiers;
  static Usage     keys[MAX_KEYS];
  static uint8_t   num_keys;
  static BoundKey  active_keys[MAX_ACTIVE_CELLS];
  static uint8_t   num_active_keys;
  static uint8_t   curr_active_key;
  static const     MacroTarget *macro;
  static bool      error_roll_over;
  static KeyMap    active_keymap;
  static KeyMap    current_keymap;
  static KeyMap    default_keymap;
};

#endif // __KEYBOARD_CLASS_H__

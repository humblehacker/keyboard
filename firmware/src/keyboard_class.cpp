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

#include <string.h>
#include <limits.h>
#include <util/delay.h>

#include "Keyboard.h"
#include "keyboard_class.h"
#include "keymaps.h"
#include "conf_keyboard.h"
#include "binding.c"

static Modifiers get_modifier(Usage usage);

uint32_t           Keyboard::row_data[NUM_ROWS];
uint8_t            Keyboard::modifiers;
Usage              Keyboard::keys[MAX_KEYS];
uint8_t            Keyboard::num_keys;
BoundKey           Keyboard::active_keys[MAX_ACTIVE_CELLS];
uint8_t            Keyboard::num_active_keys;
uint8_t            Keyboard::curr_active_key;
const MacroTarget *Keyboard::macro;
bool               Keyboard::error_roll_over;
KeyMap             Keyboard::active_keymap;
KeyMap             Keyboard::current_keymap;
KeyMap             Keyboard::default_keymap;

void
Keyboard::init()
{
  init_cols();

  default_keymap = (KeyMap) pgm_read_word(&kbd_map_mx_default);
  current_keymap = default_keymap;
  active_keymap = NULL;

  Keyboard::reset();
}

void
Keyboard::reset()
{
  memset(&active_keys[0], UCHAR_MAX, sizeof(active_keys[0])*MAX_ACTIVE_CELLS);
  num_active_keys = 0;

  memset(&keys[0], UCHAR_MAX, sizeof(keys[0])*MAX_KEYS);
  num_keys = 0;

  error_roll_over = false;
  modifiers = NONE;

  active_keymap = current_keymap;
}

bool
Keyboard::is_error()
{
  return error_roll_over;
}

void
Keyboard::scan_matrix()
{
  init_cols();
  for (uint8_t row = 0; row < NUM_ROWS; ++row)
  {
    activate_row(row);

    // Insert NOPs for synchronization
    _delay_us(20);

    // Place data on all column pins for active row into a single
    // 32 bit value.
		row_data[row] = 0;
    row_data[row] = read_row_data();
  }
}

void
Keyboard::update_bindings(void)
{
  for (BoundKey* key = Keyboard::first_active_key();
       key;      key = Keyboard::next_active_key())
  {
    key->update_binding(modifiers, active_keymap);
  }
}


void
Keyboard::init_active_keys()
{
  BoundKey *key = NULL;
  uint8_t ncols;
  // now process row/column data to get raw keypresses
  for (uint8_t row = 0; row < NUM_ROWS; ++row)
  {
    ncols = 0;
    for (uint8_t col = 0; col < NUM_COLS; ++col)
    {
      if (row_data[row] & (1UL << col))
      {
        if (num_active_keys > MAX_ACTIVE_CELLS)
        {
          error_roll_over = true;
          return;
        }
        ++ncols;
        key = &active_keys[num_active_keys++];
        key->reinit(MATRIX_CELL(row, col));
      }
    }

    // if 2 or more keys pressed in a row, check for ghost-key
    if (ncols > 1)
    {
      for (uint8_t irow = 0; irow < NUM_ROWS; ++irow)
      {
        if (irow == row)
          continue;

        // if any other row has a key pressed in the same column as any
        // of the two or more keys pressed in the current row, we have a
        // ghost-key condition.
        if (row_data[row] & row_data[irow])
        {
          error_roll_over = true;
          return;
        }
      }
    }
  }
}

bool
Keyboard::momentary_mode_engaged()
{
  for (BoundKey* key = Keyboard::first_active_key();
       key;      key = Keyboard::next_active_key())
  {
    if (key->binding()->kind == KeyBinding::MODE)
    {
      ModeTarget *target = (ModeTarget*)key->binding()->target;
      if (target->type == ModeTarget::MOMENTARY)
      {
        active_keymap = target->mode_map;
        key->deactivate();
        return true;
      }
    }
  }
  return false;
}

bool
Keyboard::modifier_keys_engaged()
{
  uint8_t active_modifiers = NONE;
  for (BoundKey* key = Keyboard::first_active_key();
       key;      key = Keyboard::next_active_key())
  {
    if (key->binding()->kind == KeyBinding::MAP)
    {
      const MapTarget *target = (const MapTarget*)key->binding()->target;
      Modifiers this_modifier = NONE;
      if ((this_modifier = get_modifier(target->usage)) != NONE)
      {
        active_modifiers |= this_modifier;
        key->deactivate();
      }
    }
  }
  modifiers |= active_modifiers;
  return active_modifiers != NONE;
}

void
Keyboard::toggle_map(KeyMap mode_map)
{
  if (current_keymap == mode_map)
    current_keymap = default_keymap;
  else
    current_keymap = mode_map;
}

void
Keyboard::check_mode_toggle(void)
{
  for (BoundKey* key = Keyboard::first_active_key();
       key;      key = Keyboard::next_active_key())
  {
    if (key->binding()->kind == KeyBinding::MODE)
    {
      ModeTarget *target = (ModeTarget*)key->binding()->target;
      if (target->type == ModeTarget::TOGGLE)
      {
        Keyboard::toggle_map(target->mode_map);
        key->deactivate();
        return;
      }
    }
  }
}

void
Keyboard::process_keys()
{
  for (BoundKey* key = Keyboard::first_active_key();
       key;      key = Keyboard::next_active_key())
  {
    if (key->binding()->kind == KeyBinding::MAP)
    {
      const MapTarget *target = (const MapTarget*)key->binding()->target;
      keys[num_keys] = target->usage;
      modifiers &= ~key->binding()->premods;
      modifiers |= target->modifiers;
      ++num_keys;
    }
  }
}

uint8_t
Keyboard::fill_report(USB_KeyboardReport_Data_t *report)
{
  if (Keyboard::is_error())
  {
    report->Modifier = modifiers;
    for (uint8_t key = 1; key < 7; ++key)
      report->KeyCode[key] = USAGE_ID(HID_USAGE_ERRORROLLOVER);
  }
  else if (!Keyboard::is_processing_macro())
  {
    report->Modifier = modifiers;
    for (uint8_t key = 0; key < num_keys; ++key)
      report->KeyCode[key] = keys[key];
  }
  else
  {
    // TODO: Macro processing
#if 0
    const Macro * macro = g_kb_state.macro;
    MacroKey mkey;
    mkey.mod.all = pgm_read_byte(&macro->keys[g_kb_state.macro_key_index].mod);
    mkey.usage = pgm_read_word(&macro->keys[g_kb_state.macro_key_index].usage);
    uint8_t num_macro_keys = pgm_read_byte(&macro->num_keys);
    report->Modifier = g_kb_state.pre_macro_modifiers | mkey.mod.all;
    report->KeyCode[0] = USAGE_ID(mkey.usage);
    g_kb_state.macro_key_index++;
    if (g_kb_state.macro_key_index >= num_macro_keys)
    {
      g_kb_state.macro = NULL;
      g_kb_state.macro_key_index = 0;
    }
#endif
  }
  return sizeof(USB_KeyboardReport_Data_t);
}

bool
Keyboard::is_processing_macro()
{
  return false;
#if 0 // FIXME
  return g_kb_state.macro != NULL;
#endif
}

BoundKey*
Keyboard::first_active_key(void)
{
  curr_active_key = 0;
  BoundKey *key = &active_keys[curr_active_key];
  if (key && key->is_active()) return key;
  return Keyboard::next_active_key();
}

BoundKey*
Keyboard::next_active_key(void)
{
  BoundKey *key = NULL;
  while (!key && curr_active_key < num_active_keys)
  {
    key = &active_keys[++curr_active_key];
    if (!key->is_active())
      key = NULL;
  }
  return key;
}

static
Modifiers
get_modifier(Usage usage)
{
  switch(usage)
  {
  case HID_USAGE_LEFT_CONTROL:
    return L_CTL;
  case HID_USAGE_LEFT_SHIFT:
    return L_SHF;
  case HID_USAGE_LEFT_ALT:
    return L_ALT;
  case HID_USAGE_LEFT_GUI:
    return L_GUI;
  case HID_USAGE_RIGHT_CONTROL:
    return R_CTL;
  case HID_USAGE_RIGHT_SHIFT:
    return R_SHF;
  case HID_USAGE_RIGHT_ALT:
    return R_ALT;
  case HID_USAGE_RIGHT_GUI:
    return R_GUI;
  default:
    return NONE;
  }
}


#include <avr/pgmspace.h>
#include <stddef.h>
#include "bound_key.h"
#include "keyboard_class.h"

void
BoundKey::update_binding(uint8_t mods, KeyMap keymap)
{
  _binding = NULL;

  static KeyBindingArray bindings;
  memcpy_P((void*)&bindings, &keymap[_cell], sizeof(keymap[_cell]));
  if (bindings.length != 0)
  {
    // find and return the binding that matches the specified modifier state.
    for (int i = 0; i < bindings.length; ++i)
    {
      if (bindings.data[i].premods == mods)
      {
        _binding = &bindings.data[i];
        return;
      }
    }

    // TODO: fuzzier matching on modifer keys.

    // if no match was found, return the default binding
    // TODO: the code generator must ensure that the
    // following assumption is correct, the first
    // binding will be the one and only binding with
    // premods == NONE.
    if (bindings.data[0].premods == NONE)
    {
      _binding = &bindings.data[0];
      return;
    }
  }
}


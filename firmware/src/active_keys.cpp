#include <avr/pgmspace.h>
#include <stddef.h>
#include <limits.h>
#include <string.h>
#include "active_keys.h"

void
ActiveKeys::
reset()
{
  memset(&_keys[0], UCHAR_MAX, MAX_ACTIVE_CELLS * sizeof(_keys[0]));
  _num_keys = 0;
}

bool
ActiveKeys::
add_cell(Cell cell)
{
  if (_num_keys > MAX_ACTIVE_CELLS)
    return false;

  _keys[_num_keys++].set_cell(cell);

  return true;
}

BoundKey*
ActiveKeys::
first(void)
{
  _curr_key = 0;
  if (_keys[_curr_key].is_active())
    return &_keys[_curr_key];
  return next();
}

BoundKey*
ActiveKeys::
next(void)
{
  BoundKey *key = NULL;
  while (!key && _curr_key < _num_keys)
  {
    key = &_keys[++_curr_key];
    if (!key->is_active())
      key = NULL;
  }
  return key;
}


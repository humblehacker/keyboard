#ifndef __ACTIVE_KEYS_H__
#define __ACTIVE_KEYS_H__

#include "bound_key.h"

#define NUM_MODIFIERS 8
#define MAX_KEYS      6
#define MAX_ACTIVE_CELLS (MAX_KEYS + NUM_MODIFIERS)

class ActiveKeys
{
public:
  void       reset();
  bool       add_cell(Cell cell);

  BoundKey*  first();
  BoundKey*  next();

private:
  BoundKey  _keys[MAX_ACTIVE_CELLS];
  uint8_t   _num_keys;
  uint8_t   _curr_key;
};


#endif // __ACTIVE_KEYS_H__

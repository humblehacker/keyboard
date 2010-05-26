#include "registers.h"
#include "matrix_discovery_defs.h"

Registers registers[] =
{
#ifdef USE_PINA0
  { DDRA, PORTA, PINA, (1<<0), "A0" },
#endif
#ifdef USE_PINA1
  { DDRA, PORTA, PINA, (1<<1), "A1" },
#endif
#ifdef USE_PINA2
  { DDRA, PORTA, PINA, (1<<2), "A2" },
#endif
#ifdef USE_PINA3
  { DDRA, PORTA, PINA, (1<<3), "A3" },
#endif
#ifdef USE_PINA4
  { DDRA, PORTA, PINA, (1<<4), "A4" },
#endif
#ifdef USE_PINA5
  { DDRA, PORTA, PINA, (1<<5), "A5" },
#endif
#ifdef USE_PINA6
  { DDRA, PORTA, PINA, (1<<6), "A6" },
#endif
#ifdef USE_PINA7
  { DDRA, PORTA, PINA, (1<<7), "A7" },
#endif

#ifdef USE_PINB0
  { DDRB, PORTB, PINB, (1<<0), "B0" },
#endif
#ifdef USE_PINB1
  { DDRB, PORTB, PINB, (1<<1), "B1" },
#endif
#ifdef USE_PINB2
  { DDRB, PORTB, PINB, (1<<2), "B2" },
#endif
#ifdef USE_PINB3
  { DDRB, PORTB, PINB, (1<<3), "B3" },
#endif
#ifdef USE_PINB4
  { DDRB, PORTB, PINB, (1<<4), "B4" },
#endif
#ifdef USE_PINB5
  { DDRB, PORTB, PINB, (1<<5), "B5" },
#endif
#ifdef USE_PINB6
  { DDRB, PORTB, PINB, (1<<6), "B6" },
#endif
#ifdef USE_PINB7
  { DDRB, PORTB, PINB, (1<<7), "B7" },
#endif

#ifdef USE_PINC0
  { DDRC, PORTC, PINC, (1<<0), "C0" },
#endif
#ifdef USE_PINC1
  { DDRC, PORTC, PINC, (1<<1), "C1" },
#endif
#ifdef USE_PINC2
  { DDRC, PORTC, PINC, (1<<2), "C2" },
#endif
#ifdef USE_PINC3
  { DDRC, PORTC, PINC, (1<<3), "C3" },
#endif
#ifdef USE_PINC4
  { DDRC, PORTC, PINC, (1<<4), "C4" },
#endif
#ifdef USE_PINC5
  { DDRC, PORTC, PINC, (1<<5), "C5" },
#endif
#ifdef USE_PINC6
  { DDRC, PORTC, PINC, (1<<6), "C6" },
#endif
#ifdef USE_PINC7
  { DDRC, PORTC, PINC, (1<<7), "C7" },
#endif

#ifdef USE_PIND0
  { DDRD, PORTD, PIND, (1<<0), "D0" },
#endif
#ifdef USE_PIND1
  { DDRD, PORTD, PIND, (1<<1), "D1" },
#endif
#ifdef USE_PIND2
  { DDRD, PORTD, PIND, (1<<2), "D2" },
#endif
#ifdef USE_PIND3
  { DDRD, PORTD, PIND, (1<<3), "D3" },
#endif
#ifdef USE_PIND4
  { DDRD, PORTD, PIND, (1<<4), "D4" },
#endif
#ifdef USE_PIND5
  { DDRD, PORTD, PIND, (1<<5), "D5" },
#endif
#ifdef USE_PIND6
  { DDRD, PORTD, PIND, (1<<6), "D6" },
#endif
#ifdef USE_PIND7
  { DDRD, PORTD, PIND, (1<<7), "D7" },
#endif

#ifdef USE_PINE0
  { DDRE, PORTE, PINE, (1<<0), "E0" },
#endif
#ifdef USE_PINE1
  { DDRE, PORTE, PINE, (1<<1), "E1" },
#endif
#ifdef USE_PINE2
  { DDRE, PORTE, PINE, (1<<2), "E2" },
#endif
#ifdef USE_PINE3
  { DDRE, PORTE, PINE, (1<<3), "E3" },
#endif
#ifdef USE_PINE4
  { DDRE, PORTE, PINE, (1<<4), "E4" },
#endif
#ifdef USE_PINE5
  { DDRE, PORTE, PINE, (1<<5), "E5" },
#endif
#ifdef USE_PINE6
  { DDRE, PORTE, PINE, (1<<6), "E6" },
#endif
#ifdef USE_PINE7
  { DDRE, PORTE, PINE, (1<<7), "E7" },
#endif

#ifdef USE_PINF0
  { DDRF, PORTF, PINF, (1<<0), "F0" },
#endif
#ifdef USE_PINF1
  { DDRF, PORTF, PINF, (1<<1), "F1" },
#endif
#ifdef USE_PINF2
  { DDRF, PORTF, PINF, (1<<2), "F2" },
#endif
#ifdef USE_PINF3
  { DDRF, PORTF, PINF, (1<<3), "F3" },
#endif
#ifdef USE_PINF4
  { DDRF, PORTF, PINF, (1<<4), "F4" },
#endif
#ifdef USE_PINF5
  { DDRF, PORTF, PINF, (1<<5), "F5" },
#endif
#ifdef USE_PINF6
  { DDRF, PORTF, PINF, (1<<6), "F6" },
#endif
#ifdef USE_PINF7
  { DDRF, PORTF, PINF, (1<<7), "F7" },
#endif
};

uint8_t registers_length = sizeof(registers)/sizeof(Registers);

#!/usr/bin/env gawk -f
BEGIN {
   i = 0
}

/^Traceback/ {
   tb = 1
}

tb == 1 && /^  File/ {
   push($0)
}

tb == 1 && /^[a-zA-Z]+Error\:/ {
   lasterr = pop()
   match(lasterr, /\"([^\"]+)\", line ([0-9]+)/, matches)
   print matches[1] ":" matches[2] ": " $0
   tb = 0
   next
}

{
   print
}

function push(val) {
   stack[++i] = val
}

function pop() {
   val = stack[i--]
   return val
}

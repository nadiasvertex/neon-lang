neon
======

neon is an experimental language being implemented in RPython. Its Intent is to explore
the Interface between a functional language like Haskell with compositional elements like 
Go in a dynamic environment like Python.

Having spent some time with functional languages, it appears obvious that some procedural
code is necessary and desirable. A significant part of the experiment involves exploring
how the functional and procedural elements can be combined in an elegant way. Rust and
Scala seem to have done this quite well.

It is unclear whether pure immutability is desirable, so it is hard to say whether neon
will allow mutation. On the one hand, immutability makes strong type inference simpler.
On the other, it makes doing certain things efficiently quite hard.

All functions are generic be default. A new function is generated each time a call is made
with a different type. 

Provisional Syntax
===================

Functions
---------

```
# Function definition
do_something param1 param2 = some_other_func (func_3 param1) (func_4 param2)

# Function definition with type annotation
do_something2 :: Int String = String
do_something2    p1  p2     = do_something p1 p2

# Function definition with where clause
do_something3 p1 p2 = do_something a b 
   where
      a = do_something2 (some_expression p1) (some_expression p2) 
      b = do_something2 (some_expression p2) (some_expression p1)

procedural_do_something p1 p2:
   prInt "some stuff to the screen"
   prInt "more stuff"
   
   a = do_something3 p1 p2
   b = do_something3 p2 p1
   
   return a + b
```

Algebraic Data Types
--------------------

These are intelligent union types. 

```
# Simple type
type SomeType:
   I Int
   S String

# Construct with:
v = I 1
v = S "one"

# Deconstruct with:
I i = v
S s = v

# Compound type
type Expr:
   I   Int
   B   Bool
   Add Expr Expr 
   Mul Expr Expr 
   Eq  Expr Expr 

# Construct with:
v = I 5
v = B True
v = Add (I 5) (I 10)

# Deconstruct with:
I i = v
B b = v
Add l r = v
Mul l r = v
Eq  l r = v
```

Pattern Matching
-----------------

```

# Using the expr type above

eval :: Expr   = Expr
eval (I n)     = n
eval (Add l r) = (eval l) + (eval r)
eval (Mul l r) = (eval l) * (eval r)

# Works for procedural functions too

print :: Expr
print (I n):
   io.put (str n)

print (Add l r):
   print l
   io.put " + "
   print r


print (Mul l r):
   print l
   io.put " * "
   print r
```

Structs
------------

Compact data storage with named values.

```
struct SomeData:
   i Int
   b Bool
   s String
   
# Anonymous construction
v = SomeData 5 True "test"

# Anonymous deconstruction
(SomeData v1 v2 v3) = v

# Named construction
v = SomeData s="test2" i=10 b=False 

# Named deconstruction
(SomeData v1=b v2=s) = v

# Member access
v1 = v.i
v2 = v.b
v3 = v.s

```

Interfaces
-------------

Pure specifications of behavior.

```

interface Writer:
   write Bytes = Int

interface Reader:
   read Int = Bytes

interface ReaderWriter:
   Reader
   Writer

```

Methods
--------

```
write :: SomeStream Bytes = Int
write s b = s.io.put b 

# Create a new instance of SomeStream
st = new_stream

# Call the write method
st.write some_data

```

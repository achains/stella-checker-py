language core;
extend with #tuples;

fn foo(x : Nat) -> {Nat, Bool, Nat} {
  return {0, true, 0}
}

fn main(n : Nat) -> {Nat, Nat} {
  return foo(n).3 // 4 > 3
}
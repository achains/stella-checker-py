// true line 6 -- UNEXPECTED_TYPE
language core;
extend with #pairs;

fn main(n : Nat) -> {Nat, Nat} {
  return {succ(n), {succ(succ(n)), true}}.2
}
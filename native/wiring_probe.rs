//! Thin stdin adapter to the existing graph checker and register evaluator.
extern crate imasm_core;
use imasm_core::{check::{Graph, ClosureState}, classic::Token,
                 flow::flow_values, imasm16_3::Reg16_3};
use std::io::{self, Read};

fn mask(v: Reg16_3) -> u8 {
    v.big_t as u8 | (v.big_f as u8) << 1 |
        (v.small_t as u8) << 2 | (v.small_f as u8) << 3
}
fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut lines = input.lines();
    let seed: u8 = lines.next().unwrap().parse().unwrap();
    assert!(seed < 16);
    let nodes = lines.next().unwrap().split_whitespace()
        .map(|s| Token::parse(s).expect("unknown opcode")).collect();
    let edges = lines.map(|line| {
        let mut fields = line.split_whitespace();
        let a: usize = fields.next().unwrap().parse().unwrap();
        let b: usize = fields.next().unwrap().parse().unwrap();
        assert!(fields.next().is_none());
        (a, b)
    }).collect();
    let g = Graph { nodes, edges };
    assert!(g.edges.iter().all(|&(a,b)| a < g.nodes.len() && b < g.nodes.len()));
    let errors = g.validate();
    assert!(errors.is_empty(), "invalid graph: {:?}", errors);
    let (pairs, fully) = g.frobenius_closures();
    let state = g.closure_state();
    let (closure, closed) = match state {
        ClosureState::Closed(_) => ("closed", true),
        ClosureState::Identity => ("identity", false),
        ClosureState::Open => ("open", false),
        ClosureState::None => ("none", false),
    };
    let v = Reg16_3 { big_t: seed & 1 != 0, big_f: seed & 2 != 0,
                     small_t: seed & 4 != 0, small_f: seed & 8 != 0 };
    let (node_in, edges) = flow_values(&g, v);
    let pairs: Vec<[usize;2]> = pairs.iter().map(|&(a,b)| [a,b]).collect();
    let recoveries: Vec<bool> = pairs.iter().map(|p| node_in[p[0]] == node_in[p[1]]).collect();
    println!("{{\"closure\":\"{}\",\"closure_verified\":{},\"fully_reconnected\":{},\"pairs\":{:?},\"node_inputs\":{:?},\"edge_values\":{:?},\"pair_recovers_input\":{:?}}}",
        closure, closed, fully, pairs,
        node_in.into_iter().map(mask).collect::<Vec<_>>(),
        edges.into_iter().map(mask).collect::<Vec<_>>(), recoveries);
}

import networkx as nx

from cirbo.core import Circuit
from cirbo.core.circuit import gate


_gate_type_to_name: dict[gate.GateType, str] = {
        getattr(gate, gt_name): gt_name
        for gt_name in [
            'INPUT',
            'ALWAYS_FALSE',
            'ALWAYS_TRUE',
            'AND',
            'GEQ',
            'GT',
            'IFF',
            'LEQ',
            'LIFF',
            'LNOT',
            'LT',
            'NAND',
            'NOR',
            'NOT',
            'NXOR',
            'OR',
            'RIFF',
            'RNOT',
            'XOR'
        ]
    }


def cirbo2nx(
    circuit: Circuit,
) -> nx.DiGraph:

    graph: nx.DiGraph = nx.DiGraph()

    def _create_node(_gate_label, cur_gate):
        graph.add_node(
            _gate_label,
            node_id=cur_gate.label,
            node_type=_gate_type_to_name[cur_gate.gate_type],
        )

    def _find_operand(operand: gate.Label) -> gate.Label:
        _gate = circuit.get_gate(operand)
        if _gate.gate_type in [gate.IFF, gate.LIFF]:
            return _find_operand(_gate.operands[0])
        elif _gate.gate_type == gate.RIFF:
            return _find_operand(_gate.operands[1])
        return _gate.label

    # Add all circuit nodes to networkx digraph.
    for _, (gate_label, cur_gate) in enumerate(circuit._gates.items()):

        if cur_gate.gate_type in [gate.IFF, gate.LIFF, gate.RIFF]:
            continue

        _create_node(gate_label, cur_gate)

        if cur_gate.gate_type in [gate.GT, gate.GEQ, gate.LT, gate.LEQ]:
            for _, operand in enumerate(cur_gate.operands):
                graph.add_edge(
                    _find_operand(operand),
                    gate_label,
                )
        elif cur_gate.gate_type == gate.LNOT:
            graph.add_edge(
                _find_operand(cur_gate.operands[0]),
                gate_label,
            )
        elif cur_gate.gate_type == gate.RNOT:
            graph.add_edge(
                _find_operand(cur_gate.operands[1]),
                gate_label,
            )
        else:
            for operand in cur_gate.operands:
                graph.add_edge(
                    _find_operand(operand),
                    gate_label,
                )

    # Redraw inputs with different shape.
    for _input in circuit._inputs:
        if _input not in graph:
            graph.add_node(_input)

    # Redraw outputs with different shape.
    for _, _output in enumerate(circuit._outputs):
        node = _find_operand(_output)
        if node not in graph:
            graph.add_node(node)
        graph.add_node(
            f'!OUT_{node}',
            node_id=f'!OUT_{node}',
            node_type='OUTPUT'
        )
        graph.add_edge(
            node,
            f'!OUT_{node}'
        )
    return graph


def nx2cirbo(
    graph: nx.DiGraph,
) -> Circuit:
    circuit = Circuit()
    outputs = []

    for _, layer in enumerate(nx.topological_generations(graph)):
        for node in layer:
            data = graph.nodes[node]
            if data.get('node_type') == 'INPUT':
                circuit.add_gate(gate.Gate(node, gate.INPUT))
            elif data.get('node_type') == 'OUTPUT':
                outputs.append(node)
            else:
                circuit.add_gate(
                    gate.Gate(
                        node,
                        getattr(gate, data.get('node_type')),
                        tuple(graph.predecessors(node))
                    )
                )

    for mock_out in sorted(outputs):
        out = list(graph.predecessors(mock_out))[0]
        circuit.mark_as_output(out)

    return circuit

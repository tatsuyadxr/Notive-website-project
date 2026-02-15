"""qiskitquantum.py — small collection of Qiskit-friendly quantum math utilities.

Functions provided:
- pauli_matrices()
- pauli_string_to_matrix(s)
- inner_product(psi, phi)
- state_fidelity(psi, phi)
- expectation_value(operator, state)
- bloch_vector(state)
- qft_matrix(n) and apply_qft(state)

All functions accept plain NumPy statevectors (preferred) and will also accept
Qiskit Statevector/DensityMatrix objects when Qiskit is available.

Usage examples are in the __main__ block.
"""
from typing import Union, Sequence
import numpy as np
import sys

# Optional Qiskit imports (used only if available)
try:
    from qiskit.quantum_info import Statevector, DensityMatrix, state_fidelity as _qstate_fidelity
    HAS_QISKIT = True
except Exception:
    HAS_QISKIT = False

StateLike = Union[Sequence[complex], np.ndarray]


def pauli_matrices() -> dict:
    """Return single-qubit Pauli matrices as NumPy arrays."""
    return {
        "I": np.array([[1, 0], [0, 1]], dtype=complex),
        "X": np.array([[0, 1], [1, 0]], dtype=complex),
        "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    }


def _to_numpy_state(state: StateLike) -> np.ndarray:
    """Convert input to a 1-D NumPy statevector (pure-state only).

    Accepts: raw sequence/ndarray or Qiskit Statevector/DensityMatrix (if qiskit
    is installed). Raises ValueError for unsupported inputs or mixed states.
    """
    if HAS_QISKIT and isinstance(state, Statevector):
        return np.asarray(state.data, dtype=complex)
    if HAS_QISKIT and isinstance(state, DensityMatrix):
        # try to extract a pure statevector from the density matrix
        rho = np.asarray(state.data, dtype=complex)
        # check purity (Tr(rho^2) == 1 for pure)
        purity = np.real_if_close(np.trace(rho @ rho))
        if not np.isclose(purity, 1.0):
            raise ValueError("DensityMatrix is mixed; this utility expects pure states")
        # extract the eigenvector with eigenvalue ~1
        eigvals, eigvecs = np.linalg.eigh(rho)
        idx = np.argmax(eigvals)
        vec = eigvecs[:, idx]
        # ensure global phase/normalization is standard
        return vec / np.linalg.norm(vec)

    arr = np.asarray(state, dtype=complex)
    if arr.ndim != 1:
        # allow column vectors
        if arr.ndim == 2 and 1 in arr.shape:
            arr = arr.reshape(-1)
        else:
            raise ValueError("State must be a 1-D statevector (or qiskit Statevector)")
    norm = np.linalg.norm(arr)
    if norm == 0:
        raise ValueError("Zero vector is not a valid quantum state")
    return arr / norm


def inner_product(psi: StateLike, phi: StateLike) -> complex:
    """Return the inner product <psi|phi> (psi, phi may be arrays or Qiskit objects)."""
    a = _to_numpy_state(psi)
    b = _to_numpy_state(phi)
    return np.vdot(a, b)


def state_fidelity(psi: StateLike, phi: StateLike) -> float:
    """Return fidelity between two pure states.

    For pure states fidelity = |<psi|phi>|^2. If Qiskit is installed and either
    argument is a Qiskit object, Qiskit's `state_fidelity` will be used.
    """
    if HAS_QISKIT and (isinstance(psi, (Statevector,)) or isinstance(phi, (Statevector,))):
        try:
            return float(_qstate_fidelity(psi, phi))
        except Exception:
            pass
    overlap = inner_product(psi, phi)
    return float(np.abs(overlap) ** 2)


def expectation_value(operator: Union[np.ndarray, str], state: StateLike) -> complex:
    """Compute expectation value <state|operator|state>.

    `operator` may be a NumPy matrix matching the state dimension, or a
    Pauli string like 'X', 'ZI', 'IXY' (left-most character acts on most
    significant qubit).
    """
    psi = _to_numpy_state(state)
    dim = psi.shape[0]

    if isinstance(operator, str):
        op = pauli_string_to_matrix(operator)
    else:
        op = np.asarray(operator, dtype=complex)

    if op.shape != (dim, dim):
        raise ValueError(f"Operator shape {op.shape} does not match state dimension {dim}")

    return float(np.vdot(psi, op @ psi))


def pauli_string_to_matrix(s: str) -> np.ndarray:
    """Convert a Pauli string (e.g. 'X', 'ZI', 'IX') to a NumPy matrix.

    The left-most character corresponds to the most-significant qubit.
    """
    paulis = pauli_matrices()
    if not s:
        return paulis['I']
    mats = []
    for ch in s:
        if ch.upper() not in paulis:
            raise ValueError(f"Invalid Pauli character: {ch}")
        mats.append(paulis[ch.upper()])
    # Tensor product: left-most is most significant -> kron chain in order
    full = mats[0]
    for m in mats[1:]:
        full = np.kron(full, m)
    return full


def bloch_vector(state: StateLike) -> np.ndarray:
    """Return the Bloch vector (x, y, z) for a single-qubit pure statevector.

    Raises ValueError if the state is not single-qubit.
    """
    psi = _to_numpy_state(state)
    if psi.size != 2:
        raise ValueError("bloch_vector expects a single-qubit state (dimension=2)")
    paulis = pauli_matrices()
    return np.array([
        np.real(np.vdot(psi, paulis['X'] @ psi)),
        np.real(np.vdot(psi, paulis['Y'] @ psi)),
        np.real(np.vdot(psi, paulis['Z'] @ psi)),
    ])


def qft_matrix(n: int) -> np.ndarray:
    """Return the 2^n x 2^n Quantum Fourier Transform matrix."""
    if n < 1:
        raise ValueError("n must be >= 1")
    N = 2 ** n
    omega = np.exp(2j * np.pi / N)
    j = np.arange(N).reshape((N, 1))
    k = np.arange(N).reshape((1, N))
    mat = omega ** (j * k) / np.sqrt(N)
    return mat.astype(complex)


def apply_qft(state: StateLike) -> np.ndarray:
    """Apply QFT to a statevector and return the transformed statevector."""
    psi = _to_numpy_state(state)
    dim = psi.size
    n = int(np.log2(dim))
    if 2 ** n != dim:
        raise ValueError("Statevector length must be a power of two")
    return qft_matrix(n) @ psi


__all__ = [
    "pauli_matrices",
    "pauli_string_to_matrix",
    "inner_product",
    "state_fidelity",
    "expectation_value",
    "bloch_vector",
    "qft_matrix",
    "apply_qft",
]


def _parse_state_arg(s: str) -> np.ndarray:
    """Parse a state argument passed on the CLI or from the web.

    Accepts predefined names: '0','1','+','-' or a comma-separated list of
    numeric/amplitude tokens. Returns a normalized NumPy statevector.
    """
    s = (s or "").strip()
    if s in ("0", "|0>"):
        return _to_numpy_state([1, 0])
    if s in ("1", "|1>"):
        return _to_numpy_state([0, 1])
    if s == "+":
        return _to_numpy_state([1, 1])
    if s == "-":
        return _to_numpy_state([1, -1])
    if s == "":
        raise ValueError("Empty state provided")
    # parse comma-separated amplitudes
    parts = [p.strip() for p in s.split(',') if p.strip()]
    vals = []
    for p in parts:
        try:
            vals.append(complex(p))
        except Exception:
            # try simple real parse
            vals.append(float(p))
    return _to_numpy_state(np.array(vals, dtype=complex))


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="qiskitquantum CLI — run math ops from command line")
    parser.add_argument("--cmd", choices=["fidelity", "bloch", "expectation", "inner", "qft"], help="operation to run")
    parser.add_argument("--state", help="state (predefined like 0,1,+,- or comma-separated amplitudes)")
    parser.add_argument("--state1", help="first state for two-state operations")
    parser.add_argument("--state2", help="second state for two-state operations")
    parser.add_argument("--pauli", help="Pauli string for expectation (e.g. ZI)")
    parser.add_argument("--nqubits", type=int, help="number of qubits for QFT")
    parser.add_argument("--out-file", help="optional file to write JSON result")
    parser.add_argument("name", nargs="?", help="(optional) context name")
    parser.add_argument("age", nargs="?", help="(optional) context age")
    parser.add_argument("country", nargs="?", help="(optional) context country")

    args = parser.parse_args()

    if not args.cmd:
        # no cmd -> run demo (original behaviour)
        print("Qiskit math utilities demo — running simple examples:\n")
        zero = np.array([1.0, 0.0], dtype=complex)
        plus = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2)
        print("|0> fidelity with |+>", state_fidelity(zero, plus))
        print("Inner product <0|+>", inner_product(zero, plus))
        print("Bloch vector of |+>", bloch_vector(plus))
        print("Expectation Z on |0>", expectation_value('Z', zero))
        psi01 = np.zeros(4, dtype=complex); psi01[1] = 1.0
        print("\nQFT (2 qubits) applied to |01> -> amplitudes:")
        print(np.round(apply_qft(psi01), 6))
        op = pauli_string_to_matrix('ZI')
        print("\nOperator ZI matrix:\n", op)
        if HAS_QISKIT:
            print("\nQiskit is available — convert example to Statevector")
            sv = Statevector(plus)
            print("Qiskit Statevector fidelity (plus, plus):", state_fidelity(sv, sv))
        else:
            print("\nQiskit not installed — functions work with NumPy statevectors.")
        sys.exit(0)

    result = {"operation": args.cmd}
    try:
        if args.cmd == 'fidelity':
            if not args.state1 or not args.state2:
                raise ValueError('fidelity requires --state1 and --state2')
            psi = _parse_state_arg(args.state1)
            phi = _parse_state_arg(args.state2)
            val = state_fidelity(psi, phi)
            result['value'] = float(val)

        elif args.cmd == 'inner':
            if not args.state1 or not args.state2:
                raise ValueError('inner requires --state1 and --state2')
            psi = _parse_state_arg(args.state1)
            phi = _parse_state_arg(args.state2)
            val = inner_product(psi, phi)
            result['value'] = {'real': float(np.real(val)), 'imag': float(np.imag(val))}

        elif args.cmd == 'bloch':
            if not args.state:
                raise ValueError('bloch requires --state')
            psi = _parse_state_arg(args.state)
            vec = bloch_vector(psi)
            result['value'] = vec.tolist()

        elif args.cmd == 'expectation':
            if not args.state or not args.pauli:
                raise ValueError('expectation requires --state and --pauli')
            psi = _parse_state_arg(args.state)
            val = expectation_value(args.pauli, psi)
            result['value'] = float(val)

        elif args.cmd == 'qft':
            n = args.nqubits or int(np.log2(len(_parse_state_arg(args.state)))) if args.state else None
            if n is None:
                raise ValueError('qft requires --nqubits or a --state of power-of-two length')
            if args.state:
                psi = _parse_state_arg(args.state)
            else:
                psi = np.zeros(2**n, dtype=complex); psi[0] = 1.0
            out = apply_qft(psi)
            result['value'] = [complex(x) for x in out]

        # attach optional context
        result['context'] = {'name': args.name, 'age': args.age, 'country': args.country}
        out_text = json.dumps(result, default=lambda o: (o.real, o.imag) if isinstance(o, complex) else str(o))
        if args.out_file:
            with open(args.out_file, 'w', encoding='utf-8') as f:
                f.write(out_text)
        else:
            print(out_text)
    except Exception as exc:
        err = {"error": str(exc)}
        if args.out_file:
            with open(args.out_file, 'w', encoding='utf-8') as f:
                f.write(json.dumps(err))
        else:
            print(json.dumps(err))
        sys.exit(2)

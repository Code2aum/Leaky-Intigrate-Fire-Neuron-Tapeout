<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

The project implements a **Leaky Integrate-and-Fire (LIF)** neuron model, which is a fundamental building block in computational neuroscience and neuromorphic engineering.

- **Leakage (Decay)**: On every clock cycle, the current membrane potential (`state`) is shifted right by 1 bit (`state >> 1`), simulating a 50% decay (leak).
- **Integration**: The incoming 8-bit input current (`ui_in`) is added to the decayed membrane potential to calculate the `next_state`.
- **Threshold & Spiking**: The `next_state` is compared to a fixed threshold of **200**.
  - If `next_state >= 200`, the `spike` output is pulled high.
  - The current implementation tracks the membrane potential but does not automatically reset it to zero after a spike (non-resetting integrator behavior).
- **Outputs**:
  - `uo_out`: The 8-bit membrane potential.
  - `uio_out[7]`: The spike signal.

## How to test

1. **Reset**: Pulse the `rst_n` pin low to initialize the membrane potential to 0.
2. **Input Current**: Provide an 8-bit value to `ui_in`. 
   - A small value (e.g., 20) will cause the potential to settle at a low value (40) due to leakage.
   - A high value (e.g., >100) will cause the potential to rise toward the threshold.
3. **Observe Potential**: Monitor `uo_out` to see the membrane potential integrating and leaking.
4. **Observe Spikes**: Check `uio_out[7]` for a high signal when the potential exceeds 200.

## External hardware

None required. The project can be tested using standard digital I/O or a logic analyzer.

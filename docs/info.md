<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

The project implements a **Leaky Integrate-and-Fire (LIF)** neuron model in synthesizable Verilog.

- **Leakage (Decay)**: On every clock cycle, the current membrane potential (`state`) is shifted right by 1 bit (`state >> 1`), simulating a 50% exponential decay.
- **Integration**: The incoming 8-bit input current (`ui_in`) is added to the decayed membrane potential to produce `next_state`.
- **Threshold & Spiking**: The `next_state` is compared to a fixed threshold of **200**. If `next_state >= 200`, the `spike` output (`uio_out[7]`) is driven high.
- **Spike Reset**: When a spike fires, the membrane potential resets to **0** on the next clock edge, enabling rhythmic firing under sustained input.
- **Outputs**:
  - `uo_out[7:0]`: The 8-bit membrane potential.
  - `uio_out[7]`: The spike signal (high for one cycle per spike event).

## How to test

1. **Reset**: Hold `rst_n` low for several clock cycles to initialize the membrane potential to 0.
2. **Apply Current**: Drive an 8-bit value on `ui_in`.
   - A small value (e.g., 20) will cause the membrane to settle around 40 (leak balances input) — no spike.
   - A large value (e.g., 150) will cause the membrane to cross the threshold and spike every 2 cycles.
3. **Observe Potential**: Monitor `uo_out[7:0]` to see the membrane potential integrating and decaying.
4. **Observe Spikes**: Check `uio_out[7]` for a one-cycle pulse when the potential crosses 200.

## External hardware

None required. The project can be tested using standard digital I/O or a logic analyzer.

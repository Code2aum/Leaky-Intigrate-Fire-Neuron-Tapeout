# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # 10 us clock period (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # -------------------------------------------------------
    # Reset – drive signals, hold rst_n low for 10 cycles
    # -------------------------------------------------------
    dut._log.info("Reset")
    dut.ena.value    = 1
    dut.ui_in.value  = 0
    dut.uio_in.value = 0
    dut.rst_n.value  = 0
    await ClockCycles(dut.clk, 10)

    # Release reset and set first input (Active phase – safe to drive)
    dut.rst_n.value = 1
    dut.ui_in.value = 20

    # -------------------------------------------------------
    # Sampling strategy (works for both RTL and gate-level):
    #   RisingEdge  → NBA commits + gate delays start propagating
    #   FallingEdge → 5 µs later, all gate delays have settled
    #
    # Drive inputs right after RisingEdge (Active phase).
    # Read outputs at FallingEdge (mid-cycle, fully settled).
    # -------------------------------------------------------

    # -------------------------------------------------------
    # Test 1: state=0, current=20
    #   next = (0>>1) + 20 = 20  →  state = 20
    # -------------------------------------------------------
    dut._log.info("Test 1: state=0, current=20 -> state=20")
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)   # settle
    val = int(dut.uo_out.value)
    assert val == 20, f"T1: Expected 20, got {val}"
    spike = int(dut.uio_out.value)
    assert spike == 0, f"T1: No spike expected, got {spike}"

    # -------------------------------------------------------
    # Test 2: state=20, current=20
    #   next = (20>>1) + 20 = 30  →  state = 30
    # -------------------------------------------------------
    dut._log.info("Test 2: state=20, current=20 -> state=30")
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    val = int(dut.uo_out.value)
    assert val == 30, f"T2: Expected 30, got {val}"

    # -------------------------------------------------------
    # Test 3: high current (150) → spike should fire
    # -------------------------------------------------------
    dut._log.info("Test 3: High current, expect spike within 10 cycles")
    await RisingEdge(dut.clk)    # Active – safe to drive
    dut.ui_in.value = 150

    spiked = False
    for i in range(10):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)
        spike_bit = (int(dut.uio_out.value) >> 7) & 1
        if spike_bit:
            dut._log.info(f"Spike at iteration {i+1}, state={int(dut.uo_out.value)}")
            spiked = True
            break
    assert spiked, "T3: Expected spike with current=150 but none fired within 10 cycles"

    # -------------------------------------------------------
    # Test 4: after spike, membrane resets to 0
    # -------------------------------------------------------
    dut._log.info("Test 4: Post-spike membrane reset")
    await RisingEdge(dut.clk)    # Active
    dut.ui_in.value = 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    val = int(dut.uo_out.value)
    assert val == 0, f"T4: Expected 0 after spike reset, got {val}"

    dut._log.info("All tests passed!")

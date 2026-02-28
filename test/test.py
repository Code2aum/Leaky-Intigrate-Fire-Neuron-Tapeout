# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, ReadOnly, RisingEdge


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # 10 us clock period (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # -------------------------------------------------------
    # Reset – hold rst_n low for 10 cycles
    # After ClockCycles(), we are in the ACTIVE phase → safe to drive signals
    # -------------------------------------------------------
    dut._log.info("Reset")
    dut.ena.value    = 1
    dut.ui_in.value  = 0
    dut.uio_in.value = 0
    dut.rst_n.value  = 0
    await ClockCycles(dut.clk, 10)   # Active phase – can still drive

    # Release reset and set first input while still in Active phase
    dut.rst_n.value = 1
    dut.ui_in.value = 20

    # -------------------------------------------------------
    # Test 1: state=0, current=20
    #   next = (0>>1) + 20 = 20  →  state = 20 after 1 clock
    # Pattern: RisingEdge (schedules NBA) → ReadOnly (NBA committed, safe to read)
    # -------------------------------------------------------
    dut._log.info("Test 1: state=0, current=20 → state=20")
    await RisingEdge(dut.clk)   # clock 1 cycle; NBA not yet committed
    await ReadOnly()             # now NBA IS committed: state = 20
    assert int(dut.uo_out.value)  == 20, f"T1: Expected 20, got {dut.uo_out.value}"
    assert int(dut.uio_out.value) ==  0, "T1: No spike expected"

    # -------------------------------------------------------
    # Test 2: state=20, current=20
    #   next = (20>>1) + 20 = 30  →  state = 30
    # From ReadOnly, RisingEdge advances to the next clock's Active phase.
    # -------------------------------------------------------
    dut._log.info("Test 2: state=20, current=20 → state=30")
    await RisingEdge(dut.clk)   # T+2 Active (ui_in still 20)
    await ReadOnly()             # state = 30
    assert int(dut.uo_out.value) == 30, f"T2: Expected 30, got {dut.uo_out.value}"

    # -------------------------------------------------------
    # Test 3: drive high current → spike fires
    # Must move to Active before driving a new input value.
    # -------------------------------------------------------
    dut._log.info("Test 3: High current, expect spike within 10 cycles")
    await RisingEdge(dut.clk)   # Get back to Active phase so we can drive
    dut.ui_in.value = 150       # drive in Active – safe

    spiked = False
    for i in range(10):
        await RisingEdge(dut.clk)
        await ReadOnly()
        spike_bit = (int(dut.uio_out.value) >> 7) & 1
        if spike_bit:
            dut._log.info(f"Spike at iteration {i+1}, state_before_reset={int(dut.uo_out.value)}")
            spiked = True
            break
    assert spiked, "T3: Expected a spike with current=150 but none fired within 10 cycles"

    # -------------------------------------------------------
    # Test 4: one cycle after spike, membrane resets to 0
    # -------------------------------------------------------
    dut._log.info("Test 4: Post-spike membrane reset")
    await RisingEdge(dut.clk)   # Active phase – spike NBA has now committed state=0
    dut.ui_in.value = 0         # remove input current
    await RisingEdge(dut.clk)   # clock once with current=0
    await ReadOnly()             # state = (0>>1)+0 = 0 → state = 0
    assert int(dut.uo_out.value) == 0, f"T4: Expected 0, got {dut.uo_out.value}"

    dut._log.info("All tests passed!")
